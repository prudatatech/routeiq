// Final Cloudflare Worker Script with CORS and Redirect Handling
const SUPABASE_URL = 'https://vqjmdzvjknhhdwpswvvh.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZxam1denZqa25oaGR3cHN3dnZoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ0Mzc1NTcsImV4cCI6MjA5MDAxMzU1N30.j8rC5a8U3E4a-15ekL5lqomfl4ghE9QXvHg9JApXpbE';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS, PATCH',
  'Access-Control-Allow-Headers': 'apikey, authorization, x-client-info, x-supabase-api-version, x-supabase-auth, content-type, range, if-none-match',
  'Access-Control-Expose-Headers': 'Content-Range, Content-Length, ETag, Location',
  'Access-Control-Max-Age': '86400',
};

async function handleRequest(request) {
  // Handle CORS preflight
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      status: 204,
      headers: corsHeaders
    });
  }

  const url = new URL(request.url);
  const proxyUrl = url.origin;
  const targetUrl = `${SUPABASE_URL}${url.pathname}${url.search}`;
  
  // Clone headers and prepare for Supabase
  const headers = new Headers(request.headers);
  
  // Default apikey if not provided
  if (!headers.get('apikey')) {
    headers.set('apikey', SUPABASE_ANON_KEY);
  }
  
  // REQUIRED: Host must match the real Supabase project
  headers.set('host', new URL(SUPABASE_URL).host);

  try {
    const response = await fetch(targetUrl, {
      method: request.method,
      headers: headers,
      body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined,
      redirect: 'manual'
    });

    let responseHeaders = new Headers(response.headers);
    
    // Inject CORS headers into the response
    Object.keys(corsHeaders).forEach(key => responseHeaders.set(key, corsHeaders[key]));

    // Handle Redirects (rewrite them to stay in the proxy)
    if ([301, 302, 303, 307, 308].includes(response.status)) {
      const location = responseHeaders.get('Location');
      if (location && location.startsWith(SUPABASE_URL)) {
        responseHeaders.set('Location', location.replace(SUPABASE_URL, proxyUrl));
      }
    }

    // Standard cleanup
    responseHeaders.delete('content-encoding');

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders
    });
    
  } catch (error) {
    return new Response(JSON.stringify({ 
      error: 'Proxy Error', 
      message: error.message 
    }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
        ...corsHeaders
      }
    });
  }
}

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});
