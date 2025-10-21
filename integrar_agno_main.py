"""
Integração do Agno com o sistema ARIA atual
Adiciona Web Search ao endpoint de routing
"""

from agno.tools.duckduckgo import DuckDuckGoTools

# Criar ferramenta de web search uma única vez (reutilizar)
web_search = DuckDuckGoTools()

def search_web(query: str, max_results: int = 3) -> str:
    """
    Busca informações na web usando DuckDuckGo.
    
    Args:
        query: Texto para buscar
        max_results: Número máximo de resultados
    
    Returns:
        Texto formatado com os resultados
    """
    try:
        # Usar a ferramenta de busca
        results = web_search.search(query=query, max_results=max_results)
        
        if not results:
            return "Nenhum resultado encontrado."
        
        # Formatação dos resultados
        formatted_results = []
        for i, result in enumerate(results[:max_results], 1):
            title = result.get('title', 'Sem título')
            snippet = result.get('snippet', '')
            link = result.get('link', '')
            
            formatted = f"{i}. **{title}**\n"
            if snippet:
                formatted += f"   {snippet}\n"
            if link:
                formatted += f"   🔗 {link}\n"
            
            formatted_results.append(formatted)
        
        return "\n".join(formatted_results)
        
    except Exception as e:
        return f"Erro na busca: {str(e)}"


# Exemplo de uso
if __name__ == "__main__":
    print("Testando Web Search com DuckDuckGo")
    print("=" * 50)
    
    query = "WhatsApp Business API latest features 2025"
    print(f"\nBuscando: {query}\n")
    
    results = search_web(query, max_results=3)
    print(results)

