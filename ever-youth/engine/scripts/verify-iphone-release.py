"""Check the complete mobile release delta, including all 120 HTML routes."""
from pathlib import Path
from urllib.request import urlopen
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,time
root=Path(__file__).resolve().parents[1]
manifest={x['path']:x for x in json.loads((root/'releases/manifest.json').read_text(encoding='utf-8'))}
names=json.loads((root/'reports/iphone/changed-files.json').read_text(encoding='utf-8'))
def check(name):
 try:
  with urlopen('https://itvm.ru/ever-youth/'+name,timeout=30) as response:data=response.read();status=response.status
  return {'path':name,'status':status,'matches':hashlib.sha256(data).hexdigest()==manifest[name]['sha256']}
 except Exception as error:return {'path':name,'error':str(error),'matches':False}
with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(check,names))
for attempt in range(2):
 failed=[x['path'] for x in rows if not x['matches']]
 if not failed:break
 time.sleep(1)
 replacements={p:check(p) for p in failed};rows=[replacements.get(x['path'],x) for x in rows]
before=(root/'reports/iphone/root-before.sha256').read_text().strip()
root_same=hashlib.sha256(urlopen('https://itvm.ru/',timeout=30).read()).hexdigest()==before
report={'checked':len(rows),'htmlPages':sum(x['path'].endswith('.html') for x in rows),'matches':sum(x['matches'] for x in rows),'rootUnchanged':root_same,'failures':[x for x in rows if not x['matches']],'files':rows}
(root/'reports/iphone/deployment.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='files'}))
if report['failures'] or not root_same:raise SystemExit(1)
