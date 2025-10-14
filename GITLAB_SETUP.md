# Configuração do GitLab para ARIA-SDR

## Passos para criar e configurar o repositório no GitLab

### 1. Criar o repositório no GitLab

1. Acesse [GitLab.com](https://gitlab.com) e faça login
2. Clique em "New Project" ou "Novo Projeto"
3. Escolha "Create blank project"
4. Configure:
   - **Project name**: `aria-sdr`
   - **Project slug**: `aria-sdr`
   - **Project description**: `ARIA-SDR - Agente de Relacionamento Inteligente da AR Online`
   - **Visibility Level**: Private (recomendado) ou Internal
   - **Initialize repository with a README**: ❌ (desmarque, pois já temos conteúdo)
5. Clique em "Create project"

### 2. Obter a URL do repositório GitLab

Após criar o projeto, você verá uma página com instruções. A URL será algo como:
- HTTPS: `https://gitlab.com/AR-Online/aria-sdr.git`
- SSH: `git@gitlab.com:AR-Online/aria-sdr.git`

### 3. Configurar o remote GitLab

Execute os comandos abaixo substituindo `GITLAB_URL` pela URL do seu repositório:

```bash
# Adicionar o remote do GitLab
git remote add gitlab GITLAB_URL

# Verificar os remotes configurados
git remote -v

# Fazer push para o GitLab
git push gitlab main

# Configurar push para ambos os remotes
git remote set-url --add --push origin https://github.com/AR-Online/ARIA-SDR.git
git remote set-url --add --push origin GITLAB_URL
```

### 4. Configuração de sincronização automática

Para manter ambos os repositórios sincronizados, você pode:

#### Opção A: Push para ambos simultaneamente
```bash
# Configurar push para múltiplos remotes
git remote set-url --add --push origin https://github.com/AR-Online/ARIA-SDR.git
git remote set-url --add --push origin https://gitlab.com/AR-Online/aria-sdr.git

# Agora um simples 'git push' enviará para ambos
git push origin main
```

#### Opção B: Push separado para cada remote
```bash
# Push para GitHub
git push origin main

# Push para GitLab
git push gitlab main
```

### 5. Configurar CI/CD no GitLab

O GitLab tem seu próprio sistema de CI/CD. Você pode:

1. Criar um arquivo `.gitlab-ci.yml` na raiz do projeto
2. Configurar pipelines específicos para GitLab
3. Ou manter apenas os workflows do GitHub Actions

### 6. Configurações recomendadas

- **Branch protection**: Configure proteção para o branch `main` em ambos os repositórios
- **Webhooks**: Configure webhooks se necessário para integrações
- **Issues e MRs**: Use o sistema de issues do GitLab se preferir
- **Wiki**: Mantenha documentação sincronizada entre ambos

## Comandos úteis

```bash
# Verificar status dos remotes
git remote -v

# Fazer fetch de ambos os remotes
git fetch origin
git fetch gitlab

# Ver diferenças entre remotes
git log origin/main..gitlab/main
git log gitlab/main..origin/main

# Sincronizar um remote com o outro
git push gitlab origin/main:main
git push origin gitlab/main:main
```

## Notas importantes

- Mantenha ambos os repositórios sincronizados
- Use tags para releases em ambos os repositórios
- Configure notificações para ambos os sistemas
- Documente qual repositório é o "primário" para sua equipe
