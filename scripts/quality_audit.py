"""Structural validation, independent arithmetic checks and source inventory. Not editorial certification."""
import collections, json, re, unicodedata
from fractions import Fraction as F
from pathlib import Path
from urllib.parse import urlparse
from seasonal_update import ROOT, CATS, validate, load_js

def norm(s):
    return ' '.join(unicodedata.normalize('NFKC',s).casefold().split())

def numeric(q):
    s=q['question']; n=lambda x:F(x.replace(',',''))
    patterns=[
      (r'What is (\d+)% of (\d+)\?',lambda a,b:b*a/100),
      (r'A vehicle travels (\d+) km in (\d+) hours\. Find its average speed\.',lambda a,b:a/b),
      (r'The ratio of red to blue pens is (\d+):(\d+)\. If there are (\d+) red pens, how many blue pens are there\?',lambda a,b,c:c*b/a),
      (r'Find the average of (\d+), (\d+), and (\d+)\.',lambda a,b,c:(a+b+c)/3),
      (r'An item costs ₱(\d+)\. After a (\d+)% discount, what is the new price\?',lambda a,b:a*(100-b)/100),
      (r'A supply order costs ₱(\d+)\. A (\d+)% discount is applied, then a ₱(\d+) delivery fee is added\. What is the total in pesos\?',lambda a,b,c:a*(100-b)/100+c),
      (r'The ratio of filed to pending records is (\d+):(\d+)\. If (\d+) records are filed and (\d+) more become pending, how many are pending now\?',lambda a,b,c,d:c*b/a+d),
      (r'A clerk processes (\d+) forms in (\d+) hours\. Another clerk processes (\d+) more forms per hour\. What is the second clerk’s hourly rate\?',lambda a,b,c:a/b+c),
      (r'Find the missing term: (\d+), (\d+), (\d+), ___, where the next increment is three times the first increment\.',lambda a,b,c:c+3*(b-a)),
      (r'A ₱(\d+) item is discounted by (\d+)%, then by (\d+)% of the reduced price\. What is the final price in pesos\?',lambda a,b,c:a*(100-b)*(100-c)/10000),
      (r'An office processes one-third of (\d+) forms in the morning and one-fourth of the original total in the afternoon\. How many remain unprocessed\?',lambda a:a*(1-F(1,3)-F(1,4))),
      (r'A vehicle travels (\d+) km at (\d+) km/h and returns at (\d+) km/h\. How many minutes does the entire round trip take\?',lambda a,b,c:60*(a/b+a/c)),
      (r'Four employees average (\d+) processed files\. A fifth employee processes (\d+) files\. What is the new average\?',lambda a,b:(4*a+b)/5),
      (r'A budget of ₱(\d+) is allocated (\d+)% to supplies\. Of the remainder, ₱(\d+) is used for transport\. How many pesos remain\?',lambda a,b,c:a*(100-b)/100-c),
      (r'An office receives (\d+) forms\. One-third is incomplete\. After (\d+) additional complete forms arrive, how many complete forms are there\?',lambda a,b:a*F(2,3)+b),
      (r'A supplier lists an item at PHP ([\d,]+)\. Apply a (\d+)% discount, then (\d+)% off the reduced price\. What is the final price in pesos\?',lambda a,b,c:a*(100-b)*(100-c)/10000),
    ]
    special={
      'A tank is 3/5 full. After 24 liters are added, it is 9/10 full. What is its total capacity in liters?': F(24)/(F(9,10)-F(3,5)),
      'A worker completes a task in 6 hours. Another completes the same task in 12 hours. At constant rates, how long will they take together?':1/(F(1,6)+F(1,12)),
      'A mother is 36 years old and her child is 12. In how many years will the mother be twice as old as her child?':F(36-2*12),
      'A vehicle travels 60 km at 30 km/h and another 60 km at 60 km/h. What is its average speed for the entire trip?':F(120)/(F(60,30)+F(60,60)),
      'Find the next number if the operations alternate between multiplying by 2 and adding 3: 4, 8, 11, 22, 25, ___.':F(25*2),
    }
    expected=special.get(s)
    if expected is None:
        for p,fn in patterns:
            m=re.fullmatch(p,s)
            if m: expected=fn(*map(n,m.groups()));break
    if expected is None:return None
    def option(c):
        m=re.fullmatch(r'₱?([\d,]+(?:\.\d+)?)(?: km/h| hours)?',c)
        return n(m[1]) if m else None
    options=list(map(option,q['choices']))
    if options.count(expected)!=1 or options[q['answer']]!=expected:
        raise ValueError(f"Question {q['id']}: arithmetic mismatch; expected {expected}")
    return True

def audit(bank):
    validate(bank)
    if sum('professionalVariant' in q for q in bank)!=90: raise ValueError('Expected 90 level variants')
    allq=bank+[q['professionalVariant'] for q in bank if 'professionalVariant' in q]
    seen={}; math_checked=0; sources=set(); templates=collections.Counter()
    for q in allq:
        key=(norm(q['question']),tuple(sorted(map(norm,q['choices']))))
        if key in seen:raise ValueError(f"Exact duplicate items {seen[key]} and {q['id']}")
        seen[key]=q['id']
        if 'professionalVariant' in q and q['professionalVariant']['category']!=q['category']:raise ValueError('Variant category mismatch')
        if q['category']=='General Information':
            u=urlparse(q.get('source',''))
            if u.scheme!='https' or u.hostname not in {'lawphil.net','www.lawphil.net','www.un.org','un.org','csc.gov.ph','www.csc.gov.ph'}:raise ValueError(f"Invalid factual reference: {q['id']}")
            sources.add(q['source'])
        if q['category']=='Numerical Skills' and numeric(q):math_checked+=1
        templates[re.sub(r'\d+(?:[,.]\d+)*','#',norm(q['question']))]+=1
    return dict(baseQuestions=len(bank),professionalVariants=90,records=len(allq),exactDuplicates=0,mathChecked=math_checked,numericalRecords=sum(q['category']=='Numerical Skills' for q in allq),factualReferences=len(sources),repeatedTemplateGroups=sum(v>1 for v in templates.values()),editorialReview='pending',note='Structural checks and covered arithmetic only; reference links and question templates are not independent content validation.')

if __name__=='__main__':
    import argparse, datetime
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args()
    result=audit(load_js('questions.js')); print(json.dumps(result,indent=2))
    if args.write:
        result['checkedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
        (ROOT/'updates/quality.json').write_text(json.dumps(result,indent=2)+'\n')
