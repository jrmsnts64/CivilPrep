(()=>{
  const host=document.createElement('div'); host.id='tabby-host'; host.hidden=true;
  host.innerHTML=`<div id="tabby-greeting" hidden><img class="tabby-art" src="assets/tabby.webp" alt="Tabby, a smiling cat wearing a graduation cap and raising a paw"><div class="tabby-copy" role="status" aria-live="polite"><div class="tabby-label">Your study buddy</div><strong>Hi! I’m Tabby! 👋</strong><p id="tabby-message">Ready to review? Let’s learn together!</p></div><button type="button" id="tabby-close" aria-label="Dismiss Tabby's greeting">×</button></div><button type="button" id="tabby-replay" aria-label="Say hi to Tabby" hidden><img src="assets/tabby.webp" alt="">Say hi to Tabby</button>`;
  document.body.append(host);
  const card=document.getElementById('tabby-greeting'),replay=document.getElementById('tabby-replay'),message=document.getElementById('tabby-message');
  const phrases=['Ready to review? Let’s learn together!','Welcome back! One question at a time.','Hi, future civil servant! Enjoy your review.'];
  let greeted=false,launch=0,hideTimer=0,exitTimer=0,shown=false;
  const eligible=()=>page==='Dashboard'&&!document.querySelector('dialog[open]');
  function stop(){clearTimeout(hideTimer);clearTimeout(exitTimer);card.hidden=true;card.className='';shown=false;}
  function dismiss(){clearTimeout(hideTimer);if(!shown)return;shown=false;card.className='leave';exitTimer=setTimeout(()=>{card.hidden=true;card.className='';replay.hidden=!eligible()},360)}
  function show(){if(!eligible())return;stop();greeted=true;shown=true;host.hidden=false;replay.hidden=true;message.textContent=phrases[Math.floor(Math.random()*phrases.length)];card.hidden=false;card.className='enter';hideTimer=setTimeout(dismiss,8500)}
  function sync(){if(!eligible()){clearTimeout(launch);launch=0;stop();host.hidden=true;replay.hidden=true;return}host.hidden=false;if(!greeted&&!launch){launch=setTimeout(()=>{launch=0;show()},900)}else if(greeted&&!shown&&card.hidden){replay.hidden=false}}
  replay.addEventListener('click',show);document.getElementById('tabby-close').addEventListener('click',dismiss);
  new MutationObserver(sync).observe(document.getElementById('heading'),{childList:true,subtree:true});
  document.querySelectorAll('dialog').forEach(d=>new MutationObserver(sync).observe(d,{attributes:true,attributeFilter:['open']}));
  sync();
})();
