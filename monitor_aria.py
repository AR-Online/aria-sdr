#!/usr/bin/env python3
"""
Monitor da Conexão ARIA
Execute: python monitor_aria.py
"""

import requests
import json
from datetime import datetime

# Configurações da ARIA
ARIA_TOKEN = "c3e79a1e8503825ba091f5e46adeea724131d37f19cc8190c14ba7d6f5efbc7805125dd0bd5d4806be4caee1efe262d42e8b539fad5691d35872a10e1b84e550acc87c1c782461f452d2f72acdbec7204706a402b5963d74d5f6a9b8ae051ac407216f838780e5f937cf6ba745ea893ee4c52557a924ca451e1134af58"
API_BASE = "https://api-aronline.mindchatapp.com.br"
ARIA_CONNECTION_ID = 8
ARIA_WHATSAPP_NUMBER = "5516997918658"

def get_aria_connection():
    """Busca especificamente a conexão ARIA"""
    print(f"\n{'='*60}")
    print(f"MONITOR DA CONEXAO ARIA")
    print(f"{'='*60}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"ID da Conexão: {ARIA_CONNECTION_ID}")
    print(f"Número WhatsApp: {ARIA_WHATSAPP_NUMBER}")
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {ARIA_TOKEN}"
    }
    
    try:
        # Buscar todas as conexões
        response = requests.get(f"{API_BASE}/api/connections", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            connections = data.get("connections", [])
            
            # Encontrar a conexão ARIA
            aria_connection = None
            for conn in connections:
                if conn.get("id") == ARIA_CONNECTION_ID:
                    aria_connection = conn
                    break
            
            if aria_connection:
                print(f"\nCONEXAO ARIA ENCONTRADA:")
                print(f"   ID: {aria_connection.get('id')}")
                print(f"   Nome: {aria_connection.get('name')}")
                print(f"   Status: {aria_connection.get('status')}")
                print(f"   Número: {aria_connection.get('number')}")
                print(f"   Criada em: {aria_connection.get('createdAt')}")
                print(f"   Última atualização: {aria_connection.get('updatedAt')}")
                print(f"   É padrão: {aria_connection.get('isDefault')}")
                
                # Verificar status
                if aria_connection.get('status') == 'CONNECTED':
                    print(f"\nSTATUS: CONECTADA - ARIA funcionando!")
                else:
                    print(f"\nSTATUS: DESCONECTADA - ARIA com problemas!")
                
                return aria_connection
            else:
                print(f"\nCONEXAO ARIA NAO ENCONTRADA!")
                print(f"   Procurando ID: {ARIA_CONNECTION_ID}")
                print(f"   Conexoes disponiveis:")
                for conn in connections:
                    print(f"     - ID: {conn.get('id')}, Nome: {conn.get('name')}, Status: {conn.get('status')}")
                return None
        else:
            print(f"\nERRO AO BUSCAR CONEXOES:")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"\nERRO: {e}")
        return None

def get_aria_messages():
    """Busca mensagens da ARIA"""
    print(f"\n{'='*60}")
    print(f"MENSAGENS DA ARIA")
    print(f"{'='*60}")
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {ARIA_TOKEN}"
    }
    
    try:
        # Buscar mensagens recentes
        response = requests.get(f"{API_BASE}/api/messages?page=1&pageSize=5", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            total_messages = data.get('count', 0)
            messages = data.get('messages', [])
            
            print(f"Total de mensagens: {total_messages}")
            print(f"Ultimas 5 mensagens:")
            
            for i, msg in enumerate(messages, 1):
                print(f"\n   Mensagem {i}:")
                print(f"     ID: {msg.get('id')}")
                print(f"     De: {msg.get('from')}")
                print(f"     Para: {msg.get('to')}")
                print(f"     Texto: {msg.get('text', {}).get('body', 'N/A')[:50]}...")
                print(f"     Timestamp: {msg.get('timestamp')}")
                print(f"     Status: {msg.get('status')}")
            
            return True
        else:
            print(f"ERRO AO BUSCAR MENSAGENS:")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def test_aria_send_message():
    """Testa envio de mensagem via ARIA"""
    print(f"\n{'='*60}")
    print(f"TESTE DE ENVIO VIA ARIA")
    print(f"{'='*60}")
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {ARIA_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Mensagem de teste
    test_message = {
        "phone": "5516999999999",  # Número de teste
        "message": f"Teste ARIA - {datetime.now().strftime('%H:%M:%S')}",
        "type": "text"
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/send", json=test_message, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"MENSAGEM ENVIADA COM SUCESSO!")
            print(f"   Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"ERRO AO ENVIAR MENSAGEM:")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERRO: {e}")
        return False

def main():
    """Monitor completo da ARIA"""
    print("MONITOR DA CONEXAO ARIA")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Teste 1: Status da conexão
    aria_connection = get_aria_connection()
    
    if aria_connection and aria_connection.get('status') == 'CONNECTED':
        # Teste 2: Mensagens
        messages_ok = get_aria_messages()
        
        # Teste 3: Envio de mensagem
        send_ok = test_aria_send_message()
        
        # Resumo
        print(f"\n{'='*60}")
        print(f"RESUMO DO MONITOR ARIA")
        print(f"{'='*60}")
        print(f"[OK] Conexao ARIA: CONECTADA")
        print(f"[{'OK' if messages_ok else 'ERRO'}] Mensagens: {'OK' if messages_ok else 'ERRO'}")
        print(f"[{'OK' if send_ok else 'ERRO'}] Envio: {'OK' if send_ok else 'ERRO'}")
        
        if messages_ok and send_ok:
            print(f"\nARIA TOTALMENTE FUNCIONAL!")
        else:
            print(f"\nARIA COM PROBLEMAS PARCIAIS!")
    else:
        print(f"\nARIA DESCONECTADA OU COM PROBLEMAS!")

if __name__ == "__main__":
    main()
