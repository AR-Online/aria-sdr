#!/usr/bin/env python3
"""
Setup ngrok para webhook Mindchat
Execute: python setup_ngrok.py
"""

import subprocess
import requests
import time
import json

def install_ngrok():
    """Instala ngrok se não estiver instalado"""
    print("VERIFICANDO NGROK...")
    
    try:
        result = subprocess.run(["ngrok", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("NGROK JA INSTALADO!")
            return True
        else:
            print("NGROK NAO ENCONTRADO!")
            return False
    except FileNotFoundError:
        print("NGROK NAO INSTALADO!")
        return False

def start_ngrok_tunnel(port=8000):
    """Inicia túnel ngrok"""
    print(f"\nINICIANDO TUNEL NGROK NA PORTA {port}...")
    
    try:
        # Iniciar ngrok em background
        process = subprocess.Popen(
            ["ngrok", "http", str(port), "--log=stdout"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Aguardar ngrok inicializar
        time.sleep(3)
        
        # Obter URL pública
        try:
            response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
            if response.status_code == 200:
                data = response.json()
                tunnels = data.get("tunnels", [])
                
                for tunnel in tunnels:
                    if tunnel.get("proto") == "https":
                        public_url = tunnel.get("public_url")
                        print(f"TUNEL NGROK ATIVO:")
                        print(f"URL Publica: {public_url}")
                        print(f"URL Webhook: {public_url}/webhook/mindchat/whatsapp")
                        return public_url
                
                print("ERRO: Nenhum tunel HTTPS encontrado!")
                return None
            else:
                print("ERRO: Nao foi possivel obter URL do ngrok")
                return None
                
        except Exception as e:
            print(f"ERRO ao obter URL do ngrok: {e}")
            return None
            
    except Exception as e:
        print(f"ERRO ao iniciar ngrok: {e}")
        return None

def create_mindchat_webhook(ngrok_url):
    """Cria webhook no Mindchat com URL do ngrok"""
    print(f"\n{'='*60}")
    print(f"CRIANDO WEBHOOK NO MINDCHAT")
    print(f"{'='*60}")
    
    MINDCHAT_TOKEN = "c3e79a1e8503825ba091f5e46adeea724131d37f19cc8190c14ba7d6f5efbc7805125dd0bd5d4806be4caee1efe262d42e8b539fad5691d35872a10e1b84e550acc87c1c782461f452d2f72acdbec7204706a402b5963d74d5f6a9b8ae051ac407216f838780e5f937cf6ba745ea893ee4c52557a924ca451e1134af58"
    API_BASE = "https://api-aronline.mindchatapp.com.br"
    
    webhook_url = f"{ngrok_url}/webhook/mindchat/whatsapp"
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {MINDCHAT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    webhook_data = {
        "url": webhook_url,
        "events": ["message", "status", "delivery"],
        "verify_token": "aria_verify_token",
        "active": True,
        "description": "ARIA-SDR Webhook via ngrok"
    }
    
    try:
        response = requests.post(f"{API_BASE}/webhook", json=webhook_data, headers=headers, timeout=10)
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"WEBHOOK CRIADO COM SUCESSO!")
            print(f"URL: {webhook_url}")
            print(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"ERRO AO CRIAR WEBHOOK:")
            print(f"Status: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def test_webhook(ngrok_url):
    """Testa o webhook criado"""
    print(f"\n{'='*60}")
    print(f"TESTANDO WEBHOOK")
    print(f"{'='*60}")
    
    webhook_url = f"{ngrok_url}/webhook/mindchat/whatsapp"
    
    # Simular mensagem do WhatsApp
    test_payload = {
        "messages": [
            {
                "id": "test_msg_123",
                "from": "5516999999999",
                "timestamp": str(int(time.time())),
                "type": "text",
                "text": {
                    "body": "Teste de mensagem via ngrok"
                }
            }
        ],
        "contacts": [
            {
                "profile": {
                    "name": "Teste ngrok"
                }
            }
        ]
    }
    
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(webhook_url, json=test_payload, headers=headers, timeout=10)
        
        print(f"URL: {webhook_url}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("WEBHOOK FUNCIONANDO!")
            return True
        else:
            print("WEBHOOK COM PROBLEMAS!")
            return False
            
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def main():
    """Setup completo do ngrok"""
    print("SETUP NGROK PARA WEBHOOK MINDCHAT")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar ngrok
    if not install_ngrok():
        print("\nINSTRUCOES PARA INSTALAR NGROK:")
        print("1. Baixe ngrok: https://ngrok.com/download")
        print("2. Extraia o arquivo")
        print("3. Adicione ao PATH do sistema")
        print("4. Execute novamente este script")
        return
    
    # Iniciar túnel
    ngrok_url = start_ngrok_tunnel()
    if not ngrok_url:
        print("ERRO: Nao foi possivel iniciar ngrok!")
        return
    
    # Criar webhook
    webhook_ok = create_mindchat_webhook(ngrok_url)
    
    # Testar webhook
    test_ok = test_webhook(ngrok_url)
    
    # Resumo
    print(f"\n{'='*60}")
    print(f"RESUMO DO SETUP")
    print(f"{'='*60}")
    print(f"[{'OK' if webhook_ok else 'ERRO'}] Webhook criado")
    print(f"[{'OK' if test_ok else 'ERRO'}] Webhook testado")
    
    if webhook_ok and test_ok:
        print(f"\nSUCESSO! ARIA FUNCIONANDO COM NGROK!")
        print(f"URL Publica: {ngrok_url}")
        print(f"Webhook: {ngrok_url}/webhook/mindchat/whatsapp")
        print(f"\nAGORA VOCE PODE TESTAR NO WHATSAPP!")
    else:
        print(f"\nPROBLEMAS NO SETUP!")

if __name__ == "__main__":
    main()
