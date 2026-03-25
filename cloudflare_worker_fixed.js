// Cloudflare Worker Script (Fixed Version)
const SUPABASE_URL = 'https://vqjmdzvjknhhdwpswvvh.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZxam1denZqa25oaGR3cHN3dnZoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ0Mzc1NTcsImV4cCI6MjA5MDAxMzU1N30.j8rC5a8U3E4a-15ekL5lqomfl4ghE9QXvHg9JApXpbE';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS, PATCH',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, apikey, X-Client-Info',
  'Access-Control-Expose-Headers': '*',
  'Access-Control-Max-Age': '86400',
};

async function handleRequest(request) {
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      status: 204,
      headers: corsHeaders
    });
  }

  const url = new URL(request.url);
  const supabaseRequestUrl = `${SUPABASE_URL}${url.pathname}${url.search}`;
  
  // Clone the headers
  const headers = new Headers(request.headers);
  
  // FIXED: Only set apikey if not already provided by the requester (like the backend)
  if (!headers.get('apikey')) {
    headers.set('apikey', SUPABASE_ANON_KEY);
  }
  
  // Ensure we are talking to the correct project host
  headers.set('host', new URL(SUPABASE_URL).host);

  const supabaseRequest = new Request(supabaseRequestUrl, {
    method: request.method,
    headers: headers,
    body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined,
    redirect: 'follow'
  });

  try {
    const response = await fetch(supabaseRequest);
    const responseHeaders = new Headers(response.headers);
    
    // Merge CORS headers
    Object.keys(corsHeaders).forEach(key => {
      responseHeaders.set(key, corsHeaders[key]);
    });
    
    // Remove headers that Cloudflare might complain about
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
