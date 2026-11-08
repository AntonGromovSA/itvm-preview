import prices from '../data/prices.json';
import people from '../data/doctors.json';
import type {ClinicPage,PriceSection} from './types';
const entries=import.meta.glob('../data/pages/*.json',{eager:true,import:'default'});
export const pages=Object.values(entries) as ClinicPage[];
export const catalog=prices as PriceSection[];
export const doctors=people;
export const amount=(price:number|null)=>price===null?'Стоимость уточняйте':new Intl.NumberFormat('ru-RU').format(price)+' ₽';
export const priceByRow=new Map(catalog.flatMap(c=>c.groups.flatMap(g=>g.items)).map(i=>[i.sourceRow,i]));
export function pageByName(name:string){const page=pages.find(p=>p.name===name);if(!page)throw new Error('Unknown page: '+name);return page;}
export const photo=(page:ClinicPage)=>page.portrait||page.sections.flatMap(s=>s.images)[0];
export function searchIndex(){
 const index=pages.filter(p=>!p.alias&&p.name!=='404.html').map(p=>({title:p.title,url:p.name,text:(p.kind==='home'?'Институт традиционной восточной медицины на Арбате. Консультации, диагностика, восстановление, Palazzo Termale.':p.kind==='doctors'?doctors.map(d=>d.name+' '+d.role).join(' '):[p.description,...p.sections.map(s=>s.title+' '+s.html.replace(/<[^>]+>/g,' ')),...p.priceRows.map(id=>{const i=priceByRow.get(id);return i?i.name+' '+amount(i.price):'';})].join(' ')).replace(/\s+/g,' ')}));
 for(const c of catalog)for(const g of c.groups)for(const item of g.items)index.push({title:item.name,url:'page178607409.html?q='+encodeURIComponent(item.name)+'&center='+c.id+'#price-list',text:c.title+' '+g.title+' '+item.code+' '+amount(item.price)});
 return index;
}
