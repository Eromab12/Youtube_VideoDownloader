import uvicorn
import os
import sys
import webbrowser
from threading import Timer
from app.main import app as fastapi_app

# Este archivo sirve como punto de entrada (Entry Point) para:
# 1. Ejecución directa (python launcher.py)
# 2. PyInstaller (apuntando a este archivo se resuelven mejor los imports)

if __name__ == "__main__":
    # FIX: PyInstaller --windowed establece stdout/stderr como None.
    # Uvicorn intenta llamar a .isatty() en ellos y falla.
    # Los redirigimos a devnull si no existen.
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")

    def open_browser():
        webbrowser.open("http://127.0.0.1:8000")
    
    # Solo abrir navegador si no estamos en modo reload (debug)
    # Pero para el exe final (sin reload) es util.
    Timer(1.5, open_browser).start()
    
    # freeze_support() es necesario para multiprocessing en Windows con PyInstaller
    from multiprocessing import freeze_support
    freeze_support()
    
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, reload=False)
