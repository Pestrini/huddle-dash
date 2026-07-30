@echo off
title Huddle Dashboard TI HURP
echo ==================================================
echo      Iniciando Huddle Dashboard TI
echo ==================================================
echo.

:: Vai para a pasta onde o .bat esta sendo executado dinamicamente
cd /d "%~dp0"

:: Verifica se o Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [AVISO] O Python nao foi encontrado neste computador.
    echo Iniciando o download e a instalacao automatica do Python...
    echo Isso pode levar alguns minutos. Por favor, aguarde.
    echo.
    
    :: Baixa o instalador do Python 3.11
    curl -o python_installer.exe https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
    
    :: Executa a instalacao de forma passiva, adicionando ao PATH apenas para o usuario atual
    start /wait python_installer.exe /passive InstallAllUsers=0 PrependPath=1 Include_pip=1
    
    :: Apaga o instalador
    del python_installer.exe
    
    echo.
    echo ==================================================
    echo INSTALACAO CONCLUIDA!
    echo Como as variaveis de sistema foram atualizadas, 
    echo FECHE ESTA JANELA E ABRA O SCRIPT NOVAMENTE.
    echo ==================================================
    pause
    exit /b 0
)

echo Verificando bibliotecas necessarias (instalando apenas o que estiver faltando)...
pip install -r requirements.txt --quiet --disable-pip-version-check

echo.
echo Abrindo a interface no navegador...
python -m streamlit run main.py

pause
