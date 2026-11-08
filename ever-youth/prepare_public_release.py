from pathlib import Path
import sys,json,re,shutil,html,xml.etree.ElementTree as ET
ROOT=Path(__file__).parent;OUT=ROOT/'site';WORK=ROOT/'release-20261108';BACK=WORK/'before';BACK.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'vendor'));from bs4 import BeautifulSoup
VERSION='public-20261108';URL='https://itvm.ru/ever-youth/'
for p in OUT.glob('*.html'):
 if not (BACK/p.name).exists():shutil.copy2(p,BACK/p.name)
phones='<a href="tel:+74956460773">+7 (495) 646-07-73</a><a href="tel:+74956916612">+7 (495) 691-66-12</a><a href="tel:+74956916672">+7 (495) 691-66-72</a>'
panel=f'<div class="release-booking-panel"><h3>Запись на приём</h3><p>Свяжитесь с администратором: он поможет выбрать специалиста, уточнит стоимость и время приёма.</p><div class="release-booking-links">{phones}<a href="https://wa.me/79175253695" target="_blank" rel="noopener noreferrer">Написать в WhatsApp</a></div></div>'
canonical=[]
for p in sorted(BACK.glob('*.html')):
 s=BeautifulSoup(p.read_text(encoding='utf8'),'html.parser')
 if s.html:s.html['lang']='ru'
 if s.select_one('meta[http-equiv="refresh"]'):
  if s.head:s.head.append(s.new_tag('meta',attrs={'name':'robots','content':'noindex, follow'}))
  (OUT/p.name).write_text(str(s),encoding='utf8');continue
 if p.name=='page170676909.html':
  records=s.select_one('#allrecords')
  for child in list(records.children):
   if getattr(child,'name',None) and child.get('id') not in ('t-header','t-footer'):child.decompose()
  content=BeautifulSoup(f'<main class="release-booking-page"><div class="release-booking-inner"><p class="release-eyebrow">ИТВМ Арбат</p><h1>Запись на приём</h1><p>Позвоните в клинику или напишите в WhatsApp. Администратор уточнит запрос и предложит время приёма.</p><div class="release-booking-links">{phones}<a href="https://wa.me/79175253695" target="_blank" rel="noopener noreferrer">WhatsApp: +7 (917) 525-36-95</a></div><p>Москва, Филипповский переулок, 18</p><a class="release-detail-link" href="page171084309.html">Контакты и схема проезда →</a><a class="release-detail-link" href="page178607409.html">Услуги и цены →</a></div></main>','html.parser')
  s.select_one('#t-header').insert_after(content)
 for atom in s.select('.tn-atom,p'):
  if re.sub(r'\s+',' ',atom.get_text(' ',strip=True))=='Заполните форму — администратор подтвердит время и сообщит детали подготовки к визиту.':
   atom.clear();atom.append('Свяжитесь с администратором, чтобы подобрать время приёма и уточнить подготовку к визиту.')
 for form in s.select('form'):
  if form.select_one('input[name*="hone"],input[type="tel"],input[data-tilda-rule="phone"]'):
   form['hidden']='';form['data-clinic-form-disabled']='true';form.insert_before(BeautifulSoup(panel,'html.parser'))
   for field in form.select('input,textarea,select,button'):field['disabled']=''
 title=s.title.get_text(' ',strip=True) if s.title else 'ИТВМ Арбат'
 descriptions={'index.html':'ИТВМ Арбат: консультации специалистов, диагностика, услуги и цены. Москва, Филипповский переулок, 18. Телефон: +7 (495) 646-07-73.','page170676909.html':'Запись на приём в ИТВМ Арбат по телефону и WhatsApp. Выбор специалиста и времени визита: +7 (495) 646-07-73.','page178607409.html':'Прайс ИТВМ Арбат от 05.10.2026: 1760 позиций, поиск услуг и анализов, фильтры по разделу и цене. Стоимость в рублях.'}
 description=descriptions.get(p.name,(title.replace(' | ИТВМ Арбат','')+'. Информация клиники, услуги, цены и запись на приём. Москва, Филипповский переулок, 18. +7 (495) 646-07-73.')[:170])
 if s.head:
  for e in s.select('meta[name="description"]'):e.decompose()
  s.head.append(s.new_tag('meta',attrs={'name':'description','content':description}))
  for key,value in [('og:title',title),('og:description',description),('og:url',URL+p.name)]:
   old=s.select_one(f'meta[property="{key}"]')
   if old:old['content']=value
   else:s.head.append(s.new_tag('meta',attrs={'property':key,'content':value}))
  s.head.append(s.new_tag('link',rel='stylesheet',href='public-release.css?v='+VERSION))
 if s.body:s.body.append(s.new_tag('script',src='public-release.js?v='+VERSION,defer=''))
 (OUT/p.name).write_text(str(s),encoding='utf8');canonical.append(p.name)
base=BeautifulSoup((OUT/'page170676909.html').read_text(encoding='utf8'),'html.parser');main=base.select_one('main');main.clear();main.append(BeautifulSoup('<div class="release-booking-inner"><p class="release-eyebrow">ИТВМ Арбат</p><h1>Страница не найдена</h1><p>Перейдите к услугам клиники или свяжитесь с администратором.</p><div class="release-booking-links"><a href="/ever-youth/index.html">На главную</a><a href="/ever-youth/page178642509.html">Услуги и цены</a><a href="tel:+74956460773">+7 (495) 646-07-73</a></div></div>','html.parser'))
base.title.string='Страница не найдена | ИТВМ Арбат'
for l in base.select('link[rel="canonical"]'):l.decompose()
base.head.append(base.new_tag('meta',attrs={'name':'robots','content':'noindex, follow'}));(OUT/'404.html').write_text(str(base),encoding='utf8')
ns='http://www.sitemaps.org/schemas/sitemap/0.9';ET.register_namespace('',ns);tree=ET.Element('{'+ns+'}urlset')
for name in canonical:
 child=ET.SubElement(tree,'{'+ns+'}url');ET.SubElement(child,'{'+ns+'}loc').text=URL+name
(OUT/'sitemap.xml').write_bytes(ET.tostring(tree,encoding='utf-8',xml_declaration=True))
(WORK/'preparation.json').write_text(json.dumps({'html':len(canonical),'aliases':len(list(BACK.glob('*.html')))-len(canonical),'booking':'phone_and_whatsapp_only','old_domain_root':'unchanged'},indent=2),encoding='utf8')
print((WORK/'preparation.json').read_text())
