"""Build the existing design with verified content captured from itvm.ru."""
from pathlib import Path
import sys,json,re,runpy,html,hashlib,urllib.parse,concurrent.futures
ROOT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'vendor'))
from bs4 import BeautifulSoup
import requests
from PIL import Image,ImageOps
from io import BytesIO
ctx=runpy.run_path(str(ROOT/'build.py'))
R=ROOT/'site'; E=html.escape
head,button,cards=ctx['head'],ctx['button'],ctx['cards']
data=json.loads((ROOT/'itvm-data.json').read_text(encoding='utf8'))
source_home=BeautifulSoup((ROOT/'source-itvm/index.html').read_text(encoding='utf-8-sig'),'html.parser')
rows={p['path']:p for p in data['pages'] if 'content' in p}
mapping={'/o-nas':'clinic.html','/uslugi':'services.html','/metody-lecheniya':'methods.html','/programmy':'programs.html','/konsultatsii-spetsialistov':'doctors.html','/price-list':'prices.html','/kontakty':'contacts.html','/programmy/pazzo-termale':'program-pazzo-termale.html','/o-nas/pochemu-itvm':'advantages.html'}
for path in rows:
 if path not in mapping:
  prefix={'konsultatsii-spetsialistov':'doctor','uslugi':'service','programmy':'program','metody-lecheniya':'method'}.get(path.split('/')[1],'info')
  mapping[path]=prefix+'-'+path.rsplit('/',1)[-1]+'.html'
def text(raw):return re.sub(r'\s+',' ',BeautifulSoup(raw,'html.parser').get_text(' ',strip=True)).strip()
doctors=data['doctors']
oldspec=dict(ctx['doctor_names'])
for d in doctors:
 d['subtitle']=oldspec.get(d['name'],'')
 for a in source_home.select(f'a[href="{d["path"]}"]'):
  if a.select_one('img'):
   for ancestor in list(a.parents)[:4]:
    t=ancestor.get_text(' ',strip=True)
    if len(d['name'])+5<len(t)<700:
     d['subtitle']=t.replace(d['name'],'').replace('Подробнее','').strip();break
 if not d['subtitle']:
  bio=text(rows.get(d['path'],{}).get('content',''))
  sentences=re.split(r'(?<=[.!])\s+',bio)
  d['subtitle']=next((x for x in sentences if re.match(r'^(Врач|Доктор|Специалист|Мануальный|Руководитель)',x)), 'Специалист института')[:200]
 overrides={'doctor-dobrecov':'Доктор медицинских наук, специалист в области клинической ольфактологии, ЛОР-хирург высшей категории','manaevskaya-ginekolog':'Врач акушер-гинеколог, хирург','vycheslav-byvalcev':'Врач аюрведы, остеопат, кинезиолог','yulia-shalamova':'Клинический психолог, специалист нейропсихологической диагностики и реабилитации; ТЭС-терапия'}
 d['subtitle']=overrides.get(d['path'].rsplit('/',1)[-1],d['subtitle'])
 # A profile may contain a portrait even when absent from the home carousel.
 if not d.get('image'):
  im=BeautifulSoup(rows.get(d['path'],{}).get('content',''),'html.parser').select_one('img[src]')
  if im:d['image']=urllib.parse.urljoin('https://itvm.ru',im['src'])
assets={}
for d in doctors:
 if d.get('image'):assets[d['image']]=None
for p in rows.values():
 for im in BeautifulSoup(p['content'],'html.parser').select('img[src]'):
  u=urllib.parse.urljoin('https://itvm.ru',im['src'])
  if urllib.parse.urlsplit(u).hostname in ('itvm.ru','www.itvm.ru'):assets[u]=None
def asset(u):
 name='assets/itvm-'+hashlib.sha256(u.encode()).hexdigest()[:16]+'.webp';out=R/name
 try:
  if not out.exists():
   response=requests.get(u,timeout=20);response.raise_for_status()
   im=ImageOps.exif_transpose(Image.open(BytesIO(response.content))).convert('RGB');im.thumbnail((1400,1400));im.save(out,'WEBP',quality=84)
  return u,name
 except Exception:return u,None
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
 for u,name in pool.map(asset,assets):assets[u]=name
print('Local images',sum(bool(x) for x in assets.values()),'of',len(assets),flush=True)
def clean(raw):
 s=BeautifulSoup(raw,'html.parser')
 for n in s.select('script,style,link,iframe,form,input,button,video,audio,object,embed,noscript,svg'):
  n.decompose()
 for n in list(s.find_all(True)):
  if n.name is None:continue
  tag=n.name
  if tag=='img':
   u=urllib.parse.urljoin('https://itvm.ru',n.get('src',''));local=assets.get(u)
   if not local:n.decompose();continue
   alt=n.get('alt','');n.attrs={'src':local,'alt':alt,'loading':'lazy','decoding':'async'};continue
  if tag=='a':
   href=n.get('href','');absolute=urllib.parse.urljoin('https://itvm.ru',href);parsed=urllib.parse.urlsplit(absolute);path=parsed.path.rstrip('/')
   if href.startswith('#') or not href:href='contacts.html#appointment'
   elif parsed.hostname in ('itvm.ru','www.itvm.ru'):
    if path in mapping:href=mapping[path]
    elif path=='':href='index.html'
    elif re.search(r'\.(pdf|docx?|xlsx?)$',path,re.I):href=absolute
    elif path.startswith(('/images/','/files/')):href=absolute
    else:n.unwrap();continue
   else:href=absolute
   if not href.startswith(('https://','http://','tel:','mailto:','#')) and not re.match(r'^[a-z0-9-]+\.html',href):n.unwrap();continue
   n.attrs={'href':href}
   if href.startswith(('http://','https://')):n['target']='_blank';n['rel']='noopener'
  elif tag in ('p','h2','h3','h4','h5','h6','ul','ol','li','strong','b','em','i','br','hr','blockquote','table','thead','tbody','tr','td','th','figure','figcaption','sup','sub'):
   n.attrs={}
   if tag=='h1':n.name='h2'
  elif tag=='h1':n.name='h2';n.attrs={}
  else:n.unwrap()
 for p in s.select('p'):
  if not p.get_text(strip=True) and not p.select('img'):p.decompose()
 return str(s)
def source_note(path):return f'<p class="source-note">Материалы института: <a href="https://itvm.ru{path}" target="_blank" rel="noopener">itvm.ru ↗</a> · Информация на 26 октября 2026 года.</p>'
def render(key,title,body,desc=''):
 output=ctx['template'](key,title,body,desc or title+' — материалы Института традиционной восточной медицины на Арбате.')
 output=output.replace('style.css"','style.css?v=20261026-content"').replace('app.js"','app.js?v=20261026-content"')
 output=output.replace('</head>','<link rel="stylesheet" href="content.css?v=20261026-content"></head>')
 output=output.replace('<a href="tel:+74956916669">+7 (495) 691-66-69</a>','<a href="tel:+74956916672">+7 (495) 691-66-72</a>')
 return output
def write(filename,key,title,body,desc=''):(R/filename).write_text(render(key,E(title),body,desc),encoding='utf8')
primary={k:[] for k in ('services','methods','programs')}
for p in rows.values():
 path=p['path'];parts=path.strip('/').split('/')
 if len(parts)==2 and parts[0] in ('uslugi','metody-lecheniya','programmy') and text(p['content']):
  group={'uslugi':'services','metody-lecheniya':'methods','programmy':'programs'}[parts[0]];primary[group].append(p)
doctor_by_path={d['path']:d for d in doctors}
# Detailed profiles and articles: preserve source headings, lists, tables and images.
reserved={'clinic.html','services.html','methods.html','programs.html','doctors.html','prices.html','contacts.html'}
article_count=0
for path,p in rows.items():
 filename=mapping[path]
 if filename in reserved:continue
 if '/zabolevaniya/' in path:continue # empty or dated disease directory pages are not product content
 d=doctor_by_path.get(path); title=d['name'] if d else p['title']; key='doctors' if d else ('services' if path.startswith(('/uslugi','/metody')) else 'programs')
 back='doctors.html' if d else ('methods.html' if path.startswith('/metody') else 'services.html' if path.startswith('/uslugi') else 'programs.html')
 label='ВРАЧИ ИТВМ' if d else 'МАТЕРИАЛЫ ИНСТИТУТА'
 body=head(label,E(title),E(d['subtitle']) if d else 'Подробная информация о направлении, подходах и возможностях института.')
 image=assets.get(d.get('image','')) if d else None
 intro=f'<img class="profile-photo" src="{image}" alt="{E(title)}">' if image else ''
 bio=clean(p['content'])
 if not text(bio):bio='<p>Подробности о приёме и специализации уточните у администратора института.</p>'
 body+=f'<section class="section wrap compact"><a class="text-link" href="{back}">← Вернуться в раздел</a><div class="article-layout {"with-portrait" if image else ""}">{intro}<article class="source-content">{bio}{source_note(path)}<div class="article-actions">{button("Записаться на консультацию","contacts.html?"+urllib.parse.urlencode({"doctor" if d else "service":title})+"#appointment")}{button("Стоимость услуг","prices.html",True)}</div></article></div></section>'
 write(filename,key,title,body);article_count+=1
def excerpt(p):
 s=BeautifulSoup(p['content'],'html.parser')
 paragraphs=[x.get_text(' ',strip=True) for x in s.select('p') if len(x.get_text(' ',strip=True))>65]
 t=paragraphs[0] if paragraphs else text(p['content'])
 return t[:155].rsplit(' ',1)[0]+'…' if len(t)>155 else t
def catalog(items):return cards([(E(p['title']),E(excerpt(p)),mapping[p['path']]) for p in items])
search='''<label class="search-label" for="service-search">Поиск по услугам и методам</label><input id="service-search" type="search" placeholder="Например, неврология или массаж" autocomplete="off"><p id="search-status" role="status"></p>'''
body=head('МЕДИЦИНСКИЕ НАПРАВЛЕНИЯ','Знания. Диагностика.<br><em>Личный подход.</em>','Восемь направлений медицинской помощи — с подробным описанием услуг и возможностей института.')
body+='<section class="section wrap compact"><div class="section-tabs"><a href="#directions">Направления</a><a href="#treatments">Методы лечения</a><a href="prices.html">Прайс-лист ↗</a></div>'+search+'<div id="searchable"><div id="directions">'+catalog(primary['services'])+'</div><div class="section-head" id="treatments"><div><p class="eyebrow">L’ART DU SOIN</p><h2>Методы лечения</h2></div><p>Назначение процедур, показания и ограничения определяются на консультации специалиста.</p></div>'+catalog(primary['methods'])+'</div><p id="no-results" hidden>Ничего не найдено. Уточните запрос или свяжитесь с администратором.</p>'+source_note('/uslugi')+'</section>'
write('services.html','services','Услуги и методы',body)
write('methods.html','services','Методы лечения',head('ВОСТОЧНАЯ И ВОССТАНОВИТЕЛЬНАЯ МЕДИЦИНА','Древние практики.<br><em>Индивидуальный выбор.</em>','Подробные материалы института о методах лечения и восстановления.')+'<section class="section wrap compact">'+catalog(primary['methods'])+source_note('/metody-lecheniya')+'</section>')
write('programs.html','programs','Программы',head('CURAE PRESTIGE','Комплексные программы.<br><em>Ваш маршрут к здоровью.</em>','Восстановление, профилактика, мужское и женское здоровье, ANTI-AGE и термальное направление.')+'<section class="section wrap compact">'+catalog(primary['programs'])+'<div class="note"><p>Состав программы, длительность, стоимость и медицинские ограничения уточняются на консультации. Программа подбирается с учётом состояния пациента.</p></div>'+source_note('/programmy')+'</section>')
def doctorcard(d):
 im=assets.get(d.get('image',''));image=f'<img src="{im}" alt="{E(d["name"])}" loading="lazy">' if im else '<div class="portrait-placeholder" aria-hidden="true">'+''.join(x[0] for x in d['name'].split()[:2])+'</div>'
 return f'<a class="doctor-card" href="{mapping[d["path"]]}">{image}<div><h3>{E(d["name"])}</h3><p>{E(d["subtitle"])}</p><span class="text-link">Профиль специалиста ↗</span></div></a>'
write('doctors.html','doctors','Врачи',head('КОМАНДА ИНСТИТУТА','Люди, которым<br><em>вы доверяете здоровье.</em>','Специалисты ИТВМ: образование, профессиональный опыт и направления работы.')+f'<section class="section wrap compact"><p class="lead">{len(doctors)} специалистов в основном каталоге института. Выберите врача, чтобы познакомиться с его профессиональным опытом.</p><div class="doctor-grid">'+''.join(doctorcard(d) for d in doctors)+ '</div><p class="note">Доступность приёма и расписание выбранного специалиста уточняйте у администратора.</p>'+source_note('/konsultatsii-spetsialistov')+'</section>')
# Preserve every price row verbatim, grouping by its original accordion category.
price_soup=BeautifulSoup(rows['/price-list']['content'],'html.parser');groups={}
for tr in price_soup.select('tbody tr'):
 cells=tr.find_all(['td','th'],recursive=False)
 if len(cells)<2:continue
 name=cells[0].get_text(' ',strip=True);price=' / '.join(c.get_text(' ',strip=True) for c in cells[1:])
 labels=[]
 for ancestor in tr.parents:
  aid=ancestor.get('id')
  if aid and 'accordion-collapse' in ancestor.get('class',[]):
   b=price_soup.find('button',attrs={'aria-controls':aid})
   if b:labels.append(b.get_text(' ',strip=True))
 category=' · '.join(reversed(labels[:2])) or 'Медицинские услуги'
 if name:groups.setdefault(category,[]).append((name,price))
price_count=sum(map(len,groups.values()))
body=head('ПРАЙС-ЛИСТ ИНСТИТУТА','Стоимость услуг.<br><em>Всё по порядку.</em>','Консультации, диагностика, процедуры и восстановительные программы. Цены перенесены с основного сайта института.')
body+=f'<section class="section wrap compact"><p class="note">Прайс-лист с itvm.ru по состоянию на 26 октября 2026 года: {price_count} позиций. Перед записью уточните действующую стоимость и состав услуги у администратора.</p><label class="search-label" for="price-search">Найти услугу в прайс-листе</label><input type="search" id="price-search" placeholder="Название услуги, например массаж"><p role="status" id="price-status"></p><div class="price-groups">'
for i,(category,items) in enumerate(groups.items()):
 body+=f'<details class="price-group" {"open" if i==0 else ""}><summary>{E(category)}<span>{len(items)}</span></summary><div class="table-scroll"><table><thead><tr><th scope="col">Наименование услуги</th><th scope="col">Цена, ₽</th></tr></thead><tbody>'+''.join(f'<tr><td>{E(n)}</td><td>{E(v)}</td></tr>' for n,v in items)+'</tbody></table></div></details>'
body+='</div><p id="price-empty" hidden>Ничего не найдено. Попробуйте изменить запрос.</p>'+source_note('/price-list')+'</section>'
write('prices.html','prices','Цены',body)
# About the clinic, including the original history and patient information.
about=rows['/o-nas']
write('clinic.html','clinic','О клинике',head('ИНСТИТУТ ТРАДИЦИОННОЙ ВОСТОЧНОЙ МЕДИЦИНЫ','Восточная медицина.<br><em>В сердце Москвы.</em>','Одна из первых клиник восточной медицины в Москве. Клиническая база Института восточной медицины РУДН.')+'<section class="split"><img src="assets/clinic.webp" alt="Институт на Арбате"><div><p class="eyebrow">ФИЛИППОВСКИЙ ПЕРЕУЛОК, 18</p><h2>Внимание к человеку.<br>На каждом этапе.</h2><p>Современное диагностическое оборудование, сотрудничество с федеральными медицинскими центрами и индивидуальная схема помощи после диагностики.</p><p>Для пациентов на основном сайте указана бесплатная автомобильная парковка 24 часа. Порядок въезда уточните перед визитом.</p>'+button('Познакомиться с врачами','doctors.html')+'</div></section><section class="section wrap"><article class="source-content editorial">'+clean(about['content'])+source_note('/o-nas')+'</article></section>')
# Keep the established Palazzo landing while explaining which source services were announced.
palazzo=ctx['pages']['palazzo'][1]
palazzo=palazzo.replace('Бальнеология, талассотерапия, массажи и SPA-ритуалы','Массажи, питьевые курсы и ингаляционные процедуры')
palazzo+='<section class="section wrap"><p class="eyebrow">МАТЕРИАЛЫ ОСНОВНОГО САЙТА</p><h2>Термальное направление ИТВМ</h2><article class="source-content editorial">'+clean(rows['/programmy/pazzo-termale']['content'])+source_note('/programmy/pazzo-termale')+'</article><div class="note">Бальнеология, талассотерапия, обёртывания, соляная комната и шунгитовый грот на itvm.ru отмечены как «скоро открытие». Наличие конкретной процедуры уточните до визита.</div></section>'
write('palazzo.html','palazzo','Palazzo Termale & SPA',palazzo)
# Refresh existing pages and the homepage with the enriched information.
for key in ('home','longevity','contacts','privacy'):
 title,body,desc=ctx['pages'][key]
 if key=='home':
  extra='<section class="section wrap"><div class="section-head"><div><p class="eyebrow">СПЕЦИАЛИСТЫ ИТВМ</p><h2>Знания и опыт.<br><em>Личное внимание.</em></h2></div><p>Подробные профили врачей: образование, специализация и профессиональная практика.</p></div><div class="doctor-grid">'+''.join(doctorcard(d) for d in doctors[:3])+'</div><p>'+button('Все специалисты','doctors.html',True)+'</p></section>'
  extra+='<section class="section wrap compact"><div class="section-head"><div><p class="eyebrow">ОТКРЫТЫЙ ПРАЙС-ЛИСТ</p><h2>Планируйте визит<br><em>с уверенностью.</em></h2></div><p>Консультации, диагностика и процедуры — с ценами из прайс-листа института.</p></div>'+button('Посмотреть стоимость услуг','prices.html')+'</section>'
  body+=extra
 if key=='contacts':
  body=body.replace('href="tel:+74956916669">+7 (495) 691-66-69','href="tel:+74956916672">+7 (495) 691-66-72')
  body=body.replace('Наличие парковки и порядок въезда уточните при записи.','Для пациентов на itvm.ru указана бесплатная парковка 24 часа. Порядок въезда уточните при записи.')
  body+='<section class="section wrap compact"><div class="note"><h3>Консультация главного врача</h3><p>На основном сайте ИТВМ предлагается бесплатная консультация главного врача. Условия, формат и доступность уточните по телефону у администратора.</p>'+button('Уточнить условия консультации','tel:+74995209736')+'</div>'+source_note('/')+'</section>'
 write(ctx['link'](key),key,title,body,desc)
# Search and price controls are deliberately local: no visitor data is transmitted.
js=(R/'app.js').read_text(encoding='utf8')
marker='// ITVM_PRICE_SEARCH'
if marker in js:js=js.split(marker)[0]
js+='''\n// ITVM_PRICE_SEARCH
const priceSearch=document.querySelector('#price-search');
priceSearch?.addEventListener('input',()=>{const q=priceSearch.value.trim().toLocaleLowerCase('ru');let total=0;document.querySelectorAll('.price-group').forEach(group=>{let count=0;group.querySelectorAll('tbody tr').forEach(row=>{const match=row.textContent.toLocaleLowerCase('ru').includes(q);row.hidden=!match;if(match){count++;total++}});group.hidden=count===0;if(q)group.open=count>0;else group.open=group===document.querySelector('.price-group')});document.querySelector('#price-status').textContent=q?`Найдено услуг: ${total}`:'';document.querySelector('#price-empty').hidden=total!==0});
'''
(R/'app.js').write_text(js,encoding='utf8')
files=list(R.glob('*.html'))
(R/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>https://itvm.ru/ever-youth/'+f.name+'</loc></url>' for f in files)+'</urlset>',encoding='utf8')
(ROOT/'import-report.json').write_text(json.dumps({'date':'2026-10-26','pages':len(files),'articles':article_count,'doctors':len(doctors),'services':len(primary['services']),'methods':len(primary['methods']),'programs':len(primary['programs']),'price_rows':price_count,'price_groups':len(groups),'images':sum(bool(x) for x in assets.values()),'unavailable_source_pages':[p['path'] for p in data['pages'] if 'error' in p]},ensure_ascii=False,indent=2),encoding='utf8')
print('Built',len(files),'pages;',len(doctors),'doctors;',price_count,'prices in',len(groups),'groups;',article_count,'articles',flush=True)

