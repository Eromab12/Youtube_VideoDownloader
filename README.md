# YTDL-NIS Python Downloader (No sirve por los momentos)

Un descargador de videos de YouTube moderno y minimalista construido con **Python**, **FastAPI** y **HTMX**. Diseñado como alternativa ligera y personalizable.

![Preview](https://raw.githubusercontent.com/yt-dlp/yt-dlp/master/devscripts/logo.svg) <!-- Puedes reemplazar esto con una captura real de tu app -->

## Características

- 🎥 **Descarga de Video y Audio**: Soporte para múltiples formatos (MP4, MKV, MP3, M4A).
- ⚡ **Interfaz Reactiva**: UI moderna y oscura usando HTMX (sin recargas de página).
- 🛠 **Codecs y Calidad**: Selección detallada de resolución y codecs (AV1, VP9, H.264).
- 🧩 **Portable**: Se compila en un solo archivo `.exe`.

## Requisitos Previos

### 1. FFmpeg (Esencial)
Para que el programa pueda unir el mejor video con el mejor audio (y convertir formatos), necesita **FFmpeg**.

1.  **Descargar**: Ve a [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/) y descarga `ffmpeg-release-essentials.zip`.
2.  **Instalar (Opción Portátil)**:
    -   Extrae el archivo `.zip`.
    -   Entra a la carpeta `bin`.
    -   Copia `ffmpeg.exe` y `ffprobe.exe`.
    -   Pégalos en la **misma carpeta** donde tengas tu `YTDL-Downloader.exe` (o en la carpeta raíz del proyecto si lo corres con código, aun no funciona el .exe).

### 2. Python (Solo para desarrollo)
Si vas a modificar el código, necesitas Python 3.10+.

## Ejecución

### Desde Código (Desarrollo)
1.  Instalar dependencias:
    ```bash
    pip install -r requirements.txt
    ```
2.  Ejecutar:
    ```bash
    run_dev.bat
    ```

### Crear Ejecutable (.exe)
1.  Haz doble click en `build_exe.bat`.
2.  Al finalizar, busca tu archivo en la carpeta `dist/`.

## Preguntas Frecuentes

**¿La aplicación se actualiza sola?**
No automáticamente. Como es un ejecutable "congelado", la versión de `yt-dlp` interna es la que había cuando compilaste el programa.
- **Si YouTube cambia algo y deja de funcionar**: Ejecuta nuevamente `build_exe.bat`. Esto descargará la última versión de `yt-dlp` y generará un nuevo `.exe` actualizado.

**¿Dónde se guardan las descargas?**
Por defecto, se crea una carpeta `media` junto al ejecutable.

## Tecnologías

-   **Backend**: FastAPI (Python)
-   **Frontend**: Jinja2 + HTMX + CSS Vanilla
-   **Core**: yt-dlp
