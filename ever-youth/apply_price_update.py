from pathlib import Path
import sys,re,json,html,shutil,urllib.parse
ROOT=Path(__file__).parent;sys.path.insert(0,str(ROOT/'vendor'))
from bs4 import BeautifulSoup
OUT=ROOT/'site';WORK=ROOT/'price-update';BASE=WORK/'site-before';BASE.mkdir(exist_ok=True)
VER='prices-20261028'
catalog=json.loads((WORK/'catalog-xls.json').read_text(encoding='utf8'))
doctors=json.loads((WORK/'doctors-source.json').read_text(encoding='utf8'))
for p in OUT.glob('*.html'):
 if not (BASE/p.name).exists():shutil.copy2(p,BASE/p.name)
byrow={i['sourceRow']:i for c in catalog for g in c['groups'] for i in g['items']}
# Explicitly mapped rows retain physician, age and procedure distinctions from the source.
doctor_rows={44:[1828,1829,1830],45:[1836,1837,1838],46:[149,150],50:[1775,1780,1773],55:[210,232],56:[241,242,243,244,248,249],58:[1849,1850,1820],59:[224,225,226],61:[181,182,183,184,185],62:[251,252,253,254,255],64:[165,166,167,168],66:[220],68:[207,218],70:[1589,1590],71:[1595,1596,1597],73:[1735,1736,1738,1739,1740,1741],75:[1712,1713,1714,1715,1716],76:[1719,1720,153,163],78:[1530,1531],80:list(range(1426,1434)),81:[1530,1531],83:[132,154],84:[37,38,39,40,41,55,59],86:[119,120,122],87:[119,120,121,122],89:[1847],90:[1737],92:list(range(173,180)),93:[148],94:list(range(187,194)),96:[87,92,93,198],98:[87,92,93,80]}
for d in doctors:d['prices']=[byrow[n] for n in doctor_rows.get(d['sourceRow'],[]) if n in byrow]
for d in doctors:
 if d['sourceRow']==96:d['prices']=[i for i in d['prices'] if i['sourceRow']!=198]
def esc(t):return html.escape(str(t))
def money(v):return f'{v:,}'.replace(',',' ')+' ₽' if v is not None else 'Стоимость уточняйте'
def price_url(q='',center=''):
 return 'page178607409.html?v='+VER+('&q='+urllib.parse.quote(q) if q else '')+('&center='+center if center else '')+'#price-list'
def load(name):return BeautifulSoup((BASE/name).read_text(encoding='utf8'),'html.parser')
def save(s,name):
 for link in s.select('link[href^="price-update.css"]'):link.decompose()
 for script in s.select('head script[src^="assets/"][async]'):
  del script['async'];script['defer']=''
 if s.head:s.head.append(s.new_tag('link',rel='stylesheet',href='price-update.css?v='+VER))
 (OUT/name).write_text(str(s).replace('contacts-20261028',VER),encoding='utf8')
def section(title,body,kicker='Услуги института'):
 return BeautifulSoup(f'<section class="itvm-addition ey-source-section"><div class="itvm-addition-inner"><p class="itvm-kicker">{esc(kicker)}</p><h1>{esc(title)}</h1>{body}</div></section>','html.parser')
def insert_before_footer(s,content):
 foot=s.select_one('#t-footer')
 if foot:foot.insert_before(content)
 else:s.body.append(content)
def clear_content(s):
 allrec=s.select_one('#allrecords')
 for el in list(allrec.children):
  if getattr(el,'name',None) and el.get('id') not in ('t-header','t-footer'):el.decompose()
def table(items):
 return '<div class="ey-source-table"><table><thead><tr><th>Услуга</th><th>Стоимость</th></tr></thead><tbody>'+''.join(f'<tr data-source-row="{i["sourceRow"]}"><td>{esc(i["name"])}</td><td>{money(i["price"])}</td></tr>' for i in items)+'</tbody></table></div>'
# Replace the single source of all interactive price rows, preserving the tested UI.
s=load('page178607409.html');script=next(x for x in s.select('script:not([src])') if 'var catalog = [' in x.get_text())
js=script.get_text();start=js.index('    var catalog = [');end=js.index('];',start)+2
js=js[:start]+'    var catalog = '+json.dumps(catalog,ensure_ascii=False)+';'+js[end:]
js=js.replace('return numberFormatter.format(value) + " ₽";','return value === null ? "Стоимость уточняйте" : numberFormatter.format(value) + " ₽";')
js=js.replace('values.push(value);','if (value !== null) values.push(value);')
js=js.replace('row.dataset.prices.split(",").map(Number)','row.dataset.prices ? row.dataset.prices.split(",").map(Number) : []')
js=js.replace('var priceMatches = !invalidBounds && prices.some(function (price) {','var priceMatches = !invalidBounds && ((prices.length === 0 && minValue === null && maxValue === null) || prices.some(function (price) {')
js=js.replace('return matchesMinimum && matchesMaximum;\n            });','return matchesMinimum && matchesMaximum;\n            }));')
js=js.replace('item.name,\n                currentSubsection,','item.name,\n                item.code || "",\n                currentSubsection,')
js=js.replace('    rememberManualAccordionState();','    rememberManualAccordionState();\n    var initial = new URLSearchParams(location.search);\n    searchInput.value = initial.get("q") || "";\n    if (initial.get("center")) centerSelect.value = initial.get("center");')
js=js.replace('["услуга", "услуги", "услуг"]','["позиция", "позиции", "позиций"]').replace('["центр", "центра", "центров"]','["раздел", "раздела", "разделов"]').replace('["центре", "центрах", "центрах"]','["разделе", "разделах", "разделах"]')
script.string=js
price=s.select_one('.itp-price');price['id']='price-list'
for label in price.select('label,span,option'):
 if label.get_text(strip=True)=='Центр клиники':label.string='Раздел прайса'
 if label.get_text(strip=True)=='Все центры':label.string='Все разделы'
for p in price.select('p'):
 t=p.get_text(' ',strip=True)
 if 'Полный перечень медицинских услуг' in t:p.string='Прайс от 05.10.2026'
 elif 'Все суммы указаны в рублях.' in t:p.string='Стоимость указана в рублях. Состав и длительность процедуры приведены в названии услуги.'
 elif 'Состав услуги и итоговая стоимость' in t:p.string='Стоимость услуг — по прейскуранту от 05.10.2026. Позиции без установленной цены уточняйте у администратора.'
save(s,'page178607409.html')
# A complete, browsable catalogue points to the same prices instead of duplicating rates.
s=load('page178642509.html');clear_content(s)
cards=''.join(f'<a class="ey-service-card" href="{price_url(center=c["id"])}"><h2>{esc(c["title"])}</h2><p>{sum(len(g["items"]) for g in c["groups"])} позиций</p><span>Услуги и цены →</span></a>' for c in catalog)
body='<p>Консультации специалистов, диагностика, лечебные и восстановительные процедуры. Выберите раздел или найдите услугу в полном прайс-листе.</p><a class="itvm-link-button" href="'+price_url()+'">Открыть полный прайс-лист</a><div class="ey-service-grid">'+cards+'</div>'
insert_before_footer(s,section('Услуги и цены',body));save(s,'page178642509.html')
# Group the source's rows by person, retaining all specialties without inventing biographies.
people={}
existing=[]
for p in BASE.glob('doctor-*.html'):
 ss=load(p.name)
 if not ss.select_one('meta[http-equiv="refresh"]') and ss.title:existing.append((p.name,ss.title.get_text()))
for d in doctors:
 key=d['name'];person=people.setdefault(key,{'name':key,'entries':[],'photo':d['photo'],'url':None})
 person['entries'].append(d)
 if not person['photo']:person['photo']=d['photo']
 lastname=key.split()[0]
 matches=[(url,title) for url,title in existing if lastname.lower() in title.lower()]
 if matches:person['url']=matches[0][0]
 else:person['url']='specialist-source-'+str(d['sourceRow'])+'.html'
for person in people.values():
 url=person['url'];existing_file=url.startswith('doctor-') and (BASE/url).exists();s=load(url if existing_file else 'doctor-chekunov-oleg-vladimirovich.html')
 if not existing_file:clear_content(s);s.title.string=person['name']+' | ИТВМ Арбат'
 entries=person['entries'];prices=[];seen=set()
 for d in entries:
  for item in d['prices']:
   if item['sourceRow'] not in seen:seen.add(item['sourceRow']);prices.append(item)
 body=('<img class="itvm-portrait" src="'+person['photo']+'" alt="'+esc(person['name'])+'">' if not existing_file and person['photo'] else '')
 body+=''.join('<p>'+esc(d['direction'].capitalize())+'. '+esc(re.sub(r',?\s*портативный мрт\.?','',d['role'],flags=re.I).capitalize())+'</p>' for d in entries)
 body+=table(prices) if prices else '<p>Стоимость зависит от выбранного исследования или процедуры. Уточните назначение и цену у администратора.</p>'
 body+='<a class="itvm-link-button" href="'+price_url()+'">Все услуги и цены</a>'
 block=section(person['name'] if not existing_file else 'Приём и услуги',body,'Специалисты института')
 if existing_file:
  for el in s.select('p'):
   if 'Стоимость приема 6000 рублей' in el.get_text():el.string='Продолжительность сеанса — 60 минут. Возраст — от 9 лет.'
  first=s.select_one('.itvm-addition')
  if first:first.insert_after(block)
  else:insert_before_footer(s,block)
 else:insert_before_footer(s,block)
 save(s,url)
# Add the current direction-to-specialist directory; preserve original detailed profiles.
s=load('page172957109.html')
groups={}
for person in people.values():
 directions=list(dict.fromkeys(d['direction'] for d in person['entries']))
 for direction in directions:groups.setdefault(direction,[]).append(person)
body='<p>Специалисты и направления приёма. На страницах врачей приведены услуги и цены из прейскуранта клиники.</p>'
for direction,ps in groups.items():
 body+='<h2>'+esc(direction.capitalize())+'</h2><div class="ey-doctor-grid">'
 for p in ps:
  body+=f'<a class="ey-doctor-card" href="{p["url"]}?v={VER}">'+(f'<img src="{p["photo"]}" alt="" loading="lazy">' if p['photo'] else '')+'<span>'+esc(p['name'])+'</span></a>'
 body+='</div>'
block=section('Направления и специалисты',body,'Приём в институте')
header=s.select_one('#t-header');header.insert_after(block);save(s,'page172957109.html')
# Remove unverified marketing tariffs from every remaining page.
for p in BASE.glob('*.html'):
 if p.name in ('page178607409.html','page178642509.html','page172957109.html') or any(v['url']==p.name for v in people.values()):continue
 s=load(p.name)
 for el in list(s.select('.tn-atom,p,span,div')):
  if el.find(['p','div']):continue
  t=el.get_text(' ',strip=True)
  if not re.search(r'\d[\d\s\u00a0]*\s*(?:₽|руб(?:лей|\b))',t,re.I):continue
  if p.name=='doctor-chekunov-oleg-vladimirovich.html':continue
  el.clear();el.append(re.sub(r'(?:от\s*)?\d[\d\s\u00a0]*\s*(?:₽|рублей|руб\.?)(?:\s*за\s*сеанс)?\*?', 'Стоимость уточняйте',t,flags=re.I))
 save(s,p.name)
# Link specialty pages to the authoritative matching section.
specialties={'page182655909.html':['Центр Инструментальной и функциональной диагностики','Лаборатория ЭндоМедЛаб'],'page182669909.html':['Центр Эстетической медицины'],'page182686609.html':['Центр Реабилитации и восстановительной медицины'],'page182699009.html':['Центр Женского здоровья'],'page182706809.html':['Центр Превентивной медицины'],'page182714209.html':['Центр Превентивной медицины'],'page182718709.html':['Центр Превентивной медицины'],'page182725309.html':['Центр Превентивной медицины'],'page171080109.html':['Центр СПА'],'page171071209.html':['Центр СПА']}
for name,titles in specialties.items():
 s=BeautifulSoup((OUT/name).read_text(encoding='utf8'),'html.parser')
 body=''.join('<a class="itvm-link-button" href="'+price_url(center=c['id'])+'">'+esc(c['title'])+': услуги и цены</a> ' for c in catalog if c['title'] in titles)
 insert_before_footer(s,section('Стоимость услуг',body,'Прайс от 05.10.2026'));save(s,name)
# Include every service in the site-wide search with a direct filtered result.
index=[]
for p in OUT.glob('*.html'):
 s=BeautifulSoup(p.read_text(encoding='utf8'),'html.parser')
 if s.select_one('meta[http-equiv="refresh"]'):continue
 title=s.title.get_text(' ',strip=True) if s.title else p.stem
 for e in s.select('script,style,header,footer'):e.decompose()
 index.append({'title':title,'url':p.name+'?v='+VER,'text':re.sub(r'\s+',' ',s.get_text(' ',strip=True))[:32000]})
for c in catalog:
 for g in c['groups']:
  for i in g['items']:index.append({'title':i['name'],'url':price_url(q=i['name'],center=c['id']),'text':c['title']+' '+g['title']+' '+i['code']+' '+money(i['price'])})
(OUT/'replica-search.json').write_text(json.dumps(index,ensure_ascii=False),encoding='utf8')
(OUT/'price-catalog.json').write_text(json.dumps(catalog,ensure_ascii=False),encoding='utf8')
for p in OUT.glob('*.html'):
 ss=BeautifulSoup(p.read_text(encoding='utf8'),'html.parser');changed=False
 for select in ss.select('select'):
  names=[o.get_text() for o in select.select('option')]
  if not any('Десятерик' in t for t in names):continue
  for person in people.values():
   if person['name'] not in names:
    option=ss.new_tag('option');option.string=person['name'];select.append(option);changed=True
 if changed:p.write_text(str(ss),encoding='utf8')
(WORK/'applied-report.json').write_text(json.dumps({'positions':len(byrow),'doctorRows':len(doctors),'sourceDoctors':len(people),'sourcePriority':'прайс 05.10.2026.xls','catalogueSections':len(catalog),'searchEntries':len(index)},ensure_ascii=False,indent=2),encoding='utf8')
print((WORK/'applied-report.json').read_text(encoding='utf8'))
