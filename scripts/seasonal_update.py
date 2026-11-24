"""CivilPrep: public-source monitoring and original, rule-based draft rotation.
No scraped questions, exam recollections, AI answer claims, or automatic factual edits.
"""
import argparse, collections, datetime as dt, hashlib, json, random, re, sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
PH = ZoneInfo('Asia/Manila')
SOURCES = {
    'CSC advisories': 'https://www.csc.gov.ph/examination-advisories',
    'CSC scope announcement': 'https://www.csc.gov.ph/examination-advisories/examination-announcement-no-06-s-2026-career-service-examination-pen-and-paper-test-for-professional-and-sub-professional-levels-14-march-2027',
    'Philippine Constitution': 'https://lawphil.net/consti/cons1987.html',
    'RA 6713': 'https://lawphil.net/statutes/repacts/ra1989/ra_6713_1989.html',
    'RA 9003': 'https://lawphil.net/statutes/repacts/ra2001/ra_9003_2001.html',
    'RA 8749': 'https://lawphil.net/statutes/repacts/ra1999/ra_8749_1999.html',
    'RA 9275': 'https://lawphil.net/statutes/repacts/ra2004/ra_9275_2004.html',
    'UDHR': 'https://www.un.org/en/about-us/universal-declaration-of-human-rights',
    'Independent topic guide: CSE PH': 'https://cse.ph/reviewers/cse/online-reviewer-quiz/',
    'Independent topic guide: CSE Pass': 'https://csepass.ph/civil-service-exam-reviewer',
}
TIERS = {'Easy', 'Moderate', 'Difficult'}
CATS = ['General Information','Clerical Skills','Numerical Skills','Abstract / Analytical Skills','Verbal Skills']

def read(path, default=None):
    p=ROOT/path
    return json.loads(p.read_text()) if p.exists() else default

def write(path, obj):
    p=ROOT/path; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')

def load_js(path):
    return json.loads((ROOT/path).read_text().split('=',1)[1].strip().rstrip(';'))

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.skip=0; self.text=[]; self.links=[]; self.href=None; self.label=[]
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style','noscript'): self.skip+=1
        if not self.skip and tag=='a': self.href=dict(attrs).get('href'); self.label=[]
    def handle_endtag(self,tag):
        if tag in ('script','style','noscript') and self.skip: self.skip-=1
        if tag=='a' and self.href is not None:
            self.links.append((self.href,' '.join(' '.join(self.label).split()))); self.href=None
    def handle_data(self,data):
        if not self.skip:
            self.text.append(data)
            if self.href is not None: self.label.append(data)

def fetch(url):
    with urlopen(Request(url,headers={'User-Agent':'CivilPrep-source-monitor/2.7 (public educational references)', 'Accept':'text/html,application/xhtml+xml', 'Accept-Language':'en-PH,en;q=0.8'}),timeout=15) as r:
        if r.status!=200: raise ValueError('HTTP '+str(r.status))
        if urlparse(r.url).hostname not in {urlparse(url).hostname, 'www.'+urlparse(url).hostname.removeprefix('www.'),urlparse(url).hostname.removeprefix('www.')}:
            raise ValueError('Unexpected redirect domain')
        if 'html' not in r.headers.get('Content-Type','').lower(): raise ValueError('Expected HTML')
        raw=r.read(2_000_001)
        if len(raw)>2_000_000: raise ValueError('Response too large')
        p=Page(); p.feed(raw.decode(r.headers.get_content_charset() or 'utf-8',errors='replace'))
        body=' '.join(' '.join(p.text).split())
        if len(body)<300 or re.search(r'^(just a moment|access denied|verify you are human)',body,re.I): raise ValueError('Empty or blocked page')
        return p,body

def csc_links(page):
    result={}
    for href,title in page.links:
        url=urljoin(SOURCES['CSC advisories'],href)
        u=urlparse(url)
        if u.scheme=='https' and u.hostname in ('csc.gov.ph','www.csc.gov.ph') and '/examination-advisories/' in u.path and re.search(r'career service examination|cse[- ]ppt|civil service examinations',title,re.I):
            result[u.path]={'title':title,'url':url}
    return sorted(result.values(),key=lambda x:x['url'])

def monitor(old):
    results=[]; links=old.get('advisories',[]); changed=[]
    previous={x['name']:x for x in old.get('sources',[])}
    for name,url in SOURCES.items():
        before=previous.get(name,{})
        try:
            used=url
            try:
                p,body=fetch(url)
            except Exception:
                if not name.startswith('CSC'): raise
                used=url.replace('https://www.csc.gov.ph/','https://csc.gov.ph/')
                if used==url: raise
                p,body=fetch(used)
            if name=='CSC advisories':
                found=csc_links(p)
                if not found: raise ValueError('No matching CSE advisory links; review parser')
                links=found
                body=json.dumps(found,sort_keys=True)
            digest=hashlib.sha256(body.encode()).hexdigest()
            if before.get('hash') and before['hash']!=digest: changed.append(name)
            results.append({'name':name,'url':url,'status':'checked','checkedUrl':used,'hash':digest,'lastSuccessfulCheck':NOW,'changeDetected':bool(before.get('changeDetected') or name in changed)})
        except Exception as exc:
            results.append({'name':name,'url':url,'status':'unavailable','errorType':type(exc).__name__,'httpStatus':getattr(exc,'code',None),'hash':before.get('hash'),'lastSuccessfulCheck':before.get('lastSuccessfulCheck'),'changeDetected':bool(before.get('changeDetected'))})
            print(f'{name}: {type(exc).__name__}',file=sys.stderr)
    return results,links,changed

def validate(bank):
    assert collections.Counter(q['category'] for q in bank)=={c:100 for c in CATS}, '500 base slots / 100 per subject required'
    allq=bank+[q['professionalVariant'] for q in bank if 'professionalVariant' in q]
    assert len({q['id'] for q in allq})==len(allq), 'duplicate ID'
    for q in allq:
        assert type(q['id']) is int and q['category'] in CATS and q['difficulty'] in TIERS
        assert isinstance(q['question'],str) and q['question'].strip() and q['explanation'].strip()
        assert len(q['choices'])==4 and len({c.strip().casefold() for c in q['choices']})==4 and all(c.strip() for c in q['choices'])
        assert type(q['answer']) is int and 0<=q['answer']<4
    return len(allq)

def candidates(bank,cycle):
    rng=random.Random('civilprep-season-'+cycle)
    highest=max(q['id'] for q in bank+[q['professionalVariant'] for q in bank if 'professionalVariant' in q]); out=[]
    used={q['question'] for q in bank}; scope=load_js('exam-config.js')['scopeDate']
    def add(old,question,options,correct,explanation,rule):
        assert question not in used and len(set(options))==4 and correct in options
        used.add(question); rng.shuffle(options)
        q={k:v for k,v in old.items() if k!='professionalVariant'}; q.pop('source',None)
        q.update(id=highest+len(out)+1,question=question,choices=options,answer=options.index(correct),explanation=explanation,scopeVersion=scope,origin='Original rule-based seasonal draft',reviewRule=rule)
        out.append({'replaceId':old['id'],'question':q})
    # Four categories; general information requires source-based editorial review.
    for cat in CATS[1:]:
        slots=[q for q in bank if q['category']==cat and q['difficulty']=='Moderate' and not q.get('professionalVariant')]
        # Rotate existing repetitive slots; deterministic per season, not an exam prediction.
        for old in rng.sample(slots,5):
            if cat=='Numerical Skills':
                while True:
                    total=rng.randrange(3,23)*400; a=rng.randrange(2,8)*5; b=rng.randrange(1,8)*5
                    # ensure integer cents, exact arithmetic
                    value=total*(100-a)*(100-b)//10000
                    text=f'A supplier lists an item at PHP {total:,}. Apply a {a}% discount, then {b}% off the reduced price. What is the final price in pesos?'
                    if text not in used:break
                assert value*10000==total*(100-a)*(100-b)
                add(old,text,[str(x) for x in [value,value+10,value+20,value-10]],str(value),f'{total} × {100-a}/100 × {100-b}/100 = {value} pesos.','Exact integer arithmetic')
            elif cat=='Clerical Skills':
                while True:
                    codes=rng.sample(range(10000,99999),4); order=sorted(codes); pos=rng.randrange(1,3); text=f'Arrange these record numbers in ascending order: {", ".join(map(str,codes))}. Which is number {pos+1} in the sorted list?'
                    if text not in used:break
                add(old,text,list(map(str,codes)),str(order[pos]),'Ascending order: '+', '.join(map(str,order))+'.','Numeric filing order')
            elif cat=='Abstract / Analytical Skills':
                while True:
                    start=rng.randrange(1,30); step=rng.randrange(2,14); growth=rng.randrange(2,12); seq=[start]
                    for i in range(4): seq.append(seq[-1]+step+i*growth)
                    text='Find the next number: '+', '.join(map(str,seq))+', ____.'
                    if text not in used:break
                val=seq[-1]+step+4*growth
                add(old,text,list(map(str,[val,val+growth,val-growth,val+1])),str(val),f'The successive differences are {", ".join(str(step+i*growth) for i in range(4))}. The next difference is {step+4*growth}, so the next term is {val}.','Increasing arithmetic differences')
            else:
                nouns=['reports','documents','forms','applications','records','notices','letters','files','receipts','requests','summaries','invoices']
                verbs=[('review','reviews'),('check','checks'),('inspect','inspects'),('sort','sorts'),('prepare','prepares'),('verify','verifies'),('file','files'),('update','updates')]
                while True:
                    noun=rng.choice(nouns); base,inf=rng.choice(verbs); text=f'Choose the correct present-tense verb: Each of the clerks ____ the {noun} every morning. (Verb: {base})'
                    if text not in used:break
                add(old,text,[base,inf,'are to '+base,'have to '+base],inf,f'The subject “Each” is singular, so the simple present verb is “{inf}”.','Subject–verb agreement (each)')
    return {'cycle':cycle,'createdAt':NOW,'status':'draft; owner approval required','notes':'Original practice templates, not questions collected from exam takers. General Information and all changed references require editorial review. Check language, difficulty and distractors before approving.','replacements':out}

def publish(bank,pack,cycle,status):
    if not pack or pack['cycle']!=cycle: raise ValueError('Approval must match the pending exam date')
    expected=candidates(bank,cycle)['replacements']
    # Regenerate from bank and seed; reject stale or modified packs rather than applying ambiguous edits.
    if pack['replacements']!=expected: raise ValueError('Draft differs from current deterministic candidates. Review/rebuild before approval.')
    lookup={r['replaceId']:r['question'] for r in expected}; new=[lookup.get(q['id'],q) for q in bank]
    validate(new)
    assert len(lookup)==20 and sum('professionalVariant' in q for q in new)==90
    oldtiers=collections.Counter((q['category'],q['difficulty']) for q in bank)
    assert oldtiers==collections.Counter((q['category'],q['difficulty']) for q in new)
    (ROOT/'questions.js').write_text('window.QUESTIONS='+json.dumps(new,ensure_ascii=False,indent=1)+';\n')
    version='2.7-'+cycle
    p=ROOT/'difficulty.js'; p.write_text(re.sub(r"const version='[^']+'",f"const version='{version}'",p.read_text(),count=1))
    p=ROOT/'sw.js'; p.write_text(re.sub(r"const CACHE='[^']+'",f"const CACHE='civilprep-shell-v{version}'",p.read_text(),count=1))
    status.setdefault('publishedCycles',[]).append(cycle); status['lastBankUpdate']=NOW; status['bankVersion']=version
    status['lastPublishedCount']=20; status['pendingCycle']=None
    (ROOT/'updates/candidates.json').unlink(missing_ok=True)
    return new

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--approve',default=''); parser.add_argument('--today',help='Test date YYYY-MM-DD; only use with --no-network'); parser.add_argument('--no-network',action='store_true'); parser.add_argument('--acknowledge-sources',action='store_true'); args=parser.parse_args()
    if args.today and not args.no_network: parser.error('--today requires --no-network')
    NOW=dt.datetime.now(PH).isoformat(timespec='seconds'); today=args.today or dt.datetime.now(PH).date().isoformat()
    dt.date.fromisoformat(today)
    status=read('updates/status.json',{}); bank=load_js('questions.js'); print('Validated records:',validate(bank)); config=load_js('exam-config.js')
    status['calendar']=[x['date'] for x in config['calendar']]; status['scopeDate']=config['scopeDate']
    if not args.no_network:
        status['sources'],status['advisories'],changed=monitor(status); status['lastMonitorRun']=NOW; status['lastRunChanges']=changed
    if args.approve:
        if not args.no_network and any(x['status']!='checked' or x.get('changeDetected') for x in status.get('sources',[]) if x['name'].startswith('CSC')):
            raise ValueError('Publication blocked: official CSC sources unavailable or changed. Review and resolve before approving.')
        bank=publish(bank,read('updates/candidates.json'),args.approve,status)
    pending=read('updates/candidates.json')
    if not pending:
        completed=sorted(d for d in status['calendar'] if d<today and d not in status.get('publishedCycles',[]))
        if completed:
            pending=candidates(bank,completed[0]); write('updates/candidates.json',pending)
    status['pendingCycle']=pending['cycle'] if pending else None
    status['candidateCount']=len(pending['replacements']) if pending else 0
    if args.acknowledge_sources:
        for source in status.get('sources',[]):
            if source['status']=='checked': source['changeDetected']=False
        status['lastSourceAcknowledgement']=NOW
    status['sourceReviewRequired']=any(x.get('changeDetected') for x in status.get('sources',[]))
    write('updates/status.json',status)
    print('Pending exam cycle:',status['pendingCycle'],'; bank:',status.get('bankVersion'))
