import json, subprocess
from pathlib import Path
s=json.loads((Path(__file__).resolve().parents[1]/'updates/status.json').read_text())
def issue(title,body):
    r=subprocess.run(['gh','issue','list','--state','open','--limit','100','--json','title'],check=True,capture_output=True,text=True)
    if title not in [x['title'] for x in json.loads(r.stdout)]:
        subprocess.run(['gh','issue','create','--title',title,'--body',body],check=True)
if s.get('pendingCycle'):
    c=s['pendingCycle']; issue('CivilPrep: review questions after '+c,'Review `updates/candidates.json` (20 original draft items). Check every answer and difficulty. Also review General Information, current CSC coverage, laws and legitimate public topic guides. Never reuse recalled/live exam items. When satisfied, run the CivilPrep workflow with approve_cycle = '+c+'. Close this issue after publication. This does not validate the entire existing question bank.')
if s.get('sourceReviewRequired'):
    issue('CivilPrep: source changes need editorial review','Review flagged references in `updates/status.json`. A page hash change is not proof of a change in exam coverage or law. Confirm changes directly, revise exam-config.js and csc-guide.js or questions as necessary, then run the workflow with acknowledge_sources checked. Close this issue when resolved.')

missing=[x["name"] for x in s.get("sources",[]) if x["status"]!="checked" and x["name"].startswith("CSC")]
if missing:
    issue("CivilPrep: official source access needs attention", "The scheduled check could not reach: "+", ".join(missing)+". See updates/status.json for details. Verify the official CSC source manually; do not treat a failed check as a confirmed update.")
