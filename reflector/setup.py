#!/usr/bin/env python3
"""
ARIA-SDR Reflector - Configuração Rápida
"""
import os
import shutil

def setup_reflector():
    """Configuração rápida do reflector"""
    print("🚀 ARIA-SDR Reflector - Configuração Rápida")
    print("=" * 50)
    
    # Verificar se .env existe
    if not os.path.exists(".env"):
        if os.path.exists("env.example"):
            shutil.copy("env.example", ".env")
            print("✅ Arquivo .env criado a partir do env.example")
        else:
            print("❌ Arquivo env.example não encontrado")
            return False
    else:
        print("✅ Arquivo .env já existe")
    
    # Criar diretório tmp se não existir
    if not os.path.exists("tmp"):
        os.makedirs("tmp")
        print("✅ Diretório tmp criado")
    
    print("\n📝 Próximos passos:")
    print("1. Edite o arquivo .env com suas chaves:")
    print("   - OPENAI_API_KEY")
    print("   - SUPABASE_URL")
    print("   - SUPABASE_SERVICE_ROLE_KEY")
    print("2. Execute: python test_system.py")
    print("3. Execute: python main.py")
    
    return True

if __name__ == "__main__":
    setup_reflector()
