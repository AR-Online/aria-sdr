"""
Web Search Integration para ARIA
Usa duckduckgo-search diretamente
"""

from duckduckgo_search import DDGS

def search_web(query: str, max_results: int = 5) -> dict:
    """
    Busca informações na web usando DuckDuckGo.
    
    Args:
        query: Texto para buscar
        max_results: Número máximo de resultados
    
    Returns:
        Dict com results (lista) e formatted_text (string)
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        
        if not results:
            return {
                "results": [],
                "formatted_text": "❌ Nenhum resultado encontrado.",
                "success": False
            }
        
        # Formatação dos resultados
        formatted_lines = ["🔍 **Resultados da busca na web:**\n"]
        
        for i, result in enumerate(results[:max_results], 1):
            title = result.get('title', 'Sem título')
            body = result.get('body', '')
            href = result.get('href', '')
            
            formatted_lines.append(f"**{i}. {title}**")
            if body:
                formatted_lines.append(f"   {body}")
            if href:
                formatted_lines.append(f"   🔗 {href}")
            formatted_lines.append("")  # Linha em branco
        
        formatted_lines.append("\n_Fonte: DuckDuckGo_")
        
        return {
            "results": results,
            "formatted_text": "\n".join(formatted_lines),
            "success": True,
            "count": len(results)
        }
        
    except Exception as e:
        return {
            "results": [],
            "formatted_text": f"❌ Erro na busca web: {str(e)}",
            "success": False,
            "error": str(e)
        }


def should_use_web_search(text: str) -> bool:
    """
    Determina se deve usar web search baseado no texto.
    
    Palavras-chave que indicam necessidade de busca web:
    - Informações atualizadas
    - Notícias
    - Últimas novidades
    - O que há de novo
    """
    keywords = [
        "últimas",
        "recentes",
        "novidades",
        "notícias",
        "novo",
        "nova",
        "atualizado",
        "atual",
        "hoje",
        "agora",
        "2025",
        "2024",
    ]
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in keywords)


# ============================================
# Teste
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("Web Search Integration - ARIA")
    print("=" * 60)
    
    # Teste 1: Busca simples
    print("\n📝 Teste 1: Busca sobre WhatsApp API")
    query = "WhatsApp Business API 2025"
    result = search_web(query, max_results=3)
    
    if result["success"]:
        print(f"✅ Encontrados {result['count']} resultados")
        print(result["formatted_text"])
    else:
        print(f"❌ Erro: {result.get('error', 'Desconhecido')}")
    
    # Teste 2: Detecção de necessidade de web search
    print("\n" + "=" * 60)
    print("📝 Teste 2: Detecção de web search")
    
    test_phrases = [
        "Quais as últimas novidades sobre WhatsApp?",
        "Como funciona o sistema ARIA?",
        "Quero enviar mensagens",
        "Qual a notícia mais recente sobre API?",
    ]
    
    for phrase in test_phrases:
        should_search = should_use_web_search(phrase)
        icon = "🔍" if should_search else "📚"
        print(f"{icon} '{phrase}' → Web Search: {should_search}")
    
    print("\n" + "=" * 60)
    print("✅ Testes concluídos!")

