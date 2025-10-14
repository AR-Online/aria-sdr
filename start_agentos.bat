@echo off
echo ========================================
echo ARIA-SDR - AgentOS Startup Script
echo ========================================

REM Ativar ambiente virtual
call agno_env\Scripts\activate.bat

REM Verificar se o ambiente foi ativado
python -c "import sys; print('Python path:', sys.executable)"

REM Verificar versão do OpenAI
python -c "import openai; print('OpenAI version:', openai.__version__)"

REM Executar AgentOS
echo.
echo Iniciando AgentOS...
python aria_first_os.py
