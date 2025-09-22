// Alias para compatibilidade - proxy para o webhook do n8n
export async function onRequest(context) {
  const { request } = context;

  // Configuração de CORS
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  };

  // Handle preflight requests
  if (request.method === 'OPTIONS') {
    return new Response(null, { status: 200, headers: corsHeaders });
  }

  try {
    // URL do webhook da ARIA
    const target = "https://n8n-inovacao.ar-infra.com.br/webhook/assist/routing";

    // Encaminha a requisição original para o webhook
    const response = await fetch(target, {
      method: request.method,
      headers: request.headers,
      body: request.method !== "GET" ? await request.text() : undefined,
    });

    return new Response(await response.text(), {
      status: response.status,
      headers: {
        ...corsHeaders,
        ...Object.fromEntries(response.headers.entries())
      },
    });

  } catch (error) {
    console.error('Erro no proxy:', error);
    return new Response(JSON.stringify({
      error: 'Proxy error',
      message: error.message,
      target: 'https://n8n-inovacao.ar-infra.com.br/webhook/assist/routing'
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
}
