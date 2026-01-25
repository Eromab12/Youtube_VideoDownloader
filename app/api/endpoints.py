from fastapi import APIRouter, Form, Request, HTTPException, BackgroundTasks
from fastapi.templating import Jinja2Templates
from app.services import YtDlpService
from app.schemas import VideoInfo
import os

router = APIRouter()

# Reutilizamos la instancia de Templates
templates_dir = os.path.join(os.getcwd(), "app/templates")
templates = Jinja2Templates(directory=templates_dir)

service = YtDlpService()

@router.post("/preview")
async def preview_video(request: Request, url: str = Form(...)):
    """
    Endpoint para HTMX. Recibe una URL, extrae info y devuelve el HTML de la tarjeta de preview.
    """
    try:
        video_info: VideoInfo = service.get_video_info(url)
        return templates.TemplateResponse(
            "partials/video_preview.html", 
            {"request": request, "video": video_info}
        )
    except Exception as e:
        # En caso de error, devolvemos un snippet de error para HTMX
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "message": str(e)},
            status_code=400
        )

@router.post("/download")
async def download_video(
    background_tasks: BackgroundTasks,
    url: str = Form(...), 
    title: str = Form(...),
    video_format_id: str = Form(...),
    audio_format_id: str = Form(None),
    subtitles: list[str] = Form([])
):
    """
    Inicia la descarga combinando video y audio si es necesario.
    """
    # Construir el string de formato para yt-dlp
    # Si hay audio seleccionado explícito: 'video+audio'
    # Si no, solo 'video' (que puede tener audio integrado o no, riesgo del usuario si elije solo video mudo)
    final_format = f"{video_format_id}+{audio_format_id}" if audio_format_id else video_format_id
    
    background_tasks.add_task(service.download_video_background, url, final_format, subtitles)
    
    print(f"Tarea: {title} | Formato: {final_format} | Subs: {subtitles}")
    return {"status": "started", "message": f"Descargando {title}..."}
