from pathlib import Path
import hashlib,json,zipfile
root=Path(__file__).resolve().parents[1];out=root/'dist';baseline=root.parent/'site';releases=root/'releases';releases.mkdir(exist_ok=True)
assert (root/'reports/verification.json').exists(),'Run pnpm verify before packaging'
manifest=[];changed=[]
for p in sorted(out.rglob('*')):
 if not p.is_file():continue
 name=p.relative_to(out).as_posix();sha=hashlib.sha256(p.read_bytes()).hexdigest();manifest.append({'path':name,'sha256':sha,'bytes':p.stat().st_size})
 old=baseline/name
 if not old.is_file() or hashlib.sha256(old.read_bytes()).hexdigest()!=sha:changed.append(p)
with zipfile.ZipFile(releases/'astro-migration-20261108.zip','w',zipfile.ZIP_DEFLATED) as archive:
 for p in changed:archive.write(p,p.relative_to(out).as_posix())
(releases/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
(releases/'changed-files.json').write_text(json.dumps([p.relative_to(out).as_posix() for p in changed],indent=2),encoding='utf8')
print(json.dumps({'changed':len(changed),'total':len(manifest),'archive_bytes':(releases/'astro-migration-20261108.zip').stat().st_size}))
