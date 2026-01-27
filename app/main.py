import sys
import os

# Borramos el hack de sys.path ya que usaremos imports relativos y el launcher maneja el root
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from .core.log_manager import log_manager
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import webbrowser
from threading import Timer

# Imports relativos (Mejor para paquete empaquetado)
from .core.config import settings
from .api.endpoints import router as api_router

# Función para obtener rutas correctas ya sea en dev o en exe (PyInstaller)
def get_resource_path(relative_path):
    """Obtiene la ruta absoluta al recurso, funciona para dev y para PyInstaller (sys._MEIPASS)"""
    if hasattr(sys, '_MEIPASS'):
        # En PyInstaller, a veces los datos se guardan en la raíz de _MEIPASS o dentro de app/
        # Probamos ambos
        base_path = sys._MEIPASS
        # Intento 1: Directo (como lo agregamos en build_exe)
        path = os.path.join(base_path, relative_path) # ej: _MEIPASS/app/static
        if os.path.exists(path):
            return path
        # Intento 2: Si por alguna razón se aplanó (poco probable con add-data "app/x;app/x")
        return os.path.join(base_path, "app", relative_path)
        
    return os.path.join(os.path.dirname(__file__), relative_path)

# Inicialización de la aplicación FastAPI
app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Montar estáticos usando la función de ruta segura
# NOTA: Como main.py está dentro de app/, dirname(__file__) es .../app/
# Si relative_path es "static", busca .../app/static. CORRECTO.
static_dir = get_resource_path("static")
if not os.path.exists(static_dir):
    # Fallback para dev si get_resource_path falla
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if not os.path.exists(static_dir): os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Configurar Templates usando la función de ruta segura
templates_dir = get_resource_path("templates")
if not os.path.exists(templates_dir):
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    if not os.path.exists(templates_dir): os.makedirs(templates_dir)

templates = Jinja2Templates(directory=templates_dir)

# Incluir Rutas
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.websocket("/ws/logs/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    print(f"WS Connection request from {client_id}")
    await log_manager.connect(websocket)
    print(f"WS Connected {client_id}")
    try:
        while True:
            # Mantener conexión viva, aunque solo enviamos info (server->client)
            # Podríamos esperar mensajes del cliente si fuera necesario
            await websocket.receive_text()
    except WebSocketDisconnect:
        print(f"WS Disconnected {client_id}")
        log_manager.disconnect(websocket)
    except Exception as e:
        print(f"WS Error {client_id}: {e}")
        log_manager.disconnect(websocket)


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
