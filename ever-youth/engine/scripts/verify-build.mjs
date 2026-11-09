import{readFile,readdir,stat,writeFile,mkdir}from'node:fs/promises';import{join,resolve}from'node:path';import{load}from'cheerio';import assert from'node:assert/strict';
const built=resolve('dist'),baseline=resolve('../site');const json=async p=>JSON.parse(await readFile(p,'utf8'));
const pages=await Promise.all((await readdir('src/data/pages')).map(n=>json('src/data/pages/'+n)));const catalog=await json('src/data/prices.json');const people=await json('src/data/doctors.json');
assert.deepEqual(await json('dist/price-catalog.json'),catalog);assert.deepEqual(catalog,await json('../site/price-catalog.json'),'Approved tariff changed');
const items=catalog.flatMap(c=>c.groups.flatMap(g=>g.items));const priceMap=new Map(items.map(i=>[i.sourceRow,i]));assert.equal(items.length,1760);assert.equal(catalog.length,14);assert.equal(items.filter(i=>i.price===null).length,2);
const normalize=s=>s.replace(/\s+/g,'');const amount=p=>p===null?'Стоимость уточняйте':new Intl.NumberFormat('ru-RU').format(p)+' ₽';let references=0;let biographies=0;const errors=[];const htmlSizes=[];
for(const page of pages){
 const html=await readFile(join(built,page.name),'utf8');const $=load(html);htmlSizes.push({page:page.name,bytes:Buffer.byteLength(html)});
 assert.ok(!/tilda|tn-atom|t396__|t_onReady|data-record-type|t-slds/i.test(html),'Vendor markup remains: '+page.name);
 assert.equal($('h1').length,1,'One main heading: '+page.name);assert.equal($('header.site-header').length,1);assert.equal($('footer.site-footer').length,1);
 assert.ok(!$('style').length,'Styles should be cached as separate files: '+page.name);assert.ok(!$('form[action]').length,'Unexpected form submission');
 const ids=$('[id]').map((_,n)=>$(n).attr('id')).get();assert.equal(new Set(ids).size,ids.length,'Duplicate ids: '+page.name);
 if(page.alias)assert.ok($('meta[http-equiv="refresh"]').attr('content')?.includes(page.alias));
 for(const tr of $('tr[data-price-row]').toArray()){const item=priceMap.get(Number($(tr).attr('data-price-row')));assert.ok(item);const cells=$(tr).find('td');assert.equal(normalize(cells.first().find('.service-name').length?cells.first().find('.service-name').text():cells.first().text()),normalize(item.name));assert.equal(normalize(cells.last().text()),normalize(amount(item.price)));}
 if(page.kind==='doctor'){
  assert.ok(people.some(p=>p.href===page.name),'Profile missing from native directory');
  const old=load(await readFile(join(baseline,page.name),'utf8'));const current=normalize($('main').text());
  for(const para of old('section#details p,section#details li').toArray()){
   const t=normalize(old(para).text());if(t.length>55&&!/Профильиобразование/.test(t)){assert.ok(current.includes(t),'Biography paragraph missing: '+page.name+' '+t.slice(0,70));biographies++;}
  }
  assert.equal($('tr[data-price-row]').length,page.priceRows.length,'Profile tariff rows missing');
 }
 for(const n of $('[src],[href],[poster],[srcset]').toArray()){
  const el=$(n);const values=[el.attr('src'),el.attr('href'),el.attr('poster'),...(el.attr('srcset')||'').split(',').map(s=>s.trim().split(/\s+/)[0])].filter(Boolean);
  for(let value of values){if(/^(?:[a-z]+:|\/\/|#)/i.test(value))continue;let path=decodeURIComponent(value.split(/[?#]/)[0]);if(!path)continue;if(path.startsWith('/ever-youth/'))path=path.slice(12);else if(path.startsWith('/'))continue;references++;await stat(join(built,path)).catch(()=>errors.push(page.name+': '+path));}
 }
}
assert.deepEqual(errors,[],'Missing public references');assert.equal(pages.length,121);assert.equal(load(await readFile('dist/page178607409.html','utf8'))('tr[data-price-row]').length,1760);
const search=await json('dist/replica-search.json');assert.equal(search.filter(i=>i.url.includes('&center=')).length,1760);assert.equal(people.length,40);
const files=async dir=>(await Promise.all((await readdir(dir,{withFileTypes:true})).map(d=>d.isDirectory()?files(join(dir,d.name)):join(dir,d.name)))).flat();
const output=await files(built);assert.ok(output.every(p=>!/[\\/]assets[\\/]|\.ttf$|component-tests|\.php$|\.csv$|\.xls/i.test(p)),'Old assets, lab or private source in output');
for(const f of output.filter(p=>/\.(css|js)$/.test(p)))assert.ok(!/tilda|tn-atom|t396__|static\.tildacdn/i.test(await readFile(f,'utf8')),'Vendor code remains: '+f);
let preservedCanvasBlocks=0;
for(const name of Object.keys(await json('src/data/compositions.json'))){
 const old=load(await readFile(join(baseline,name),'utf8')),current=load(await readFile(join(built,name),'utf8'));
 // Explicitly requested homepage removals; all remaining compositions retain their structure.
 if(['page171084309.html','page178631709.html'].includes(name))continue; // Rebuilt native contact/about pages, verified below.
 if(name==='index.html'){old('#rec2936376001').remove();old('#rec2936342401 .tn-group[data-group-id="2026080923360000010"]').remove();old('[data-group-id="2026081000075000010"]').closest('[data-record-type]').remove();}
 for(const block of old('#allrecords [data-record-type="396"]').toArray()){
  if(old(block).closest('#t-header,#t-footer').length)continue;
  const id=old(block).attr('id'),found=current('#'+id);assert.equal(found.length,1,'Authored block missing: '+name+' '+id);
  assert.equal(found.find('.node-atom').length,old(block).find('.tn-atom').length,'Authored composition flattened: '+name+' '+id);
  assert.equal(found.find('.node-group').length,old(block).find('.tn-group').length,'Authored group missing: '+name+' '+id);preservedCanvasBlocks++;
 }
}
assert.deepEqual(await readFile('dist/brand/crest.png'),await readFile(join(baseline,'assets/a897742453b07a7c2ad9.png')),'Original crest must remain unchanged');
for(const f of output.filter(p=>p.endsWith('.css'))){
 for(const match of (await readFile(f,'utf8')).matchAll(/url\(\s*(?:"([^"]*)"|'([^']*)'|([^)]*))\s*\)/g)){
  const value=(match[1]??match[2]??match[3]).trim();if(/^(?:[a-z]+:|\/\/|#)/i.test(value))continue;
  const path=value.startsWith('/ever-youth/')?join(built,value.slice(12)):resolve(f,'..',value);
  await stat(path).catch(()=>errors.push('CSS '+f+': '+value));
 }
}
assert.deepEqual(errors,[],'Missing CSS resources');
const home=load(await readFile('dist/index.html','utf8'));const shell=[];for(const n of home('script[src],link[rel="stylesheet"]').toArray()){const path=(home(n).attr('src')||home(n).attr('href')).replace('/ever-youth/','');shell.push({path,bytes:(await stat(join(built,path))).size});}
assert.equal(home('#rec2936376001').length,0,'Duplicate homepage metrics remain');
assert.equal(home('#rec2936342401 [data-group-id="2026080923360000029"]').length,0,'Obsolete Roman shortcuts remain');
assert.equal(home('#institute-metrics.home-advantages').length,1,'Institute advantages missing');
assert.equal(home('.advantages-list>li').length,4,'Expected four patient-facing advantages');
assert.equal(home('#home-programmes .programme-feature').length,2,'Readable programme panels missing');
assert.equal(home('#home-programmes a[href="exovesicles.html"]').length,1,'New science page inaccessible');
const contact=load(await readFile('dist/page171084309.html','utf8'));assert.equal(contact('#appointment').length,1);assert.equal(contact('#directions').length,1);assert.equal(contact('nav a[href="page171084309.html"]').length,1);assert.equal(contact('nav a[href*="#appointment"]').length,0);
const about=load(await readFile('dist/page178631709.html','utf8'));for(const id of ['institute','care','first-visit','team','clinic-video','documents'])assert.equal(about('#'+id).length,1,'About section missing: '+id);assert.equal(about('.about-directions>a').length,6);assert.equal(about('.about-team article').length,3);assert.equal(about('.about-doc-grid a').length,3);assert.equal(about('#clinic-video video[controls][playsinline]').length,1);assert.ok(about('main').text().indexOf('Кто принимает')<about('main').text().indexOf('Лицензия и реквизиты'));
const exo=load(await readFile('dist/exovesicles.html','utf8'));assert.equal(exo('.science-step').length,4);assert.equal(exo('[data-motion-toggle]').length,1);assert.equal(exo('.scene-fallback').length,1);assert.equal(exo('#evidence .science-reading').length,5,'Extended research sections missing');assert.equal(exo('.science-faq details').length,4,'Original FAQ missing');assert.ok(exo('#evidence').text().includes('митохондри'));assert.equal(exo('a[href="page171084309.html#appointment"]').length>0,true);
assert.equal(home('.advantages-motion video[autoplay][muted][playsinline]').length,1,'Original five-element motion missing');
assert.equal(home('header .brand small').length,0,'Unrequested brand subtitle remains');
assert.ok(!home('script[src]').toArray().some(n=>/three|react|ModelViewer/.test(home(n).attr('src'))),'Heavy island loaded on homepage');
assert.equal(home('video.original-background-video[autoplay][muted][playsinline] source[src="video/30027af1c993f1fac795.mp4"]').length,1,'Original background video missing');
console.log('Preserved authored composition blocks: '+preservedCanvasBlocks);
const report={pages:pages.length,doctors:40,priceItems:1760,tariffUnchanged:true,biographyParagraphsPreserved:biographies,vendorRuntimeRemoved:true,localReferences:references,searchEntries:search.length,homepageBytes:(await stat('dist/index.html')).size,homepageCssAndJs:shell,largestHtml:htmlSizes.sort((a,b)=>b.bytes-a.bytes).slice(0,4),errors};await mkdir('reports',{recursive:true});await writeFile('reports/verification.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));
