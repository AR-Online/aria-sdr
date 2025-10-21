# api/main.py
"""
API Entry Point for ARIA-SDR

Este arquivo serve como ponto de entrada alternativo para a API.
Para uso padrão, utilize o arquivo principal: ../main.py

Este arquivo pode ser usado para:
- Deploy em plataformas que requerem api/main.py
- Testes de estrutura alternativa
- Configurações específicas de API

Para executar:
    uvicorn api.main:app --reload
"""

from fastapi import FastAPI

# Importar a aplicação principal
import sys
from pathlib import Path

# Adicionar diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importar app do main.py principal
from main import app

# Exportar para uso com uvicorn
__all__ = ["app"]

if __name__ == "__main__":
    import uvicorn
    
    print("⚠️  AVISO: Este é um ponto de entrada alternativo.")
    print("    Para uso normal, execute: python main.py")
    print("    Ou use: uvicorn api.main:app")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
