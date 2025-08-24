// Crypto Tracker PWA Service Worker
const CACHE_NAME = 'crypto-tracker-v1';
const API_CACHE_NAME = 'crypto-tracker-api-v1';

// Assets to cache for offline functionality
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png',
  // Vite will generate these, so we'll cache them dynamically
];

// API endpoints to cache
const API_ENDPOINTS = [
  '/portfolio',
  '/live_profit_loss', 
  '/daily_profit_loss',
  '/transactions',
  '/portfolio_history',
  '/current_prices'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('🔧 Service Worker: Installing...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('📦 Service Worker: Caching static assets');
        // Cache the basic HTML - other assets will be cached dynamically
        return cache.addAll([
          '/',
          '/manifest.json'
        ]);
      })
      .then(() => {
        console.log('✅ Service Worker: Installation complete');
        // Force activation of new service worker
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('❌ Service Worker: Installation failed', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('🚀 Service Worker: Activating...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            // Delete old cache versions
            if (cacheName !== CACHE_NAME && cacheName !== API_CACHE_NAME) {
              console.log('🗑️ Service Worker: Deleting old cache', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('✅ Service Worker: Activation complete');
        // Take control of all pages
        return self.clients.claim();
      })
  );
});

// Fetch event - handle network requests with caching strategy
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Handle different types of requests
  if (url.origin === location.origin) {
    // Same-origin requests (app assets)
    event.respondWith(handleAppRequest(request));
  } else if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
    // API requests to backend
    event.respondWith(handleApiRequest(request));
  } else {
    // External requests (CoinGecko API, etc.)
    event.respondWith(handleExternalRequest(request));
  }
});

// Handle app asset requests (HTML, JS, CSS, images)
async function handleAppRequest(request) {
  const url = new URL(request.url);
  
  try {
    // For navigation requests, try network first, fallback to cache
    if (request.mode === 'navigate') {
      try {
        const networkResponse = await fetch(request);
        const cache = await caches.open(CACHE_NAME);
        cache.put(request, networkResponse.clone());
        return networkResponse;
      } catch (error) {
        // Offline - serve cached version
        const cachedResponse = await caches.match('/');
        if (cachedResponse) {
          return cachedResponse;
        }
        // Last resort - return offline page
        return new Response('Offline - Please check your connection', {
          status: 503,
          headers: { 'Content-Type': 'text/plain' }
        });
      }
    }
    
    // For other assets, try cache first, then network
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    const networkResponse = await fetch(request);
    
    // Cache successful responses
    if (networkResponse.status === 200) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
    
  } catch (error) {
    console.log('🔄 Service Worker: Network failed for', request.url);
    
    // Try to serve from cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return error response
    return new Response('Resource not available offline', {
      status: 503,
      headers: { 'Content-Type': 'text/plain' }
    });
  }
}

// Handle API requests to backend
async function handleApiRequest(request) {
  const url = new URL(request.url);
  const pathname = url.pathname;
  
  try {
    // Try network first
    const networkResponse = await fetch(request);
    
    // Cache successful GET requests
    if (request.method === 'GET' && networkResponse.status === 200) {
      const cache = await caches.open(API_CACHE_NAME);
      
      // Add timestamp to cached data
      const responseData = await networkResponse.json();
      const cachedData = {
        data: responseData,
        cached_at: new Date().toISOString(),
        offline: false
      };
      
      const modifiedResponse = new Response(JSON.stringify(cachedData), {
        status: networkResponse.status,
        statusText: networkResponse.statusText,
        headers: {
          'Content-Type': 'application/json',
          'Cache-Control': 'max-age=300' // 5 minutes
        }
      });
      
      cache.put(request, modifiedResponse.clone());
      
      // Return original response to the app
      return new Response(JSON.stringify(responseData), {
        status: networkResponse.status,
        statusText: networkResponse.statusText,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    return networkResponse;
    
  } catch (error) {
    console.log('📡 Service Worker: API request failed, trying cache for', pathname);
    
    // Network failed - try cache for GET requests
    if (request.method === 'GET') {
      const cachedResponse = await caches.match(request);
      if (cachedResponse) {
        const cachedData = await cachedResponse.json();
        
        // Add offline indicator to cached data
        const offlineData = {
          ...cachedData.data,
          _offline: true,
          _cached_at: cachedData.cached_at
        };
        
        return new Response(JSON.stringify(offlineData), {
          status: 200,
          headers: { 
            'Content-Type': 'application/json',
            'X-Served-From': 'cache'
          }
        });
      }
    }
    
    // No cache available - return error
    return new Response(JSON.stringify({
      error: 'Offline - no cached data available',
      offline: true
    }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// Handle external API requests (CoinGecko, etc.)
async function handleExternalRequest(request) {
  try {
    // Try network with timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
    
    const networkResponse = await fetch(request, {
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    // Cache successful responses
    if (networkResponse.status === 200) {
      const cache = await caches.open(API_CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
    
  } catch (error) {
    // Try cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return error
    return new Response(JSON.stringify({
      error: 'External service unavailable',
      offline: true
    }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// Background sync for when connection returns
self.addEventListener('sync', (event) => {
  if (event.tag === 'portfolio-sync') {
    console.log('🔄 Service Worker: Background sync triggered');
    event.waitUntil(syncPortfolioData());
  }
});

// Sync portfolio data when connection returns
async function syncPortfolioData() {
  try {
    // Clear old cache
    const cache = await caches.open(API_CACHE_NAME);
    await cache.delete('/portfolio');
    await cache.delete('/live_profit_loss');
    await cache.delete('/current_prices');
    
    // Fetch fresh data
    await fetch('/portfolio');
    await fetch('/live_profit_loss');
    await fetch('/current_prices');
    
    console.log('✅ Service Worker: Portfolio data synced');
  } catch (error) {
    console.error('❌ Service Worker: Sync failed', error);
  }
}

// Handle messages from the main app
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'CACHE_PORTFOLIO') {
    // Force cache refresh
    caches.open(API_CACHE_NAME).then(cache => {
      cache.delete('/portfolio');
      fetch('/portfolio');
    });
  }
});

console.log('🎯 Service Worker: Loaded successfully');