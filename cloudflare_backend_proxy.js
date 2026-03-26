// Smart Cloudflare Worker Script for Railway Backend Proxy
const BACKEND_URL = 'https://melodious-beauty-production-87b1.up.railway.app';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS, PATCH',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With, Accept',
  'Access-Control-Expose-Headers': '*',
  'Access-Control-Max-Age': '86400',
};

async function handleRequest(request) {
  if (request.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers: corsHeaders });
  }

  const url = new URL(request.url);
  let path = url.pathname;

  // SMART PATHING: Auto-prepend /api/v1 if missing (except for health checks)
  if (!path.startsWith('/api/v1') && path !== '/health' && path !== '/') {
    path = `/api/v1${path}`;
  }

  const targetUrl = `${BACKEND_URL}${path}${url.search}`;
  
  const headers = new Headers(request.headers);
  headers.set('host', new URL(BACKEND_URL).host);

  try {
    const response = await fetch(targetUrl, {
      method: request.method,
      headers: headers,
      body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined,
      redirect: 'follow'
    });

    let responseHeaders = new Headers(response.headers);
    Object.keys(corsHeaders).forEach(key => responseHeaders.set(key, corsHeaders[key]));
    responseHeaders.delete('content-encoding');

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders
    });
    
  } catch (error) {
    return new Response(JSON.stringify({ 
      error: 'Backend Proxy Error', 
      message: error.message,
      target: targetUrl 
    }), {
      status: 502,
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });
  }
}

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});
