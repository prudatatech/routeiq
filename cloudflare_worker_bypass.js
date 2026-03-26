// Reinforced Cloudflare Worker Script for Jio Bypass
const SUPABASE_URL = 'https://vqjmdzvjknhhdwpswvvh.supabase.co';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS, PATCH',
  'Access-Control-Allow-Headers': 'apikey, authorization, x-client-info, x-supabase-api-version, x-supabase-auth, content-type, range, if-none-match',
  'Access-Control-Expose-Headers': 'Content-Range, Content-Length, ETag, Location',
  'Access-Control-Max-Age': '86400',
};

async function handleRequest(request) {
  if (request.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers: corsHeaders });
  }

  const url = new URL(request.url);
  const proxyUrl = url.origin;
  const targetUrl = `${SUPABASE_URL}${url.pathname}${url.search}`;
  
  // Clone incoming headers
  const headers = new Headers(request.headers);
  
  // CRITICAL: Force the host header to match Supabase
  headers.set('host', new URL(SUPABASE_URL).host);

  try {
    const response = await fetch(targetUrl, {
      method: request.method,
      headers: headers,
      body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined,
      redirect: 'manual'
    });

    let responseHeaders = new Headers(response.headers);
    Object.keys(corsHeaders).forEach(key => responseHeaders.set(key, corsHeaders[key]));

    // Handle Auth Redirects (stay in proxy)
    if ([301, 302, 303, 307, 308].includes(response.status)) {
      const location = responseHeaders.get('Location');
      if (location && (location.startsWith(SUPABASE_URL) || location.startsWith('/'))) {
        const absoluteLocation = location.startsWith('/') ? `${SUPABASE_URL}${location}` : location;
        responseHeaders.set('Location', absoluteLocation.replace(SUPABASE_URL, proxyUrl));
      }
    }

    responseHeaders.delete('content-encoding');

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders
    });
    
  } catch (error) {
    return new Response(JSON.stringify({ 
      error: 'ISP Proxy Error', 
      message: error.message 
    }), {
      status: 502,
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });
  }
}

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});
