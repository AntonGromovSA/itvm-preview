from pathlib import Path
import sys,re,json,html,copy,urllib.parse,hashlib,shutil
ROOT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'vendor'))
from bs4 import BeautifulSoup
import requests
OUT=ROOT/'site';SOURCE=ROOT/'replica/source'
assetmap=json.loads((ROOT/'replica/asset-map.json').read_text(encoding='utf8'))
data=json.loads((ROOT/'itvm-data.json').read_text(encoding='utf8'))
BASE='https://itvm.ru/ever-youth/';VERSION='replica-20261026'
ORIGINAL_HOSTS={'ever-youth.ru','www.ever-youth.ru','tune-braw-dulcimer.tilda.ws'}
# Preserve the original Adobe font kit and cache its public font files.
fonturl='https://use.typekit.net/fsc1hwg.css'
fontfile=OUT/'assets/original-font-kit.css'
if not fontfile.exists():
 raw=requests.get(fonturl,timeout=20).text
 for u in set(re.findall(r'https://use\.typekit\.net/af/[^\"\)]+',raw)):
  ext={ 'l':'.woff2','d':'.woff','a':'.otf'}.get(urllib.parse.urlsplit(u).path.rsplit('/',1)[-1],'.woff2')
  name=hashlib.sha256(u.encode()).hexdigest()[:20]+ext;p=OUT/'assets'/name
  if not p.exists():r=requests.get(u,timeout=20);r.raise_for_status();p.write_bytes(r.content)
  raw=raw.replace(u,name)
 raw=re.sub(r'@import[^;]+;','',raw);fontfile.write_text(raw,encoding='utf8')
assetmap[fonturl]='assets/original-font-kit.css'
for f in (ROOT/'dist/assets').glob('itvm-*.webp'):shutil.copy2(f,OUT/'assets'/f.name)
for name in ('clinic-tour.mp4','longevity.mp4'):
 if not (OUT/'assets'/name).exists():shutil.copy2(ROOT/'dist/assets'/name,OUT/'assets'/name)
originals={f.name:f.read_text(encoding='utf8') for f in SOURCE.glob('*.html')}
mapping={
 '/o-nas':'page178631709.html','/o-nas/pochemu-itvm':'page178631709.html',
 '/uslugi':'page178642509.html','/metody-lecheniya':'page174904109.html','/programmy':'page168915909.html',
 '/konsultatsii-spetsialistov':'page172957109.html','/price-list':'page178607409.html','/kontakty':'page171084309.html',
 '/uslugi/diagnostika-apparatnaya-i-klassicheskaya':'page182655909.html','/uslugi/kosmetologiya':'page182669909.html',
 '/uslugi/vosstanovitelnaya-meditsina':'page182686609.html','/uslugi/ginekologiya':'page182699009.html','/uslugi/nevrologiya':'page182706809.html',
 '/uslugi/pediatriya':'page182714209.html','/uslugi/terapiya':'page182718709.html','/uslugi/kardiologiya':'page182725309.html',
 '/metody-lecheniya/igloukalyvanie':'page182733209.html','/programmy/vosstanovim-obonyanie':'page185646609.html',
 '/programmy/help-for-you':'page172542009.html','/programmy/menopausa':'page172574209.html','/programmy/molodost':'page172831609.html',
 '/programmy/unikalnaya-programma-muzhskogo-i-zhenskogo-zdorovya':'page172935509.html','/programmy/pazzo-termale':'page171071209.html',
 '/programmy/diagnostika-profilaktika-zdorovya':'page185673709.html','/programmy/bezoperatsionnoe-lechenie-varikoznogo-rasshireniya-ven':'page185695609.html',
 '/programmy/profilaktika-i-lechenie-serdechno-sosudistyh-zabolevaniy':'page185701709.html','/programmy/omolojeniye':'page185863009.html'}
for p in data['pages']:
 if 'content' not in p or '/zabolevaniya/' in p['path']:continue
 if p['path'] not in mapping:
  prefix='doctor' if p['path'].startswith('/konsultatsii') else 'method'
  mapping[p['path']]=prefix+'-'+p['path'].rsplit('/',1)[-1]+'.html'
shorts={'/vrachi':'page172957109.html','/programmy':'page168915909.html','/zapis':'page170676909.html','/advantages':'page178631709.html','/analiz':'page182655909.html','/aquatornado':'page171071209.html','/sauna':'page171080109.html'}
for slug in ('uwater','uwood','uearth','ufair','umetall'):shorts['/'+slug]='page178642509.html'
method_slugs={'testherapy':'transcranialelectricalstimulation','acupuncture':'igloukalyvanie','reflexology':'refleksoterapiya','kineseotherapy':'kinezioterapiya','sujok':'su-jok','tuinamassage':'massage-tuyna','vacuumgradienttherapy':'vakuum-gradientnaya-terapiya','hirudotherapy':'girudoterapiya','ozonetherapy':'ozonoterapiya','transdermalpharmacoresis':'farmateb-for-you','bioresonancetherapy':'biorezonansnaya-terapiya','mnkmethod':'mnk','mineralwaters':'voda-navsegda','inhalationtherapy':'ingalacii','homeopathy':'gomeopatia-ot-irini'}
for shortcut,slug in method_slugs.items():shorts['/'+shortcut]=mapping['/metody-lecheniya/'+slug]
doctor_slugs={'koroleva':'koroleva','desityaric':'glavnyy-vrach','chaban':'chaban-tatyana-nikolaevna','pokladova':'ludmila-pokladova','shalamova':'yulia-shalamova','basha':'tatiyana-busha','vandeshev':'doctor-vandishev','ivanova':'darya-ivanova','shaxova':'shahova-dr','manevskaia':'manaevskaya-ginekolog','alekseeva':'doctor-alexeeva','gureeva':'bolshe-ne-bolit-givot','iskandarova':'iskanderova-nurticia','kairova':'hasanova','panov':'panov-gennadii-aleksandrovich','soboleva':'soboleva-vika','akutsa':'tatiana-akutsa','nechaeva':'doctor-nechaeva','oleinik':'doctor-oleynik','shakov':'doctor-shakov','chekunov':'chekunov-oleg-vladimirovich','minaenkov':'spa-man','loskutov':'massageryzdom','gudkova':'doctor-gudkova','bivalicev':'vycheslav-byvalcev','baxtina':'alla-bachtina','shubina':'elena-shubina','volkova':'volkova'}
for shortcut,slug in doctor_slugs.items():shorts['/'+shortcut]=mapping['/konsultatsii-spetsialistov/'+slug]
(OUT/'replica-routes.js').write_text('window.ITVM_REPLICA_ROUTES='+json.dumps(shorts,ensure_ascii=False)+';',encoding='utf8')
oldassets={}
for p in data['pages']:
 if 'content' not in p:continue
 old=BeautifulSoup(p['content'],'html.parser')
 for img in old.select('img[src]'):
  u=urllib.parse.urljoin('https://itvm.ru',img['src']);name='assets/itvm-'+hashlib.sha256(u.encode()).hexdigest()[:16]+'.webp'
  if (OUT/name).exists():oldassets[u]=name
def localhref(value):
 if value.startswith('#'):return value
 value=value.replace('/https://','https://');u=urllib.parse.urlsplit(urllib.parse.urljoin('https://ever-youth.ru/',value))
 if u.hostname in ORIGINAL_HOSTS:
  if u.path.rstrip('/') in shorts:return shorts[u.path.rstrip('/')]
  name=u.path.lstrip('/') or 'index.html'
  if name in originals:return name+('?'+u.query if u.query else '')+('#'+u.fragment if u.fragment else '')
 if u.hostname in ('itvm.ru','www.itvm.ru') and u.path.rstrip('/') in mapping:return mapping[u.path.rstrip('/')]
 return value
def media_figure(src,title,poster=''):
 return f'<figure class="itvm-video"><video controls playsinline preload="metadata" {"poster="+chr(34)+poster+chr(34) if poster else ""} aria-label="{html.escape(title)}"><source src="{src}" type="video/mp4">Ваш браузер не поддерживает видео.</video><figcaption>{html.escape(title)}</figcaption></figure>'
def section(title,content,kicker='МАТЕРИАЛЫ ИНСТИТУТА',sid='details'):
 return f'<section id="{sid}" class="itvm-addition"><div class="itvm-addition-inner"><p class="itvm-kicker">{kicker}</p><h2>{html.escape(title)}</h2>{content}</div></section>'
def clean(raw):
 s=BeautifulSoup(raw,'html.parser')
 for n in s.select('script,style,link,form,input,object,embed,noscript,svg'):n.decompose()
 for n in list(s.find_all(True)):
  if n.name is None:continue
  if n.name=='iframe':
   src=n.get('src','');m=re.match(r'https://(?:www\.)?youtube\.com/embed/([\w-]+)',src)
   if not m:n.decompose();continue
   title=n.get('title','Видео о методе лечения');vid=m[1]
   n.attrs={'src':'https://www.youtube-nocookie.com/embed/'+vid,'title':title,'loading':'lazy','allow':'fullscreen; encrypted-media; picture-in-picture','allowfullscreen':''}
   wrapper=s.new_tag('figure',attrs={'class':'itvm-youtube'});n.wrap(wrapper)
   fallback=s.new_tag('a',href='https://www.youtube.com/watch?v='+vid,attrs={'target':'_blank','rel':'noopener'});fallback.string='Открыть видео на YouTube ↗';wrapper.append(fallback)
  elif n.name=='img':
   u=urllib.parse.urljoin('https://itvm.ru',n.get('src',''));name=oldassets.get(u)
   if not name:n.decompose();continue
   n.attrs={'src':name,'alt':n.get('alt',''),'loading':'lazy'}
  elif n.name=='a':
   href=urllib.parse.urljoin('https://itvm.ru',n.get('href',''));parsed=urllib.parse.urlsplit(href)
   if parsed.path.rstrip('/') in mapping:href=mapping[parsed.path.rstrip('/')]
   elif parsed.hostname in ('itvm.ru','www.itvm.ru') and not re.search(r'\.(pdf|jpg|png|docx?)$',parsed.path,re.I):n.unwrap();continue
   if not href.startswith(('https://','http://','mailto:','tel:')) and not href.endswith('.html'):n.unwrap();continue
   n.attrs={'href':href}
  elif n.name in ('p','h2','h3','h4','ul','ol','li','strong','b','em','i','br','hr','blockquote','table','thead','tbody','tr','td','th','sup','sub'):n.attrs={}
  elif n.name=='h1':n.name='h3';n.attrs={}
  elif n.name not in ('figure',):n.unwrap()
 return str(s)
def version_links(raw):
 def change(m):
  href=html.unescape(m[1]);p=urllib.parse.urlsplit(href)
  if p.scheme or p.netloc or not p.path.endswith('.html'):return m[0]
  q=[(k,v) for k,v in urllib.parse.parse_qsl(p.query,keep_blank_values=True) if k!='v']+[('v',VERSION)]
  return 'href="'+html.escape(urllib.parse.urlunsplit(('', '',p.path,urllib.parse.urlencode(q),p.fragment)),quote=True)+'"'
 return re.sub(r'href="([^"]+)"',change,raw)
def finalize(s,name):
 # Resolve original navigation and source links while retaining all original records.
 for a in s.select('a[href]'):a['href']=localhref(a['href'])
 for n in s.select('[data-original]'):
  if n['data-original'] in ('%23n','#n'):n['data-original']='data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
 for n in s.select('link[rel=canonical]'):n['href']=BASE+name
 for n in s.select('meta[property="og:url"]'):n['content']=BASE+name
 add=s.new_tag('link',rel='stylesheet',href='replica-additions.css?v='+VERSION);s.head.append(add)
 route_script=s.new_tag('script',src='replica-routes.js?v='+VERSION,defer=True);s.head.append(route_script)
 script=s.new_tag('script',src='replica-additions.js?v='+VERSION,defer=True);s.head.append(script)
 search_script=s.new_tag('script',src='replica-search.js?v='+VERSION,defer=True);s.head.append(search_script)
 raw=str(s)
 for url,filename in sorted(assetmap.items(),key=lambda x:len(x[0]),reverse=True):
  if filename:raw=raw.replace(html.escape(url,quote=True),filename).replace(url,filename)
 raw=version_links(raw)
 (OUT/name).write_text(raw,encoding='utf8')
def supplement(s,markup,before_end=True):
 new=BeautifulSoup(markup,'html.parser');footer=s.select_one('#t-footer')
 if footer:footer.insert_before(new)
 else:s.select_one('#allrecords').append(new)
def profile_links():
 return '<div class="itvm-profile-links">'+''.join(f'<a href="{mapping[d["path"]]}">{html.escape(d["name"])}<span>Профиль и образование ↗</span></a>' for d in data['doctors'])+'</div>'
def directory(group):
 return '<div class="itvm-profile-links">'+''.join(f'<a href="{mapping[p["path"]]}">{html.escape(p["title"])}<span>Подробнее ↗</span></a>' for p in data['pages'] if 'content'in p and p['path'].startswith(group+'/') and p['path'].count('/')==2 and p['path'] in mapping)+'</div>'
for name,raw in originals.items():
 s=BeautifulSoup(raw,'html.parser')
 if name=='page178631709.html':
  video=section('Знакомство с клиникой',media_figure('assets/clinic-tour.mp4','Институт традиционной восточной медицины на Арбате'),'ВИДЕО','clinic-video')
  records=s.select('#allrecords > .t-rec')
  if len(records)>1:records[1].insert_after(BeautifulSoup(video,'html.parser'))
  else:supplement(s,video)
  about=next(p for p in data['pages'] if p['path']=='/o-nas')
  supplement(s,section('Подробно об институте',clean(about['content'])))
 if name=='page172957109.html':supplement(s,section('Образование и опыт специалистов',profile_links(),'КОМАНДА ИНСТИТУТА'))
 if name=='page174904109.html':supplement(s,section('Подробно о методах лечения',directory('/metody-lecheniya'),'L’ART DU SOIN'))
 if name=='page168915909.html':supplement(s,section('Лаборатория вечной юности','<p>Регенеративная медицина и активное долголетие — материалы направления VITA ELYSIUM.</p><a class="itvm-link-button" href="longevity.html">Открыть направление ↗</a>','ДОЛГОЛЕТИЕ'))
 if name=='page185863009.html':supplement(s,section('Активное долголетие','<p>Диагностика, индивидуальный подход и сопровождение в лаборатории вечной юности.</p><a class="itvm-link-button" href="longevity.html">Лаборатория вечной юности ↗</a>'))
 for path,target in mapping.items():
  if target==name and path not in ('/o-nas','/o-nas/pochemu-itvm','/uslugi','/metody-lecheniya','/programmy','/konsultatsii-spetsialistov','/price-list','/kontakty'):
   p=next((x for x in data['pages'] if x['path']==path and 'content'in x),None)
   if p:supplement(s,section('Дополнительная информация',clean(p['content'])))
 finalize(s,name)
# Additional profiles use the original first site's actual header and footer.
def document(title,body,name):
 s=BeautifulSoup(originals['page178631709.html'],'html.parser');root=s.select_one('#allrecords')
 for node in list(root.children):
  if getattr(node,'name',None) and node.get('id') in ('t-header','t-footer'):continue
  node.extract()
 s.title.string=title+' | ИТВМ Арбат'
 supplement(s,section(title,body,'ИНСТИТУТ ТРАДИЦИОННОЙ ВОСТОЧНОЙ МЕДИЦИНЫ'))
 finalize(s,name)
for p in data['pages']:
 path=p['path']
 if 'content' not in p or path not in mapping or mapping[path] in originals:continue
 title=next((d['name'] for d in data['doctors'] if d['path']==path),p['title'])
 # Reuse the portrait already verified in the previous import.
 previous=ROOT/'dist'/mapping[path];portrait=''
 if not previous.exists():previous=OUT/mapping[path]
 if previous.exists():
  im=BeautifulSoup(previous.read_text(encoding='utf8'),'html.parser').select_one('.profile-photo,.itvm-portrait')
  if im:portrait=f'<img class="itvm-portrait" src="{im["src"]}" alt="{html.escape(title)}">'
 body=portrait+clean(p['content'])+'<p><a class="itvm-link-button" href="page170676909.html">Записаться на приём ↗</a></p>'
 document(title,body,mapping[path])
# Content from the second site retains its video and factual sections in the first site's shell.
second_path=ROOT/'source-second.html'
if not second_path.exists():second_path=ROOT.parent/'source-second.html'
second=BeautifulSoup(second_path.read_text(encoding='utf-8-sig'),'html.parser')
parts=[];seen=set()
for atom in second.select('.tn-atom'):
 if atom.select_one('.tn-atom'):continue
 t=atom.get_text(' ',strip=True)
 if len(t)<35 or t in seen:continue
 seen.add(t)
 if any(x in t.lower() for x in ('отсутствие побочных','отсутствие токсичности','доказанное омоложение','нет болезней и старости')):continue
 tag='h3' if len(t)<130 and t.upper()==t else 'p'
 parts.append(f'<{tag}>{html.escape(t)}</{tag}>')
body=media_figure('assets/longevity.mp4','Лаборатория вечной юности')+''.join(parts)+'<p><a class="itvm-link-button" href="page170676909.html">Записаться на консультацию ↗</a></p>'
document('Лаборатория вечной юности · VITA ELYSIUM',body,'longevity.html')
# Existing shared links continue to land on the original site's pages.
aliases={'clinic.html':'page178631709.html','doctors.html':'page172957109.html','services.html':'page178642509.html','methods.html':'page174904109.html','programs.html':'page168915909.html','palazzo.html':'page171071209.html','prices.html':'page178607409.html','contacts.html':'page171084309.html','advantages.html':'page178631709.html'}
for p in data['pages']:
 if p['path'] in mapping:
  pref={'uslugi':'service','metody-lecheniya':'method','programmy':'program','konsultatsii-spetsialistov':'doctor'}.get(p['path'].split('/')[1])
  if pref:
   alias=pref+'-'+p['path'].rsplit('/',1)[-1]+'.html'
   if alias!=mapping[p['path']]:aliases[alias]=mapping[p['path']]
for alias,target in aliases.items():
 u=target+'?v='+VERSION
 (OUT/alias).write_text('<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0;url='+u+'"><title>ИТВМ Арбат</title></head><body><a href="'+u+'">Открыть страницу ИТВМ</a></body></html>',encoding='utf8')
document('Конфиденциальность','<p>Запись на приём и условия обработки персональных данных уточняйте у администратора: +7 (495) 691-66-12, itvm@mail.ru.</p><p>На страницах с роликами YouTube используется сторонний проигрыватель. Для него действуют условия сервиса YouTube.</p>','privacy.html')
print('Built exact originals',len(originals),'plus profiles, articles and compatibility links. Total HTML:',len(list(OUT.glob('*.html'))),flush=True)

