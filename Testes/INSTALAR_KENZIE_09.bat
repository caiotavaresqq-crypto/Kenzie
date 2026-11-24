@echo off
setlocal
cd /d "%~dp0"
echo ==================================================
echo KENZIE 0.9 - INSTALACAO DO MOTOR LOCAL
echo ==================================================
echo.
where ollama >nul 2>nul
if errorlevel 1 (
  echo Ollama nao foi encontrado.
  echo Instale pelo site oficial: https://ollama.com/download
  echo Depois feche e reabra este terminal.
  pause
  exit /b 1
)
echo Ollama encontrado.
echo Baixando modelo configurado no .env (default qwen2.5:1.5b)...
ollama pull qwen2.5:1.5b
if errorlevel 1 (
  echo O download do modelo falhou. Confira a conexao e tente novamente.
  pause
  exit /b 1
)
echo.
echo Instalacao do modelo concluida. Para iniciar, use INICIAR_KENZIE.bat
pause
