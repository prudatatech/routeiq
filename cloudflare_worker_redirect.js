// Advanced Cloudflare Worker Script for Supabase Proxy with Redirect Handling
const SUPABASE_URL = 'https://vqjmdzvjknhhdwpswvvh.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZxam1denZqa25oaGR3cHN3dnZoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ0Mzc1NTcsImV4cCI6MjA5MDAxMzU1N30.j8rC5a8U3E4a-15ekL5lqomfl4ghE9QXvHg9JApXpbE';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS, PATCH',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, apikey, X-Client-Info, Range',
  'Access-Control-Expose-Headers': 'Content-Range, Content-Length, Location',
  'Access-Control-Max-Age': '86400',
};

async function handleRequest(request) {
  if (request.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers: corsHeaders });
  }

  const url = new URL(request.url);
  const proxyUrl = url.origin;
  const supabaseRequestUrl = `${SUPABASE_URL}${url.pathname}${url.search}`;
  
  const headers = new Headers(request.headers);
  
  // Set apikey if missing
  if (!headers.get('apikey')) {
    headers.set('apikey', SUPABASE_ANON_KEY);
  }
  
  // Necessary for Supabase to accept the Proxied request
  headers.set('host', new URL(SUPABASE_URL).host);

  try {
    const response = await fetch(supabaseRequestUrl, {
      method: request.method,
      headers: headers,
      body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined,
      redirect: 'manual' // Handle redirects manually to rewrite them
    });

    let responseHeaders = new Headers(response.headers);
    
    // Add CORS headers
    Object.keys(corsHeaders).forEach(key => responseHeaders.set(key, corsHeaders[key]));

    // REWRITE REDIRECTS: If Supabase sends a 301/302, point it back to the Proxy
    if ([301, 302, 303, 307, 308].includes(response.status)) {
      const location = responseHeaders.get('Location');
      if (location && location.startsWith(SUPABASE_URL)) {
        responseHeaders.set('Location', location.replace(SUPABASE_URL, proxyUrl));
      }
    }

    // Standard Cleanup
    responseHeaders.delete('content-encoding');

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders
    });
    
  } catch (error) {
    return new Response(JSON.stringify({ error: 'Proxy Error', message: error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });
  }
}

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});
