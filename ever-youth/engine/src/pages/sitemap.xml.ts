import { pages } from '../lib/content';
export const GET = () => new Response('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + pages.filter(p=>!p.alias&&p.name!=='404.html').map(p=>'<url><loc>https://itvm.ru/ever-youth/'+p.name+'</loc></url>').join('') + '</urlset>', {headers:{'Content-Type':'application/xml; charset=utf-8'}});
