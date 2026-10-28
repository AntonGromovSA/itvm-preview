from pathlib import Path
import sys,re,json
ROOT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'vendor'))
from bs4 import BeautifulSoup
OUT=ROOT/'site';VERSION='contacts-20261028'
phones=[('+7 (495) 646-07-73','+74956460773'),('+7 (495) 691-66-12','+74956916612'),('+7 (495) 691-66-72','+74956916672')]
links=''.join(f'<a href="tel:{n}">{label}</a>' for label,n in phones)
social='<a href="https://wa.me/79175253695" target="_blank" rel="noopener noreferrer">WhatsApp: +7 (917) 525-36-95</a><a href="https://vk.com/itvm_arbat" target="_blank" rel="noopener noreferrer">ВКонтакте</a>'
contact=f'''<details class="ey-more ey-contact"><summary aria-label="Телефоны и соцсети"><svg viewBox="0 0 24 24" width="21" height="21" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M7 3H4a1 1 0 0 0-1 1c0 9.4 7.6 17 17 17a1 1 0 0 0 1-1v-3l-5-2-2 2a14 14 0 0 1-7-7l2-2Z"/></svg></summary><div><p>Связаться с клиникой</p>{links}{social}</div></details>'''
changed=0
for p in OUT.glob('*.html'):
 raw=p.read_text(encoding='utf8')
 for pat in (r'\+7\s*\(499\)\s*520[-– ]97[-– ]36',r'\+7\s*\(495\)\s*691[-– ]66[-– ]69',r'\+7\s*\(920\)\s*689[-– ]11[-– ]11'):
  raw=re.sub(pat,phones[0][0],raw)
 for digits in ('74995209736','74956916669','79206891111','74950000000','74951234567'):raw=raw.replace(digits,'74956460773')
 raw=raw.replace('https://wa.me/qr/WGRISTDY2KDZH1','https://wa.me/79175253695')
 s=BeautifulSoup(raw,'html.parser')
 for a in s.select('a[href^="tel:"]'):
  digits=re.sub(r'\D','',a['href'])
  if len(digits)==11 and digits[0] in '78':a['href']='tel:+7'+digits[1:]
  if digits in ('74950000000','74951234567'):a['href']='tel:+74956460773'
  visible=re.sub(r'\D','',a.get_text())
  if len(visible)==11 and visible[0] in '78':a['href']='tel:+7'+visible[1:]
 for e in s.select('.ey-contact,.ey-contact-strip'):e.decompose()
 actions=s.select_one('.ey-actions')
 if actions:actions.insert(0,BeautifulSoup(contact,'html.parser'))
 footer=s.select_one('#t-footer')
 if footer:
  strip=BeautifulSoup(f'<section class="ey-contact-strip" aria-label="Телефоны и соцсети клиники"><span>Связаться с клиникой</span><div>{links}{social}</div></section>','html.parser');footer.append(strip)
 output=str(s).replace('identity-20261028',VERSION)
 p.write_text(output,encoding='utf8');changed+=1
items=[]
for p in OUT.glob('*.html'):
 s=BeautifulSoup(p.read_text(encoding='utf8'),'html.parser')
 if s.select_one('meta[http-equiv="refresh"]'):continue
 title=s.title.get_text(' ',strip=True) if s.title else p.stem
 for e in s.select('script,style,header,footer'):e.decompose()
 items.append(dict(title=title,url=p.name+'?v='+VERSION,text=re.sub(r'\s+',' ',s.get_text(' ',strip=True))[:32000]))
(OUT/'replica-search.json').write_text(json.dumps(items,ensure_ascii=False),encoding='utf8')
print(json.dumps({'pages':changed,'indexed':len(items)}))
