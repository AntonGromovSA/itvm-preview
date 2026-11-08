"""Compile the owner's authored compositions to static HTML/CSS, with no editor runtime."""
from pathlib import Path
import sys,re,json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT.parents[2]/'ever-youth/vendor'))
from bs4 import BeautifulSoup,Comment
import tinycss2
SOURCE=ROOT.parent/'site';OUT=ROOT/'src/compositions';OUT.mkdir(exist_ok=True);PUBLIC=ROOT/'public';(PUBLIC/'composition').mkdir(exist_ok=True);(PUBLIC/'design-media').mkdir(exist_ok=True);(PUBLIC/'brand').mkdir(exist_ok=True)
shutil.copy2(SOURCE/'assets/a897742453b07a7c2ad9.png',PUBLIC/'brand/crest.png')
shutil.copy2(SOURCE/'assets/36a27ab79465db8faeba.webp',PUBLIC/'brand/entrance.webp')
def cls(value):
 if value.startswith('t-slds'):return 'carousel'+value[6:]
 if value.startswith('tn-'):return 'node-'+value[3:]
 if value.startswith('t396'):return 'canvas'+value[4:]
 if re.match(r't\d',value):return re.sub(r'^t','section',value)
 if value.startswith('t-'):return 'art-'+value[2:]
 if value.startswith('js-'):return 'hook-'+value[3:]
 return value
def asset(value,css=False):
 value=value.strip(' \"\'')
 if value.startswith('assets/'):
  p=SOURCE/value
 elif css and not re.match(r'^(?:[a-z]+:|/|#|data:)',value):p=SOURCE/'assets'/value
 else:return value
 if p.exists() and p.suffix.lower() in ['.svg','.png','.jpg','.jpeg','.webp','.gif','.mp4','.pdf']:
  dest=PUBLIC/'design-media'/p.name
  if not dest.exists():shutil.copy2(p,dest)
  return '/ever-youth/design-media/'+p.name
 return value
dark=['#050608','#161414','#15130a','#151b19','#1e2622','#0b0b0b','#000000','#000','#111111','#111','#141414','#1a1a1a','#222222','#222','#0f0e0c','#101010']
light=['#ffffff','#fff','#f3ece2','#e9dfcf','#f5f0e7','#f1ece3','#f7f1e8','#ece4d6']
def paint(name,value):
 value=value.replace('TildaSans','Onest').replace('--t396','--design-layout').replace('--t-','--design-')
 value=re.sub(r'url\(([^)]+)\)',lambda m:m[0] if m[1].strip(' \"\'').startswith('data:') else 'url("'+asset(m[1],True)+'")',value)
 if 'background' in name or name in ('fill','stroke'):
  for c in sorted(dark,key=len,reverse=True):value=re.sub(re.escape(c)+r'(?![\da-f])','#faf9f6',value,flags=re.I)
  value=re.sub(r'rgba?\(\s*(?:22\s*,\s*20\s*,\s*20|21\s*,\s*19\s*,\s*10|5\s*,\s*6\s*,\s*8)\s*(,[\d.\s]+)?\)',lambda m:'rgba(250,249,246'+(m[1] or ',1')+')',value)
 if name in ('color','fill','stroke','-webkit-text-fill-color'):
  for c in sorted(light,key=len,reverse=True):value=re.sub(re.escape(c)+r'(?![\da-f])','#28332f',value,flags=re.I)
  value=re.sub(r'rgb\(\s*(?:255\s*,\s*255\s*,\s*255|243\s*,\s*236\s*,\s*226)\s*\)','#28332f',value)
 if 'color' in name:value=value.replace('#e4c078','#8b704b').replace('#b89b72','#8b704b')
 if name in ('color','fill','stroke','-webkit-text-fill-color'):
  def foreground(m):
   h=m[1];h=''.join(c*2 for c in h) if len(h)==3 else h
   if len(h) not in (6,8):return m[0]
   r,g,b=[int(h[i:i+2],16) for i in (0,2,4)]
   if (r+g+b)/3>155:return '#8b704b' if r>b+25 and g>b+12 else '#28332f'
   return m[0]
  value=re.sub(r'#([0-9a-fA-F]{3,8})(?![0-9a-fA-F])',foreground,value)
  def foreground_rgb(m):
   r,g,b=[int(m[i]) for i in (1,2,3)]
   return '#8b704b' if (r+g+b)/3>155 and r>b+25 else '#28332f' if (r+g+b)/3>155 else m[0]
  value=re.sub(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,[\d.\s]+)?\)',foreground_rgb,value)
 if 'background' in name:
  value=re.sub(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(,[\d.\s]+)?\)',lambda m:'rgba(250,249,246'+(m[4] or ',1')+')' if all(int(m[i])<70 for i in (1,2,3)) else m[0],value)
 return value
def declarations(content):
 output=[]
 for d in tinycss2.parse_declaration_list(content,skip_comments=True,skip_whitespace=True):
  if d.type!='declaration':continue
  value=paint(d.lower_name,tinycss2.serialize(d.value));name=d.name.replace('--t396','--design-layout').replace('--t-','--design-')
  output.append(name+':'+value+('!important' if d.important else '')+';')
 
 if any(d.type=='declaration' and d.lower_name in ['background-clip','-webkit-background-clip'] and 'text' in tinycss2.serialize(d.value) for d in tinycss2.parse_declaration_list(content,skip_comments=True,skip_whitespace=True)):
  output.append('background-image:linear-gradient(110deg,#7d623a,#b08d51,#7d623a)!important;')
 return ''.join(output)
def stylesheet(raw):
 def walk(rules,keyframes=False):
  out=[]
  for rule in rules:
   if rule.type=='qualified-rule':
    selector=tinycss2.serialize(rule.prelude).strip();selectors=[]
    if re.search('tilda',selector,re.I):continue
    for s in selector.split(','):
     s=re.sub(r'\.([a-zA-Z_][\w-]*)',lambda m:'.'+cls(m[1]),s)
     s=re.sub(r'(?<![\w-])(?:body|html)(?![\w-])|:root|#allrecords', '.authored-page',s)
     s=s.replace('#t-footer','#institution-footer')
     if not keyframes and not s.strip().startswith('.authored-page'):s='.authored-page '+s.strip()
     selectors.append(s)
    out.append(','.join(selectors)+'{'+declarations(rule.content)+'}')
   elif rule.type=='at-rule' and rule.content is not None and rule.lower_at_keyword not in ['font-face','charset','import']:
    pre=tinycss2.serialize(rule.prelude).strip();out.append('@'+rule.at_keyword+' '+pre+'{'+walk(tinycss2.parse_rule_list(rule.content,skip_comments=True,skip_whitespace=True),'keyframes' in rule.lower_at_keyword)+'}')
  return ''.join(out)
 return walk(tinycss2.parse_stylesheet(raw,skip_comments=True,skip_whitespace=True))
def convert(root):
 for c in root.find_all(string=lambda s:isinstance(s,Comment)):c.extract()
 for x in root.select('script,style,noscript,meta,link'):x.decompose()
 for x in root.select('a[href*="tilda."]'):x.decompose()
 for x in root.select('form'):
  panel=BeautifulSoup('<div class="restored-booking"><h3>Запись на приём</h3><p>Свяжитесь с администратором, чтобы выбрать специалиста и время приёма.</p><a href="page170676909.html">Записаться на приём ↗</a></div>','html.parser');x.replace_with(panel)
 for x in root.find_all():
  if not x.name:continue
  if x.get('data-mp4video'):
   video=BeautifulSoup('<video class="design-motion-video" autoplay muted loop playsinline preload="metadata" style="width:100%;height:100%;object-fit:contain"></video>','html.parser').video
   video['src']=asset(x['data-mp4video']);x.append(video)
  if x.get('class'):x['class']=[cls(c) for c in x['class'] if c not in ['loading','rendering']]
  if x.get('style'):x['style']=declarations(x['style'])
  if x.get('id')=='t-footer':x['id']='institution-footer'
  for attr in list(x.attrs):
   if attr.startswith('on') or attr.startswith('data-tilda') or attr in ['data-record-type','data-hook','data-animationappear','field','bgimgfield','imgfield']:del x[attr]
   elif attr.startswith('data-field-') or (attr.startswith('data-group-') and attr!='data-group-id'):del x[attr]
   elif attr.startswith('data-animate') or attr.startswith('data-anim-'):del x[attr]
  for attr in ['src','poster','href']:
   if x.get(attr):x[attr]=asset(re.sub(r'\?v=[^#&]*','',x[attr]))
  if x.get('data-original'):
   v=asset(x['data-original']);x['data-original']=v
   if x.name=='img':x['src']=v;x['loading']='lazy';x['decoding']='async'
   else:x['style']=x.get('style','')+'background-image:url("'+v+'");'
  if x.name=='img' and x.get('src','').endswith('.svg'):x['class']=x.get('class',[])+['design-vector']
  if x.name=='iframe':x['loading']='lazy'
  if x.name=='svg':
   for path in x.select('[fill],[stroke]'):
    for a in ['fill','stroke']:
     if path.get(a):path[a]=paint(a,path[a])
 # Rebuild native carousel flow rather than relying on a script-created track width.
 for wrapper in root.select('.carousel__items-wrapper'):
  wrapper['class']=wrapper.get('class',[])+['authored-track']
  controls=BeautifulSoup('<div class="authored-carousel-controls"><button type="button" data-carousel-prev aria-label="Предыдущий слайд">←</button><button type="button" data-carousel-next aria-label="Следующий слайд">→</button></div>','html.parser').div
  wrapper.insert_before(controls)
  for arrow in wrapper.select('.carousel__arrow_wrapper'):arrow.decompose()
 for t in root.select('[data-tab-rec-ids]'):t['data-native-targets']=t['data-tab-rec-ids']
 # Header-generated body IDs must remain unique even when old source reused "details".
 seen=set()
 for x in root.select('[id]'):
  ident=x['id']
  if ident in seen:x['id']=ident+'-copy-'+str(len(seen))
  seen.add(x['id'])
 return root
index={};report=[]
for p in sorted((ROOT/'src/data/pages').glob('*.json')):
 page=json.loads(p.read_text(encoding='utf8'))
 if page.get('alias') or page['kind'] in ['prices','booking'] or page['name']=='404.html':continue
 source=BeautifulSoup((SOURCE/page['name']).read_text(encoding='utf8'),'html.parser');allrecords=source.select_one('#allrecords')
 if not allrecords:continue
 css=[]
 for link in source.head.select('link[rel="stylesheet"]'):
  file=SOURCE/link.get('href','').split('?')[0]
  if file.is_file() and file.suffix=='.css' and file.name not in ['identity-fonts.css','identity.css']:
   css.append(stylesheet(file.read_text(encoding='utf8')))
 for style in allrecords.select('style'):css.append(stylesheet(style.get_text()))
 for item in list(allrecords.find_all(recursive=False)):
  if item.get('id') in ['t-header','t-footer'] or item.get('data-record-type') in ['1370','215','376']:item.decompose()
  elif item.get('data-record-type')=='18' and page['name']=='index.html':item.decompose()
 for item in allrecords.select('#tildacopy'):item.decompose()
 allrecords=convert(allrecords);allrecords.attrs={'class':'authored-page','data-authored-page':page['name']}
 raw=str(allrecords);css=''.join(css)
 css=css.replace('Tilda','Design')
 digest=hashlib.sha256(css.encode()).hexdigest()[:16];name='composition-'+digest+'.css';(PUBLIC/'composition'/name).write_text(css,encoding='utf8')
 file=page['name'].replace('.html','.html');(OUT/file).write_text(raw,encoding='utf8')
 index[page['name']]={'htmlFile':file,'css':'composition/'+name,'hasH1':bool(allrecords.select_one('h1'))};report.append({'page':page['name'],'sections':len(allrecords.find_all(recursive=False)),'images':len(allrecords.select('img')),'cssBytes':len(css),'htmlBytes':len(raw)})
footer_source=BeautifulSoup((SOURCE/'index.html').read_text(encoding='utf8'),'html.parser');footer=footer_source.select_one('#t-footer')
footer_css=''.join(stylesheet((SOURCE/'assets'/name).read_text(encoding='utf8')) for name in ['55fa348d4437c18e9566.css','f9c038da27319eec7778.css'])
footer_css+=''.join(stylesheet(s.get_text())for s in footer.select('style'))
footer=convert(footer);footer.name='div';footer.attrs={'class':'authored-page original-footer','id':'institution-footer'}
footer_name='footer-'+hashlib.sha256(footer_css.encode()).hexdigest()[:16]+'.css';(PUBLIC/'composition'/footer_name).write_text(footer_css,encoding='utf8');(OUT/'footer.html').write_text(str(footer),encoding='utf8')
(ROOT/'src/data/composition-footer.json').write_text(json.dumps({'css':'composition/'+footer_name}),encoding='utf8')
keep={x['css'].split('/')[-1] for x in index.values()}|{footer_name}
for old in (PUBLIC/'composition').glob('*.css'):
 if old.name not in keep:
  assert old.resolve().is_relative_to(PUBLIC.resolve());old.unlink()
(ROOT/'src/data/compositions.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf8')
(ROOT/'reports/composition-restore.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({'pages':len(index),'assets':sum(1 for p in (PUBLIC/'design-media').iterdir()),'home':next(x for x in report if x['page']=='index.html')}))
