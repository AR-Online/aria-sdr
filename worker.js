// Cloudflare Worker para ARIA Endpoint
// Proxy que redireciona requisições para o webhook do n8n

export default {
  async fetch(request, env, ctx) {
    // URL do webhook da ARIA (pode também usar env.API_URL como variável)
    const target = "https://n8n-inovacao.ar-infra.com.br/webhook/assist/routing"

    // Encaminha a requisição original para o webhook
    const response = await fetch(target, {
      method: request.method,
      headers: request.headers,
      body: request.method !== "GET" ? await request.text() : undefined,
    })

    return new Response(await response.text(), {
      status: response.status,
      headers: response.headers,
    })
  }
}
