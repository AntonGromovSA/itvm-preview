from pathlib import Path
import hashlib,json,zipfile
root=Path(__file__).resolve().parents[1];out=root/'dist';baseline=root.parent/'site';releases=root/'releases';releases.mkdir(exist_ok=True)
assert json.loads((root/'reports/verification.json').read_text()).get('vendorRuntimeRemoved') is True,'Run native pnpm verify before packaging'
manifest=[];changed=[]
for p in sorted(out.rglob('*')):
 if not p.is_file():continue
 name=p.relative_to(out).as_posix();sha=hashlib.sha256(p.read_bytes()).hexdigest();manifest.append({'path':name,'sha256':sha,'bytes':p.stat().st_size})
 old=baseline/name
 changed.append(p)
with zipfile.ZipFile(releases/'native-light-20261108.zip','w',zipfile.ZIP_DEFLATED) as archive:
 for p in changed:archive.write(p,p.relative_to(out).as_posix())
(releases/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
(releases/'changed-files.json').write_text(json.dumps([p.relative_to(out).as_posix() for p in changed],indent=2),encoding='utf8')
print(json.dumps({'files':len(changed),'total':len(manifest),'archive_bytes':(releases/'native-light-20261108.zip').stat().st_size}))
