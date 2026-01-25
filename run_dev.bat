@echo off
echo Instalando dependencias...
pip install -r requirements.txt
echo.
echo Iniciando servidor de desarrollo...
python -m uvicorn app.main:app --reload --port 8000
pause
