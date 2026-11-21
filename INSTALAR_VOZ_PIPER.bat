@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo   KENZIE - INSTALADOR DA VOZ NEURAL PIPER
echo ============================================
echo.
echo Instalando o motor Piper e suas dependencias...
py -m pip install piper-tts pyttsx3
if errorlevel 1 (
    echo.
    echo ERRO: nao foi possivel instalar o Piper.
    pause
    exit /b 1
)
echo.
echo Baixando a voz Cadu - Portugues do Brasil (aprox. 63 MB)...
if not exist "voices" mkdir "voices"
py -m piper.download_voices --data-dir voices pt_BR-cadu-medium
if errorlevel 1 (
    echo.
    echo ERRO: nao foi possivel baixar o modelo de voz.
    pause
    exit /b 1
)
echo.
echo.
echo Piper instalado! Abra a Kenzie normalmente.
pause
