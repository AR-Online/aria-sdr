"""
Testes para lógica de roteamento e classificação de volume do ARIA-SDR
"""
import pytest
from main import classify_route


class TestClassifyRoute:
    """Testes para a função classify_route"""
    
    def test_route_recebimento_keywords(self):
        """Testa detecção de rota 'recebimento' por palavras-chave"""
        test_cases = [
            "Recebi uma mensagem",
            "A mensagem chegou",
            "Confirmação de leitura recebida",
            "Notificação de abertura",
        ]
        
        for user_text in test_cases:
            route, vars_out, next_action = classify_route(user_text, {})
            assert route == "recebimento", f"Falhou para: {user_text}"
    
    def test_route_envio_keywords(self):
        """Testa detecção de rota 'envio' por palavras-chave"""
        test_cases = [
            "Quero enviar mensagens",
            "Preciso mandar emails",
            "Como faço para disparar",
            "Gostaria de enviar",
        ]
        
        for user_text in test_cases:
            route, vars_out, next_action = classify_route(user_text, {})
            assert route == "envio", f"Falhou para: {user_text}"
    
    def test_route_from_variables(self):
        """Testa detecção de rota através de variáveis"""
        # Teste com fluxo_path definido
        route, vars_out, next_action = classify_route(
            "Mensagem qualquer",
            {"fluxo_path": "envio"}
        )
        assert route == "envio"
        
        route, vars_out, next_action = classify_route(
            "Mensagem qualquer",
            {"fluxo_path": "recebimento"}
        )
        assert route == "recebimento"
    
    def test_volume_classification_high(self):
        """Testa classificação de alto volume (>= 1200)"""
        test_cases = [
            {"lead_volumetria": "1500"},
            {"lead_volumetria": "2000 mensagens"},
            {"lead_duvida": "Preciso enviar 5000 emails"},
        ]
        
        for variables in test_cases:
            route, vars_out, next_action = classify_route(
                "Quero enviar mensagens",
                variables
            )
            
            assert route == "envio"
            assert vars_out.get("volume_alto") == "true"
            assert vars_out.get("volume_class") == "alto"
            assert next_action == "schedule"
    
    def test_volume_classification_low(self):
        """Testa classificação de baixo volume (< 1200)"""
        test_cases = [
            {"lead_volumetria": "500"},
            {"lead_volumetria": "100 mensagens"},
            {"lead_duvida": "Preciso enviar 50 emails"},
        ]
        
        for variables in test_cases:
            route, vars_out, next_action = classify_route(
                "Quero enviar mensagens",
                variables
            )
            
            assert route == "envio"
            assert vars_out.get("volume_alto") == "false"
            assert vars_out.get("volume_class") == "baixo"
            assert next_action == "buy_credits"
    
    def test_volume_threshold_boundary(self):
        """Testa o limiar exato de 1200"""
        # Exatamente 1200 deve ser alto volume
        route, vars_out, next_action = classify_route(
            "Quero enviar",
            {"lead_volumetria": "1200"}
        )
        assert vars_out.get("volume_alto") == "true"
        assert vars_out.get("volume_class") == "alto"
        
        # 1199 deve ser baixo volume
        route, vars_out, next_action = classify_route(
            "Quero enviar",
            {"lead_volumetria": "1199"}
        )
        assert vars_out.get("volume_alto") == "false"
        assert vars_out.get("volume_class") == "baixo"
    
    def test_volume_with_thousands_separator(self):
        """Testa parsing de números com separador de milhares"""
        test_cases = [
            "1.500",    # Formato brasileiro
            "1,500",    # Formato US
            "10.000",   # 10 mil
        ]
        
        for volume in test_cases:
            route, vars_out, next_action = classify_route(
                "Quero enviar",
                {"lead_volumetria": volume}
            )
            
            num = int(vars_out.get("volume_num", "0"))
            assert num >= 1200, f"Falhou para: {volume}"
            assert vars_out.get("volume_alto") == "true"
    
    def test_volume_keywords_high(self):
        """Testa palavras-chave que indicam alto volume"""
        test_cases = [
            "alto volume",
            "grande volume",
            "envio massivo",
            "em lote",
            "mais de mil mensagens",
        ]
        
        for text in test_cases:
            route, vars_out, next_action = classify_route(
                "Quero enviar",
                {"lead_volumetria": text}
            )
            
            assert vars_out.get("volume_alto") == "true"
            assert vars_out.get("volume_class") == "alto"
    
    def test_no_route_no_keywords(self):
        """Testa quando não há rota definida"""
        route, vars_out, next_action = classify_route(
            "Olá, como vai?",
            {}
        )
        
        assert route is None
        assert next_action is None
    
    def test_variables_output_structure(self):
        """Testa estrutura de variáveis de saída"""
        route, vars_out, next_action = classify_route(
            "Preciso enviar 2000 emails",
            {"lead_volumetria": "2000"}
        )
        
        # Verificar campos obrigatórios
        assert "volume_num" in vars_out
        assert "lead_volumetria" in vars_out
        assert "volume_alto" in vars_out
        assert "volume_class" in vars_out
        
        # Verificar tipos
        assert isinstance(vars_out["volume_num"], str)
        assert isinstance(vars_out["volume_alto"], str)
        assert isinstance(vars_out["volume_class"], str)


class TestWantRAG:
    """Testes para detecção de necessidade de RAG"""
    
    def test_rag_needed_keywords(self):
        """Testa palavras-chave que acionam RAG"""
        from main import want_rag
        
        test_cases = [
            "Como funciona o sistema?",
            "Qual o prazo de entrega?",
            "Como fazer o cadastro?",
            "Funciona em qual horario?",
            "Qual o valor?",
        ]
        
        for text in test_cases:
            assert want_rag(text, {}) is True, f"Falhou para: {text}"
    
    def test_rag_not_needed(self):
        """Testa casos onde RAG não é necessário"""
        from main import want_rag
        
        test_cases = [
            "Olá",
            "Obrigado",
            "Tudo bem",
        ]
        
        for text in test_cases:
            assert want_rag(text, {}) is False, f"Falhou para: {text}"
    
    def test_rag_forced_by_variable(self):
        """Testa forçar RAG via variável"""
        from main import want_rag
        
        result = want_rag("Qualquer texto", {"faq_mode": True})
        assert result is True


class TestThreadIDGeneration:
    """Testes para geração de thread_id"""
    
    def test_deterministic_thread_id(self):
        """Testa que thread_id é determinístico para mesmo remetente+canal"""
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        
        payload1 = {
            "message": "Teste 1",
            "variables": {
                "remetente": "user@example.com",
                "canal": "whatsapp"
            }
        }
        
        payload2 = {
            "message": "Teste 2",
            "variables": {
                "remetente": "user@example.com",
                "canal": "whatsapp"
            }
        }
        
        response1 = client.post(
            "/assist/routing",
            json=payload1,
            headers={"Authorization": "Bearer dtransforma2026"}
        )
        
        response2 = client.post(
            "/assist/routing",
            json=payload2,
            headers={"Authorization": "Bearer dtransforma2026"}
        )
        
        if response1.status_code == 200 and response2.status_code == 200:
            thread_id1 = response1.json().get("thread_id")
            thread_id2 = response2.json().get("thread_id")
            
            # Mesmo remetente+canal deve gerar mesmo thread_id
            assert thread_id1 == thread_id2


class TestAssistRouting:
    """Testes de integração para endpoint de routing"""
    
    def test_routing_with_all_fields(self):
        """Testa routing com todos os campos"""
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        
        payload = {
            "message": "Preciso enviar 1500 mensagens",
            "variables": {
                "remetente": "test@example.com",
                "canal": "web",
                "lead_volumetria": "1500"
            },
            "thread_id": "test-thread-123"
        }
        
        response = client.post(
            "/assist/routing",
            json=payload,
            headers={"Authorization": "Bearer dtransforma2026"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar campos obrigatórios
        assert "reply_text" in data
        assert "thread_id" in data
        assert data["thread_id"] == "test-thread-123"
    
    def test_routing_minimal_payload(self):
        """Testa routing com payload mínimo"""
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        
        payload = {"message": "Olá"}
        
        response = client.post(
            "/assist/routing",
            json=payload,
            headers={"Authorization": "Bearer dtransforma2026"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "reply_text" in data
        assert "thread_id" in data
        assert isinstance(data["thread_id"], str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

