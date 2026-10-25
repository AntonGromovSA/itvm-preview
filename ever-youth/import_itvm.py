import sys, pathlib, json, re, hashlib, concurrent.futures, urllib.parse, time
sys.path.insert(0,str(pathlib.Path(__file__).parent/'vendor'))
from bs4 import BeautifulSoup
import requests
ROOT=pathlib.Path(__file__).parent
CACHE=ROOT/'source-itvm'
BASE='https://itvm.ru'
home=BeautifulSoup((CACHE/'index.html').read_text(encoding='utf-8-sig'),'html.parser')
def norm(u):
 p=urllib.parse.urlsplit(urllib.parse.urljoin(BASE,u))
 return p.path.rstrip('/') if p.netloc in ('itvm.ru','www.itvm.ru') and not p.query else None
links={}
for a in home.select('a[href]'):
 p=norm(a['href'])
 if p and not re.search(r'\.(jpg|png|pdf|mp4)$',p,re.I):links.setdefault(p,a.get_text(' ',strip=True))
allowed=['/konsultatsii-spetsialistov','/uslugi','/metody-lecheniya','/programmy','/o-nas','/o-klinike','/kontakty','/price-list','/spa','/salon-krasoty','/zabolevaniya']
paths=[p for p in links if any(p==a or p.startswith(a+'/') for a in allowed)]
def fetch(p):
 fn=CACHE/(hashlib.sha256(p.encode()).hexdigest()[:16]+'.html')
 try:
  if fn.exists(): raw=fn.read_text(encoding='utf8')
  else:
   r=requests.get(BASE+p,timeout=22);r.raise_for_status();raw=r.content.decode('utf-8-sig');fn.write_text(raw,encoding='utf8')
  soup=BeautifulSoup(raw,'html.parser'); h=soup.select_one('h1');content=soup.select_one('#Content')
  if not content:return {'path':p,'error':'no_content','title':links[p]}
  return {'path':p,'title':h.get_text(' ',strip=True) if h else links[p], 'content':str(content),'source':BASE+p}
 except Exception as e:return {'path':p,'error':type(e).__name__,'title':links[p]}
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
 for i,row in enumerate(ex.map(fetch,paths),1):
  results.append(row)
  if i%25==0: print('Fetched',i,'/',len(paths),flush=True)
# Card metadata on the homepage supplies specializations and portrait images.
doctors=[]
first=home.select_one('a[href="/konsultatsii-spetsialistov/glavnyy-vrach"]')
for a in first.parent.parent.select('a[href]'):
 p=norm(a['href']);name=a.get_text(' ',strip=True);meta={'path':p,'name':name}
 for candidate in home.select(f'a[href="{p}"]'):
  for parent in list(candidate.parents)[:3]:
   image=parent.select_one('img')
   txt=parent.get_text(' ',strip=True)
   if image and len(txt)<1700:
    meta['image']=urllib.parse.urljoin(BASE,image.get('src',''))
    meta['subtitle']=txt.replace(name,'').replace('Подробнее','').strip();break
  if meta.get('image'):break
 doctors.append(meta)
(ROOT/'itvm-data.json').write_text(json.dumps({'pages':results,'doctors':doctors,'links':links,'imported_at':'2026-10-26'},ensure_ascii=False,indent=2),encoding='utf8')
print('DONE',len(results),'errors',[(x['path'],x['error']) for x in results if 'error' in x],flush=True)
print('Doctor cards',len(doctors),'photos',sum(bool(x.get('image')) for x in doctors))
