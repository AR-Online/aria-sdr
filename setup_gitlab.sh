#!/bin/bash
# Script para configurar GitLab remote para ARIA-SDR

echo "🚀 Configurando GitLab remote para ARIA-SDR..."

# Verificar se estamos em um repositório git
if [ ! -d ".git" ]; then
    echo "❌ Erro: Não estamos em um repositório git"
    exit 1
fi

# Verificar remotes atuais
echo "📋 Remotes atuais:"
git remote -v

echo ""
echo "📝 Para continuar, você precisa:"
echo "1. Criar um projeto no GitLab"
echo "2. Obter a URL do repositório GitLab"
echo ""

# Solicitar informações do usuário
read -p "Digite seu nome de usuário do GitLab: " GITLAB_USERNAME
read -p "Digite o nome do projeto no GitLab (ex: aria-sdr): " PROJECT_NAME

# Construir URL do GitLab
GITLAB_URL="https://gitlab.com/${GITLAB_USERNAME}/${PROJECT_NAME}.git"

echo ""
echo "🔗 URL do GitLab que será configurada: ${GITLAB_URL}"
echo ""

# Confirmar configuração
read -p "Confirma a configuração? (y/n): " CONFIRM

if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
    echo "⚙️  Configurando remote do GitLab..."
    
    # Adicionar remote do GitLab
    git remote add gitlab "$GITLAB_URL"
    
    echo "✅ Remote do GitLab adicionado!"
    echo ""
    echo "📋 Remotes configurados:"
    git remote -v
    
    echo ""
    echo "🚀 Próximos passos:"
    echo "1. Fazer push inicial: git push gitlab main"
    echo "2. Configurar sincronização: git remote set-url --add --push origin $GITLAB_URL"
    echo ""
    echo "💡 Para fazer push para ambos os repositórios simultaneamente:"
    echo "   git push origin main"
    echo ""
    
else
    echo "❌ Configuração cancelada"
    exit 1
fi

echo "🎉 Configuração concluída!"
