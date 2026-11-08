"""One-time import of the approved HTML snapshot; normal builds do not run this."""
from pathlib import Path
import argparse,sys,json,re,hashlib,shutil
parser=argparse.ArgumentParser();parser.add_argument('--source',required=True);parser.add_argument('--vendor');args=parser.parse_args()
if args.vendor:sys.path.insert(0,args.vendor)
from bs4 import BeautifulSoup, Comment
ENGINE=Path(__file__).resolve().parents[1];SOURCE=Path(args.source)
for name in ('src/content/pages','src/content/blocks','src/content/texts','src/content/shared','src/data','public','reports'):(ENGINE/name).mkdir(parents=True,exist_ok=True)
def write_json(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')
contacts={'name':'ИТВМ Арбат','address':'Москва, Филипповский переулок, 18','phones':[{'display':'+7 (495) 646-07-73','e164':'+74956460773'},{'display':'+7 (495) 691-66-12','e164':'+74956916612'},{'display':'+7 (495) 691-66-72','e164':'+74956916672'}],'whatsapp':{'display':'+7 (917) 525-36-95','e164':'+79175253695','url':'https://wa.me/79175253695'},'vk':'https://vk.com/itvm_arbat'}
write_json(ENGINE/'src/data/clinic.json',contacts)
catalog=json.loads((SOURCE/'price-catalog.json').read_text(encoding='utf8'));write_json(ENGINE/'src/data/prices.json',catalog)
specialists=ENGINE.parent/'price-update/doctors-source.json'
if specialists.exists():shutil.copy2(specialists,ENGINE/'src/data/specialists.json')
def tokenize(raw):
 for i,p in enumerate(contacts['phones']):
  raw=raw.replace(p['display'],f'__CLINIC_PHONE_{i}_DISPLAY__').replace(p['e164'],f'__CLINIC_PHONE_{i}_E164__')
 raw=raw.replace(contacts['whatsapp']['url'],'__CLINIC_WHATSAPP_URL__').replace(contacts['whatsapp']['display'],'__CLINIC_WHATSAPP_DISPLAY__').replace(contacts['vk'],'__CLINIC_VK_URL__')
 raw=re.sub(r'var catalog = \[.*?\];(?=\s*var catalogNode)', 'var catalog = __CLINIC_PRICE_CATALOG__;',raw,flags=re.S)
 return raw
shared={};pages=[];field_count=0
for source in sorted(SOURCE.glob('*.html')):
 s=BeautifulSoup(source.read_text(encoding='utf8'),'html.parser');stem=source.stem;texts={}
 record=s.select_one('#allrecords');blocks=[]
 def fragment(raw,label):
  path=f'src/content/blocks/{stem}--{label}.html';(ENGINE/path).write_text(tokenize(raw),encoding='utf8');return path
 def lift(el):
  global field_count
  for atom in el.select('.tn-atom[field^="tn_text_"]'):
   if atom.select_one('script,video,img,iframe,svg'):continue
   key=atom['field'];value=atom.decode_contents()
   if key in texts and texts[key]!=value:key+='-'+hashlib.sha256(value.encode()).hexdigest()[:8]
   texts[key]=tokenize(value);atom.clear();atom.append('__CLINIC_TEXT_'+key+'__');field_count+=1
 if record:
  marker='__CLINIC_RECORDS_ROOT__';record_html=str(record);body=s.body.decode_contents();before,after=body.split(record_html,1)
  for i,child in enumerate(list(record.children)):
   if not getattr(child,'name',None):
    if str(child).strip():blocks.append({'kind':'legacy','id':f'note-{i}','file':fragment('<!--'+str(child)+'-->' if isinstance(child,Comment) else str(child),f'note-{i}')})
    continue
   identifier=child.get('id',f'block-{i}')
   if identifier in ('t-header','t-footer'):
    kind='header' if identifier=='t-header' else 'footer';raw=tokenize(str(child));key=hashlib.sha256(raw.encode()).hexdigest()[:10];name=f'src/content/shared/{kind}-{key}.html'
    (ENGINE/name).write_text(raw,encoding='utf8');shared.setdefault(kind,set()).add(name);blocks.append({'kind':kind,'id':identifier,'file':name})
   else:
    lift(child);blocks.append({'kind':'legacy','id':identifier,'file':fragment(str(child),f'{identifier}-{i}')})
  attrs={k:(' '.join(v) if isinstance(v,list) else v) for k,v in record.attrs.items()}
 else:before=s.body.decode_contents() if s.body else '';after='';attrs=None
 head_path=fragment(s.head.decode_contents() if s.head else '', 'head')
 page={'name':source.name,'title':s.title.get_text() if s.title else stem,'headFile':head_path,'htmlAttributes':dict(s.html.attrs) if s.html else {'lang':'ru'},'bodyAttributes':dict(s.body.attrs) if s.body else {},'recordAttributes':attrs,'beforeFile':fragment(before,'before'),'afterFile':fragment(after,'after'),'blocks':blocks,'alias':bool(s.select_one('meta[http-equiv="refresh"]'))}
 write_json(ENGINE/f'src/content/pages/{source.name}.json',page);write_json(ENGINE/f'src/content/texts/{source.name}.json',texts);pages.append(page)
for p in SOURCE.iterdir():
 if p.suffix=='.html' or p.name in ('replica-search.json','price-catalog.json','sitemap.xml'):continue
 target=ENGINE/'public'/p.name
 if p.is_dir():shutil.copytree(p,target,dirs_exist_ok=True)
 else:shutil.copy2(p,target)
report={'pages':len(pages),'aliases':sum(p['alias'] for p in pages),'shared_templates':{k:len(v) for k,v in shared.items()},'editable_text_fields':field_count,'price_items':sum(len(g['items']) for c in catalog for g in c['groups'])}
write_json(ENGINE/'reports/import.json',report);print(json.dumps(report))
