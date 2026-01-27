import yt_dlp
from .schemas import VideoInfo, VideoFormat, SubtitleInfo
from .core.config import settings
from .core.log_manager import log_manager
from typing import List, Dict, Any
import os
import asyncio

class YtDlpLogger:
    def __init__(self, loop):
        self.loop = loop

    def debug(self, msg):
        # Ignoramos mensajes de debug muy verbosos, pero dejamos los útiles
        if msg.startswith('[debug] '): return
        self._send(msg)

    def info(self, msg):
        self._send(msg)

    def warning(self, msg):
        self._send(f"WARNING: {msg}")

    def error(self, msg):
        self._send(f"ERROR: {msg}")

    def _send(self, msg):
        if self.loop and not self.loop.is_closed():
            # Broadcast asíncrono desde hilo síncrono
            asyncio.run_coroutine_threadsafe(log_manager.broadcast(msg), self.loop)

class YtDlpService:
    """
    Servicio encargado de interactuar con la librería yt-dlp.
    Encapsula la complejidad de la configuración y extracción de datos.
    """
    
    def __init__(self):
        self.common_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }

    def get_video_info(self, url: str) -> VideoInfo:
        """
        Extrae metadatos extendidos: formatos con codecs, subtítulos, etc.
        """
        opts = {**self.common_opts, 'listsubs': True}
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            
            # Procesar y separar formatos
            v_formats, a_formats = self._process_formats(info_dict.get('formats', []))
            processed_subs = self._process_subtitles(info_dict)
            
            return VideoInfo(
                id=info_dict.get('id'),
                url=info_dict.get('webpage_url', url),
                title=info_dict.get('title'),
                thumbnail=info_dict.get('thumbnail'),
                duration=info_dict.get('duration', 0),
                uploader=info_dict.get('uploader', 'Unknown'),
                video_formats=v_formats,
                audio_formats=a_formats,
                subtitles=processed_subs
            )

    def download_video_background(self, url: str, format_id: str, subtitles: List[str] = None, options: Dict[str, Any] = None, loop=None):
        """
        Método sincrónico para ser ejecutado en BackgroundTasks.
        Realiza la descarga real. format_id puede ser un ID simple o una combinación 'video+audio'.
        """
        if options is None: options = {}
        print(f"Iniciando descarga de {url} formato {format_id} con subs: {subtitles} y opciones: {options}...")

        # Callback para progreso
        def progress_hook(d):
            if d['status'] == 'downloading':
                # Construimos un mensaje de progreso
                try:
                    p = d.get('_percent_str', '0%').replace('%','')
                    speed = d.get('_speed_str', 'N/A')
                    eta = d.get('_eta_str', 'N/A')
                    msg = f"[download] {p}% of {d.get('_total_bytes_str') or d.get('_total_bytes_estimate_str')} at {speed} ETA {eta}"
                    # Enviamos
                    if loop and not loop.is_closed():
                        asyncio.run_coroutine_threadsafe(log_manager.broadcast(msg), loop)
                except Exception:
                    pass
            elif d['status'] == 'finished':
                if loop and not loop.is_closed():
                    asyncio.run_coroutine_threadsafe(log_manager.broadcast(f"[finished] Download completed: {d.get('filename')}"), loop)
        
        # Configuración de Post-Procesadores
        postprocessors = []

        # 1. Metadatos (Título, Autor, Descripción...)
        if options.get('embed_metadata', False):
            postprocessors.append({
                'key': 'FFmpegMetadata',
                'add_chapters': options.get('embed_chapters', False),
                'add_metadata': True,
            })

        # 2. Miniatura (Cover Art)
        if options.get('embed_thumbnail', False):
            postprocessors.append({'key': 'EmbedThumbnail'})

        # 3. Subtítulos (Si se incrustan)
        if options.get('embed_subs', False):
            # FFmpegEmbedSubtitle asegura que se incrusten
            postprocessors.append({'key': 'FFmpegEmbedSubtitle'})

        ydl_opts = {
            'format': format_id, 
            'outtmpl': os.path.join(settings.DOWNLOAD_DIR, '%(title)s [%(id)s].%(ext)s'),
            'quiet': False,
            'merge_output_format': 'mkv',
            
            # Subtítulos Config
            'writesubtitles': options.get('embed_subs', False) or bool(subtitles), 
            'subtitleslangs': subtitles if subtitles else [],
            # embedsubtitles=True también activa el postprocesador interno, pero lo dejamos explícito arriba o aquí
            # Lo dejamos aquí por compatibilidad
            'embedsubtitles': options.get('embed_subs', False),
            'subtitlesformat': options.get('sub_format', 'best'), # 'best' permite conversión automática si es necesario
            
            # Metadatos / Thumbnail Config
            'writethumbnail': options.get('embed_thumbnail', False), # Necesario para bajarla antes de incrustar
            
            # Lista de procesadores
            'postprocessors': postprocessors,
            
            'logger': YtDlpLogger(loop) if loop else None,
            'progress_hooks': [progress_hook] if loop else [],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print(f"Descarga completada: {url}")
            if loop and not loop.is_closed():
                asyncio.run_coroutine_threadsafe(log_manager.broadcast(f"SUCCESS: Descarga completada para {url}"), loop)

        except Exception as e:
            print(f"Error descargando {url}: {e}")
            if loop and not loop.is_closed():
                asyncio.run_coroutine_threadsafe(log_manager.broadcast(f"ERROR: {str(e)}"), loop)

    def _process_formats(self, raw_formats: List[Dict[str, Any]]) -> tuple[List[VideoFormat], List[VideoFormat]]:
        video_formats = []
        audio_formats = []
        
        for f in raw_formats:
            if f.get('protocol') == 'm3u8_native': continue
            
            # Ignorar formatos sin codecs conocidos o irrelevantes
            vcodec = f.get('vcodec', 'none')
            acodec = f.get('acodec', 'none')
            
            if vcodec == 'none' and acodec == 'none': continue

            # Crear objeto VideoFormat
            fmt = VideoFormat(
                format_id=f['format_id'],
                ext=f['ext'],
                resolution=f.get('resolution') or 'N/A',
                fps=f.get('fps'),
                filesize=f.get('filesize'),
                vcodec=vcodec,
                acodec=acodec,
                note=f.get('format_note', '')
            )
            
            # Clasificación
            # Audio puro
            if vcodec == 'none' and acodec != 'none':
                audio_formats.append(fmt)
            
            # Video (puede tener audio o ser video only)
            # Solo nos interesan los videos "reales" (mp4/webm), ignoramos cosas raras
            elif vcodec != 'none':
                video_formats.append(fmt)
        
        # Orden solicitado: "de peor a mejor calidad siempre"
        # Ordenamos Audio por filesize (proxy de bitrate) ascendente (peor -> mejor)
        audio_formats.sort(key=lambda x: x.filesize or 0)
        
        # Ordenamos Video por Altura (resolucion) y luego bitrate/filesize ascendente
        # Extraemos altura '1080p' -> 1080 integer para ordenar bien
        def get_height(res_str):
            try:
                return int(res_str.replace('p', '').split('x')[-1].strip())
            except:
                return 0
                
        video_formats.sort(key=lambda x: (get_height(x.resolution), x.filesize or 0))

        return video_formats, audio_formats

    def _process_subtitles(self, info_dict: Dict[str, Any]) -> List[SubtitleInfo]:
        """Extrae subtítulos manuales y automáticos"""
        subs = []
        
        def add_subs(source_dict, is_auto=False):
            if not source_dict: return
            for lang, sub_list in source_dict.items():
                if not sub_list: continue
                # yt-dlp devuelve una lista de formatos para el sub, tomamos el primero
                sub_data = sub_list[0]
                
                # Intentamos obtener un nombre legible
                raw_name = sub_data.get('name')
                
                # Lógica de nombrado
                if raw_name:
                    display_name = f"{raw_name}"
                    if is_auto and "(Auto)" not in display_name:
                        display_name += " (Auto)"
                else:
                    display_name = f"{lang} (Auto)" if is_auto else lang

                # Evitar duplicados exactos si ya existe (por si acaso)
                if not any(s.lang == lang and s.name == display_name for s in subs):
                    subs.append(SubtitleInfo(lang=lang, name=display_name, ext=sub_data.get('ext', 'vtt')))

        # 1. Subtítulos manuales
        # Nota: Algunos videos NO tienen subs manuales, solo auto.
        add_subs(info_dict.get('subtitles', {}), is_auto=False)
        
        # 2. Subtítulos automáticos
        add_subs(info_dict.get('automatic_captions', {}), is_auto=True)
        
        # Ordenar: Manuales primero, luego Autos. Alfabéticamente dentro de cada grupo.
        # Simple heurística: si tiene "(Auto)" va al final.
        subs.sort(key=lambda x: (1 if "(Auto)" in x.name else 0, x.name))
        
        return subs
