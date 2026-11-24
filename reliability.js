/* Report links open a draft only. No personal data is collected. */
let qualityStatus=null;
async function qualityCheck(){
  try{const r=await fetch(new URL('updates/quality.json',document.baseURI),{cache:'no-store'});if(!r.ok)throw Error();const d=await r.json();if(!Number.isInteger(d.records)||!Number.isInteger(d.mathChecked)||!Number.isInteger(d.numericalRecords))throw Error();qualityStatus=d;}catch{qualityStatus=null;}
}
function questionReport(q){
  const u=new URL('https://github.com/jrmsnts64/CivilPrep/issues/new');
  u.searchParams.set('title','Question review requested: '+q.id);
  u.searchParams.set('body','Question ID: '+q.id+'\nQuestion bank: '+CP_DIFFICULTY.version+'\nCategory: '+q.category+'\nQuestion: '+q.question+'\nIssue or suggested correction: \nReference (if available): \n\nPlease do not include personal details.');
  return `<div class="reliability-report"><a href="${escapeHTML(u.href)}" target="_blank" rel="noopener noreferrer">Report a question ↗</a><small>Opens a public GitHub issue draft. Sign-in required. Do not share personal information.</small></div>`;
}
function qualityPanel(){
 const d=qualityStatus;
 return `<section class="panel reliability-panel"><h3>Question quality checks</h3><p class="muted">Automated checks are not independent editorial certification.</p>${d?`<div class="quality-grid"><div><small>Records checked</small><strong>${d.records}</strong></div><div><small>Numerical answers checked</small><strong>${d.mathChecked}/${d.numericalRecords}</strong></div><div><small>Exact duplicates</small><strong>${Number(d.exactDuplicates)}</strong></div><div><small>Repeated template groups</small><strong>${Number(d.repeatedTemplateGroups)}</strong></div></div><p class="muted">Audit: ${escapeHTML(d.checkedAt||'Unknown date')} · Editorial review pending</p>`:'<p>Audit report unavailable. Try refreshing while online.</p>'}<button class="secondary" onclick="checkCSC(true)">Refresh checks</button></section>`;
}
