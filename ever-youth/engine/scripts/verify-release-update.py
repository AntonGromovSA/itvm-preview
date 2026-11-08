"""Recheck a follow-up release and retry previous transient failures."""
from pathlib import Path
from urllib.request import urlopen
from concurrent.futures import ThreadPoolExecutor
import json,hashlib
root=Path(__file__).resolve().parents[1]
report=json.loads((root/'reports/deployment.json').read_text())
before={x['path']:x['sha256'] for x in json.loads((root/'reports/first-restoration-manifest.json').read_text())}
manifest={x['path']:x for x in json.loads((root/'releases/manifest.json').read_text())}
names=sorted({x['path'] for x in report['failures']}|{p for p,x in manifest.items() if before.get(p)!=x['sha256']})
def check(name):
 try:
  with urlopen('https://itvm.ru/ever-youth/'+name,timeout=25) as response:data=response.read();status=response.status
  return {'path':name,'status':status,'matches':hashlib.sha256(data).hexdigest()==manifest[name]['sha256']}
 except Exception as error:return {'path':name,'error':str(error),'matches':False}
with ThreadPoolExecutor(max_workers=6) as pool:updates=list(pool.map(check,names))
files={x['path']:x for x in report['files']};files.update({x['path']:x for x in updates})
report.update(files=list(files.values()),matches=sum(x['matches'] is True for x in files.values()),failures=[x for x in files.values() if x['matches'] is False],followupChecked=len(updates))
(root/'reports/deployment.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='files'}))
