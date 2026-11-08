import {readFile,readdir,stat,writeFile,mkdir} from 'node:fs/promises';
import {resolve,join,relative} from 'node:path';
import {load} from 'cheerio';
import assert from 'node:assert/strict';
const root=process.cwd();const built=resolve(root,'dist');const baseline=resolve(root,'../site');
const catalog=JSON.parse(await readFile('src/data/prices.json','utf8'));
const outputCatalog=JSON.parse(await readFile('dist/price-catalog.json','utf8'));
assert.deepEqual(outputCatalog,catalog,'Built tariff must equal the editable source');
const priceItems=catalog.flatMap(c=>c.groups.flatMap(g=>g.items));
assert.equal(priceItems.length,1760);assert.equal(new Set(priceItems.map(i=>i.sourceRow)).size,1760);
assert.equal(priceItems.filter(i=>i.price===null).length,2);
const oldCatalog=JSON.parse(await readFile(join(baseline,'price-catalog.json'),'utf8'));assert.deepEqual(catalog,oldCatalog,'Migration must not change prices or services');
const htmlNames=(await readdir(baseline)).filter(n=>n.endsWith('.html'));
// Astro adds whitespace between component boundaries; compare the actual characters.
const normalize=text=>text.replace(/\s+/g,'');
const issues=[];const pages=[];
for(const name of htmlNames){
 const before=load(await readFile(join(baseline,name),'utf8'));const after=load(await readFile(join(built,name),'utf8'));
 before('script,style').remove();after('script,style').remove();
 if(normalize(before('body').text())!==normalize(after('body').text()))issues.push({page:name,issue:'visible-text-changed'});
 for(const selector of ['#t-header','#t-footer']){
  if(before(selector).length!==after(selector).length)issues.push({page:name,issue:'shared-component-missing',selector});
 }
 const urls=$=> $('a[href],img[src],video[src],source[src],iframe[src]').map((_,e)=>$(e).attr('href')||$(e).attr('src')).get();
 if(JSON.stringify(urls(before))!==JSON.stringify(urls(after)))issues.push({page:name,issue:'link-or-media-changed'});
 const records=$=>$('.t-rec[id]').map((_,e)=>$(e).attr('id')).get();
 if(JSON.stringify(records(before))!==JSON.stringify(records(after)))issues.push({page:name,issue:'visual-records-changed'});
 pages.push(name);
}
assert.equal(issues.length,0,JSON.stringify(issues.slice(0,20)));
const search=JSON.parse(await readFile('dist/replica-search.json','utf8'));
assert.equal(search.filter(i=>i.url.includes('&center=')).length,1760);
for(const name of htmlNames){
 const html=await readFile(join(built,name),'utf8');assert.ok(!html.includes('__CLINIC_'),'Unresolved content token in '+name);
 const $=load(html);for(const element of $('[src],[href]').toArray()){
  const value=$(element).attr('src')||$(element).attr('href');if(!value||/^(?:[a-z]+:|\/\/|#)/i.test(value))continue;
  let path=decodeURIComponent(value.split(/[?#]/)[0]);if(!path)continue;
  if(path.startsWith('/ever-youth/'))path=path.slice('/ever-youth/'.length);else if(path.startsWith('/'))continue;
  await stat(join(built,path)).catch(()=>{throw new Error('Missing local asset '+name+': '+path)});
 }
}
assert.ok(!(await readdir(built)).includes('component-lab.html'),'Development lab must not be deployed');
await stat(join(built,'component-tests/interactive.html')).then(()=>{throw new Error('Component lab leaked into production')},()=>{});
await mkdir('reports',{recursive:true});await writeFile('reports/verification.json',JSON.stringify({pages:pages.length,visibleTextUnchanged:true,linksAndMediaUnchanged:true,visualRecordIdsUnchanged:true,priceItems:1760,tariffUnchanged:true,searchEntries:search.length,issues},null,2));
console.log(JSON.stringify({pages:pages.length,priceItems:1760,issues:0,visualTextLinksAndMedia:'unchanged'}));
