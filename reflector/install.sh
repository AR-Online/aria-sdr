#!/bin/bash
# ARIA-SDR Reflector - Script de Instalação

echo "🚀 ARIA-SDR Reflector - Instalação"
echo "=================================="

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.8+ primeiro."
    exit 1
fi

echo "✅ Python 3 encontrado"

# Criar ambiente virtual
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo "📚 Instalando dependências..."
pip install -r requirements.txt

# Copiar arquivo de configuração
if [ ! -f ".env" ]; then
    echo "⚙️  Copiando arquivo de configuração..."
    cp env.example .env
    echo "📝 Edite o arquivo .env com suas chaves antes de executar"
fi

# Executar teste
echo "🧪 Executando teste de sistema..."
python test_system.py

echo ""
echo "✅ Instalação concluída!"
echo ""
echo "Próximos passos:"
echo "1. Edite o arquivo .env com suas chaves"
echo "2. Execute: python main.py"
echo "3. Acesse: http://localhost:8000"
