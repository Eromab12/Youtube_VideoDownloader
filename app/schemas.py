from pydantic import BaseModel
from typing import List, Optional, Dict

class VideoFormat(BaseModel):
    """
    Representa una opción de formato de descarga disponible.
    Incluye detalles técnicos como codecs para usuarios avanzados.
    """
    format_id: str
    ext: str
    resolution: Optional[str] = "N/A"
    fps: Optional[float] = None
    filesize: Optional[int] = None
    vcodec: Optional[str] = None # Codec de Video (ej: avc1, vp9)
    acodec: Optional[str] = None # Codec de Audio (ej: mp4a, opus)
    note: Optional[str] = None

    @property
    def filesize_mb(self) -> str:
        if self.filesize:
            return f"{self.filesize / (1024 * 1024):.1f} MB"
        return "N/A"
    
    @property
    def codec_summary(self) -> str:
        """Resumen corto de codecs para la UI"""
        v = self.vcodec if self.vcodec and self.vcodec != 'none' else None
        a = self.acodec if self.acodec and self.acodec != 'none' else None
        if v and a: return f"{v} + {a}"
        if v: return f"{v} (Video)"
        if a: return f"{a} (Audio)"
        return "Unknown"

class SubtitleInfo(BaseModel):
    """Información sobre un subtítulo disponible"""
    lang: str
    name: str
    ext: str

class VideoInfo(BaseModel):
    """
    Información general del video, ahora incluyendo subtítulos y formatos separados.
    """
    id: str
    url: str
    title: str
    thumbnail: str
    duration: int
    uploader: str
    video_formats: List[VideoFormat]
    audio_formats: List[VideoFormat]
    subtitles: List[SubtitleInfo]
    
    @property
    def duration_str(self) -> str:
        m, s = divmod(self.duration, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"
