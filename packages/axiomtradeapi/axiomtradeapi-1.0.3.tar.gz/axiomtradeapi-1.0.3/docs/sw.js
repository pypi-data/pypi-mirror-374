// AxiomTradeAPI Documentation Service Worker
// Provides offline support and caching for better performance

const CACHE_NAME = 'axiomtradeapi-docs-v1';
const STATIC_CACHE_NAME = 'axiomtradeapi-static-v1';

// Files to cache for offline access
const STATIC_FILES = [
  '/',
  '/installation',
  '/trading-bots',
  '/websocket-guide',
  '/api-reference',
  '/assets/css/custom.css',
  '/assets/js/main.js',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
];

// Network-first strategy for dynamic content
const NETWORK_FIRST_PATHS = [
  '/api/',
  '/search',
  '/feedback'
];

// Cache-first strategy for static assets
const CACHE_FIRST_PATHS = [
  '/assets/',
  '/images/',
  'https://fonts.googleapis.com',
  'https://cdnjs.cloudflare.com'
];

// Install event - cache static files
self.addEventListener('install', event => {
  console.log('Service Worker: Installing...');
  
  event.waitUntil(
    Promise.all([
      caches.open(STATIC_CACHE_NAME).then(cache => {
        console.log('Service Worker: Caching static files');
        return cache.addAll(STATIC_FILES);
      })
    ])
  );
  
  // Skip waiting to activate immediately
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('Service Worker: Activating...');
  
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME && cacheName !== STATIC_CACHE_NAME) {
            console.log('Service Worker: Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  
  // Claim all clients immediately
  self.clients.claim();
});

// Fetch event - handle requests with different strategies
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  
  // Skip non-GET requests
  if (event.request.method !== 'GET') {
    return;
  }
  
  // Skip Chrome extension requests
  if (url.protocol === 'chrome-extension:') {
    return;
  }
  
  // Handle different types of requests
  if (shouldUseNetworkFirst(url)) {
    event.respondWith(networkFirstStrategy(event.request));
  } else if (shouldUseCacheFirst(url)) {
    event.respondWith(cacheFirstStrategy(event.request));
  } else {
    event.respondWith(staleWhileRevalidateStrategy(event.request));
  }
});

// Network-first strategy for dynamic content
async function networkFirstStrategy(request) {
  const cache = await caches.open(CACHE_NAME);
  
  try {
    // Try network first
    const networkResponse = await fetch(request);
    
    // Cache successful responses
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('Service Worker: Network failed, trying cache:', request.url);
    
    // Fallback to cache
    const cachedResponse = await cache.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline page for navigation requests
    if (request.mode === 'navigate') {
      return cache.match('/offline') || new Response('Offline', { status: 503 });
    }
    
    throw error;
  }
}

// Cache-first strategy for static assets
async function cacheFirstStrategy(request) {
  const cache = await caches.open(STATIC_CACHE_NAME);
  
  // Try cache first
  const cachedResponse = await cache.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    // Fallback to network
    const networkResponse = await fetch(request);
    
    // Cache successful responses
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('Service Worker: Failed to fetch:', request.url);
    throw error;
  }
}

// Stale-while-revalidate strategy for most content
async function staleWhileRevalidateStrategy(request) {
  const cache = await caches.open(CACHE_NAME);
  
  // Get from cache immediately
  const cachedResponse = await cache.match(request);
  
  // Fetch from network in background
  const fetchPromise = fetch(request).then(networkResponse => {
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  }).catch(error => {
    console.log('Service Worker: Background fetch failed:', request.url);
  });
  
  // Return cached version immediately, or wait for network if no cache
  return cachedResponse || fetchPromise;
}

// Helper functions to determine strategy
function shouldUseNetworkFirst(url) {
  return NETWORK_FIRST_PATHS.some(path => url.pathname.startsWith(path));
}

function shouldUseCacheFirst(url) {
  return CACHE_FIRST_PATHS.some(path => 
    url.pathname.startsWith(path) || url.origin.includes(path)
  );
}

// Handle background sync for offline form submissions
self.addEventListener('sync', event => {
  if (event.tag === 'feedback-sync') {
    event.waitUntil(syncFeedback());
  }
});

// Sync feedback when back online
async function syncFeedback() {
  const cache = await caches.open(CACHE_NAME);
  const requests = await cache.keys();
  
  for (const request of requests) {
    if (request.url.includes('/feedback-pending/')) {
      try {
        const response = await fetch(request);
        if (response.ok) {
          await cache.delete(request);
          console.log('Service Worker: Synced feedback:', request.url);
        }
      } catch (error) {
        console.log('Service Worker: Failed to sync feedback:', error);
      }
    }
  }
}

// Handle push notifications (if implemented)
self.addEventListener('push', event => {
  if (!event.data) return;
  
  const data = event.data.json();
  const options = {
    body: data.body,
    icon: '/assets/images/icon-192.png',
    badge: '/assets/images/badge-72.png',
    tag: 'axiomtradeapi-update',
    renotify: true,
    actions: [
      {
        action: 'view',
        title: 'View Update'
      },
      {
        action: 'dismiss',
        title: 'Dismiss'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', event => {
  event.notification.close();
  
  if (event.action === 'view') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Periodic background sync for cache updates
self.addEventListener('periodicsync', event => {
  if (event.tag === 'cache-update') {
    event.waitUntil(updateCache());
  }
});

// Update cache in background
async function updateCache() {
  const cache = await caches.open(STATIC_CACHE_NAME);
  
  try {
    await cache.addAll(STATIC_FILES);
    console.log('Service Worker: Cache updated in background');
  } catch (error) {
    console.log('Service Worker: Failed to update cache:', error);
  }
}

// Message handling for manual cache updates
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'UPDATE_CACHE') {
    event.waitUntil(updateCache());
  }
});

console.log('Service Worker: Loaded and ready!');
