"""Verify deployed public files against a packaged release; writes only local reports."""
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError
from concurrent.futures import ThreadPoolExecutor,as_completed
import json,hashlib,time
root=Path(__file__).resolve().parents[1]
manifest={x['path']:x for x in json.loads((root/'releases/manifest.json').read_text())}
names=json.loads((root/'releases/changed-files.json').read_text())
def check(name):
 try:
  with urlopen('https://itvm.ru/ever-youth/'+name+'?engine=20261108',timeout=35) as r:data=r.read();status=r.status
  return {'path':name,'status':status,'matches':hashlib.sha256(data).hexdigest()==manifest[name]['sha256']}
 except HTTPError as e:return {'path':name,'status':e.code,'matches':False}
 except Exception as e:return {'path':name,'error':type(e).__name__,'matches':False}
results=[]
with ThreadPoolExecutor(max_workers=12) as pool:
 jobs=[pool.submit(check,name) for name in names]
 for job in as_completed(jobs):
  results.append(job.result())
  if len(results)%25==0:print(json.dumps({'checked':len(results),'total':len(names)}),flush=True)
before=root/'reports/root-before.sha256';unchanged=None
if before.exists():
 try:unchanged=hashlib.sha256(urlopen('https://itvm.ru/',timeout=35).read()).hexdigest()==before.read_text().strip()
 except Exception:pass
report={'checked':len(results),'matches':sum(x['matches'] for x in results),'rootUnchanged':unchanged,'failures':[x for x in results if not x['matches']],'files':results}
(root/'reports/deployment.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='files'}),flush=True)
