from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).parent/'vendor'))
import xlrd,openpyxl
OUT=Path(__file__).parent/'price-update';OUT.mkdir(exist_ok=True)
sources=[]
b=xlrd.open_workbook('C:/Users/Administrator/Desktop/прайс 05.10.2026.xls',formatting_info=True)
for sh in b.sheets():
 rows=[]
 for i in range(sh.nrows):
  values=sh.row_values(i)
  if any(v!='' for v in values):rows.append({'row':i+1,'values':values})
 sources.append({'file':'прайс 05.10.2026.xls','sheet':sh.name,'rows':rows,'merged':sh.merged_cells})
b=openpyxl.load_workbook('C:/Users/Administrator/Desktop/Направления института и врачи.xlsx',data_only=True,read_only=False)
for sh in b:
 rows=[]
 for i,row in enumerate(sh.iter_rows(values_only=True),1):
  if any(v is not None for v in row):rows.append({'row':i,'values':list(row)})
 sources.append({'file':'Направления института и врачи.xlsx','sheet':sh.title,'rows':rows,'merged':[str(x) for x in sh.merged_cells.ranges]})
(OUT/'source-rows.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2,default=str),encoding='utf8')
for sh in sources:
 print(json.dumps({'file':sh['file'],'sheet':sh['sheet'],'rows':len(sh['rows']),'columns':max((len(r['values']) for r in sh['rows']),default=0),'sample':sh['rows'][:12]},ensure_ascii=False,default=str))
