// Editorial practice difficulty, not official CSC weighting or calibrated item difficulty.
window.CP_DIFFICULTY=(()=>{
 const version='2.5', tiers=['Easy','Moderate','Difficult'];
 const weights={Professional:[20,50,30],Subprofessional:[50,40,10]};
 function pool(level,questions,config){return questions.filter(q=>config.levels[level].includes(q.category)).map(q=>{let {professionalVariant,...base}=q;return level==='Professional'&&professionalVariant?professionalVariant:base})}
 function shuffle(a){a=[...a];for(let i=a.length-1;i>0;i--){let j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a}
 function sample(rows,n,level){n=Math.max(0,Math.min(rows.length,Math.floor(Number(n)||0)));let exact=weights[level].map(w=>n*w/100),quotas=exact.map(Math.floor);let order=tiers.map((_,i)=>i).sort((a,b)=>(exact[b]-quotas[b])-(exact[a]-quotas[a]));let remainder=n-quotas.reduce((a,b)=>a+b,0);for(let i=0;i<remainder;i++)quotas[order[i]]++;let selected=tiers.flatMap((tier,i)=>shuffle(rows.filter(q=>q.difficulty===tier)).slice(0,quotas[i]));if(selected.length<n){let ids=new Set(selected.map(q=>q.id));selected.push(...shuffle(rows.filter(q=>!ids.has(q.id))).slice(0,n-selected.length))}return shuffle(selected)}
 return {version,tiers,weights,pool,sample};
})();
