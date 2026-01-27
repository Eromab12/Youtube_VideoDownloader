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

    import socket

    def find_available_port(start_port=8000, max_attempts=10):
        """Busca un puerto libre iniciando desde start_port"""
        port = start_port
        for _ in range(max_attempts):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('127.0.0.1', port)) != 0:
                    return port
                port += 1
        return start_port # Fallback to default if all usually taken

    port = find_available_port()

    def open_browser():
        webbrowser.open(f"http://127.0.0.1:{port}")
    
    # Solo abrir navegador si no estamos en modo reload (debug)
    # Pero para el exe final (sin reload) es util.
    Timer(1.5, open_browser).start()
    
    # freeze_support() es necesario para multiprocessing en Windows con PyInstaller
    from multiprocessing import freeze_support
    freeze_support()
    
    print(f"Iniciando servidor en http://127.0.0.1:{port}")
    uvicorn.run(fastapi_app, host="127.0.0.1", port=port, reload=False)
