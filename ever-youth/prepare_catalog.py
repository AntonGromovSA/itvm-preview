from pathlib import Path
import json,re,io
import openpyxl
from PIL import Image
ROOT=Path(__file__).parent;WORK=ROOT/'price-update';OUT=ROOT/'site'
sources=json.loads((WORK/'source-rows.json').read_text(encoding='utf8'))
def clean(v):return re.sub(r'\s+',' ',str(v or '')).strip()
catalog=[];excluded=[];center=None;group=None;heading='';old=False
def set_center(name):
 global center,group
 center={'id':'center-'+str(len(catalog)+1),'title':name,'groups':[]};catalog.append(center);group=None
def set_group(name):
 global group
 group={'title':name,'items':[],'open':False};center['groups'].append(group)
for row in sources[0]['rows']:
 n=row['row'];_,code,name,price,org=row['values'];code=clean(code);name=clean(name)
 if n<7:continue
 if not isinstance(price,(int,float)):
  if code:
   if code=='Общая':set_center('Продукция');set_group('DAIGO')
   elif code in ('Категория сложности','Аюрведа'):set_group(code)
   elif code.startswith('Индивидуальные аллергены') or code=='Витамины':
    center=next(c for c in catalog if c['title']=='Лаборатория ЭндоМедЛаб');set_group(code)
   else:set_center(code)
   heading='';old=False
  elif name:
   if name=='Старый':old=True
   elif name=='Новый':old=False;set_group('УЗИ')
   elif name=='УЗИ':set_group('УЗИ')
   else:set_group(name)
   heading=name
  continue
 if n in list(range(8,18))+[25,26] or old:
  excluded.append({'row':n,'name':name,'price':price,'reason':'служебная позиция' if not old else 'блок УЗИ «Старый»'});continue
 if group is None:set_group(center['title'])
 if center['title']=='Центр Инструментальной и функциональной диагностики' and group['title']=='УЗИ' and not name.lower().startswith(('узи','ультразв')):name='УЗИ '+name
 item={'name':name,'price':int(price) if price else None,'code':code,'source':'xls','sourceRow':n}
 group['items'].append(item)
catalog=[{**c,'groups':[g for g in c['groups'] if g['items']]} for c in catalog]
catalog=[c for c in catalog if c['groups']]
book=openpyxl.load_workbook('C:/Users/Administrator/Desktop/Направления института и врачи.xlsx');sheet=book.active
photo_rows={}
for im in sheet._images:
 row=im.anchor._from.row+1
 if row<41:continue
 image=Image.open(io.BytesIO(im._data())).convert('RGB');image.thumbnail((650,750))
 target='assets/doctor-source-row-'+str(row)+'.jpg';image.save(OUT/target,quality=87);photo_rows[row]=target
doctors=[];direction=''
for row in sources[1]['rows']:
 n=row['row'];v=row['values'];role=clean(v[0]);person=clean(v[2]);note=clean(v[3]);desc=clean(v[4])
 if not person:
  if n!=41:direction=role
  continue
 if n in (44,45,46):name=person.split(',')[0]
 else:name=person
 doctors.append({'sourceRow':n,'name':name,'direction':direction,'role':role,'priceNote':note,'description':desc,'photo':photo_rows.get(n)})
(WORK/'catalog-xls.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf8')
(WORK/'doctors-source.json').write_text(json.dumps(doctors,ensure_ascii=False,indent=2),encoding='utf8')
(WORK/'excluded-rows.json').write_text(json.dumps(excluded,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'positions':sum(len(g['items']) for c in catalog for g in c['groups']),'sections':len(catalog),'excluded':len(excluded),'doctors_rows':len(doctors),'portraits':len(photo_rows)},ensure_ascii=False))
