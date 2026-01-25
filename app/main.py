import sys
import os

# Agregar el directorio raíz del proyecto al sys.path para permitir imports absolutos (from app...)
# Esto soluciona errores de "ModuleNotFoundError: No module named 'app'"
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import webbrowser
from threading import Timer
from app.core.config import settings
from app.api.endpoints import router as api_router

# Función para obtener rutas correctas ya sea en dev o en exe (PyInstaller)
def get_resource_path(relative_path):
    """Obtiene la ruta absoluta al recurso, funciona para dev y para PyInstaller (sys._MEIPASS)"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

# Inicialización de la aplicación FastAPI
app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Montar estáticos usando la función de ruta segura
static_dir = get_resource_path("static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir) # En modo exe esto no debería ser necesario si se empaquetó bien
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Configurar Templates usando la función de ruta segura
templates_dir = get_resource_path("templates")
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir)
templates = Jinja2Templates(directory=templates_dir)

# Incluir Rutas
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Ruta Principal (Home).
    
    Args:
        request (Request): Objeto de solicitud actual, necesario para Jinja2.
        
    Returns:
        HTMLResponse: Renderiza el archivo 'index.html' con el contexto dado.
    """
    return templates.TemplateResponse("index.html", {"request": request, "title": settings.PROJECT_NAME})

# El bloque if __name__ == "__main__" se ha movido a launcher.py en la raíz
# para evitar problemas de imports con PyInstaller.
