// Bump cache version for every release, especially question-bank updates.
const CACHE='civilprep-shell-v2.6-seasonal';
const SHELL=['./','./index.html','./questions.js','./seasonal.js','./exam-config.js','./difficulty.js','./kpi.js','./kpi.css','./csc-guide.js','./csc-guide.css','./design-system.css','./mobile.css','./mobile.js','./mobile-config.js','./tabby.css','./tabby.js','./assets/tabby.webp','./manifest.webmanifest','./icons/icon-192.png','./icons/icon-512.png','./icons/maskable-512.png'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL))));
self.addEventListener('activate',e=>e.waitUntil((async()=>{for(const k of await caches.keys())if(k.startsWith('civilprep-shell-')&&k!==CACHE)await caches.delete(k);await self.clients.claim()})()));
self.addEventListener('message',e=>{if(e.data==='SKIP_WAITING')self.skipWaiting()});
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(e.request.method!=='GET'||u.origin!==self.location.origin||u.pathname.includes('/api/'))return;const allowed=SHELL.map(p=>new URL(p,self.registration.scope).pathname);if(e.request.mode==='navigate'){e.respondWith(caches.match(new URL('./index.html',self.registration.scope).href).then(r=>r||fetch(e.request)));return}if(allowed.includes(u.pathname))e.respondWith(caches.match(e.request,{ignoreSearch:true}).then(r=>r||fetch(e.request)));});
