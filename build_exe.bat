@echo off
echo Instalando PyInstaller...
pip install pyinstaller

echo Limpiando builds anteriores...
rmdir /s /q build dist
del *.spec

echo Generando ejecutable...
echo Nota: Esto puede tomar unos minutos.

pyinstaller --noconfirm --onefile --windowed --name "YTDL-Downloader" ^
    --add-data "app/templates;app/templates" ^
    --add-data "app/static;app/static" ^
    --hidden-import "uvicorn" ^
    --hidden-import "uvicorn.logging" ^
    --hidden-import "uvicorn.loops" ^
    --hidden-import "uvicorn.loops.auto" ^
    --hidden-import "uvicorn.protocols" ^
    --hidden-import "uvicorn.protocols.http" ^
    --hidden-import "uvicorn.protocols.http.auto" ^
    --hidden-import "uvicorn.protocols.websockets" ^
    --hidden-import "uvicorn.protocols.websockets.auto" ^
    --hidden-import "uvicorn.lifespan.on" ^
    --hidden-import "app" ^
    launcher.py

echo.
echo ==========================================
echo Build completado!
echo El ejecutable esta en la carpeta 'dist'.
echo ==========================================
pause
