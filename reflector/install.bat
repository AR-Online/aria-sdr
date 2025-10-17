@echo off
REM ARIA-SDR Reflector - Script de Instalação Windows

echo 🚀 ARIA-SDR Reflector - Instalação
echo ==================================

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado. Instale Python 3.8+ primeiro.
    pause
    exit /b 1
)

echo ✅ Python encontrado

REM Criar ambiente virtual
if not exist "venv" (
    echo 📦 Criando ambiente virtual...
    python -m venv venv
)

REM Ativar ambiente virtual
echo 🔧 Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Instalar dependências
echo 📚 Instalando dependências...
pip install -r requirements.txt

REM Copiar arquivo de configuração
if not exist ".env" (
    echo ⚙️  Copiando arquivo de configuração...
    copy env.example .env
    echo 📝 Edite o arquivo .env com suas chaves antes de executar
)

REM Executar teste
echo 🧪 Executando teste de sistema...
python test_system.py

echo.
echo ✅ Instalação concluída!
echo.
echo Próximos passos:
echo 1. Edite o arquivo .env com suas chaves
echo 2. Execute: python main.py
echo 3. Acesse: http://localhost:8000
pause
