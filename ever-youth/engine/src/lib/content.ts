import { readFileSync, readdirSync } from 'node:fs';
import { resolve } from 'node:path';
import { load } from 'cheerio';
import type { PageDefinition, PriceSection } from './types';
import clinic from '../data/clinic.json';
import prices from '../data/prices.json';

const root = process.cwd();
export const catalog: PriceSection[] = prices;
export const pages: PageDefinition[] = readdirSync(resolve(root, 'src/content/pages'))
  .filter(name => name.endsWith('.json'))
  .map(name => JSON.parse(readFileSync(resolve(root, 'src/content/pages', name), 'utf8')));
const cache = new Map<string, string>();
const source = (file: string) => {
  if (!file.startsWith('src/content/')) throw new Error('Invalid content path');
  if (!cache.has(file)) cache.set(file, readFileSync(resolve(root, file), 'utf8'));
  return cache.get(file)!;
};
const texts = new Map<string, Record<string,string>>();
const priceByRow = new Map(catalog.flatMap(c => c.groups.flatMap(g => g.items)).map(i => [String(i.sourceRow), i]));
const amount = (value: number | null) => value === null ? 'Стоимость уточняйте' : new Intl.NumberFormat('ru-RU').format(value) + ' ₽';
export function fragment(file: string, page: PageDefinition): string {
  let raw = source(file);
  if (raw.includes('__CLINIC_TEXT_')) {
    if (!texts.has(page.name)) texts.set(page.name, JSON.parse(readFileSync(resolve(root, 'src/content/texts', page.name + '.json'), 'utf8')));
    raw = raw.replace(/__CLINIC_TEXT_(.*?)__/g, (_, key: string) => {
      const value = texts.get(page.name)![key];
      if (value === undefined) throw new Error(`Missing text ${page.name}:${key}`);
      return value;
    });
  }
  clinic.phones.forEach((phone, i) => {
    raw = raw.replaceAll(`__CLINIC_PHONE_${i}_DISPLAY__`, phone.display).replaceAll(`__CLINIC_PHONE_${i}_E164__`, phone.e164);
  });
  raw = raw.replaceAll('__CLINIC_WHATSAPP_URL__', clinic.whatsapp.url).replaceAll('__CLINIC_WHATSAPP_DISPLAY__', clinic.whatsapp.display).replaceAll('__CLINIC_VK_URL__', clinic.vk);
  raw = raw.replaceAll('__CLINIC_PRICE_CATALOG__', JSON.stringify(catalog).replaceAll('</script', '<\\/script'));
  if (raw.includes('data-source-row=')) {
    const $ = load(raw, {}, false);
    $('tr[data-source-row]').each((_, element) => {
      const row = $(element); const item = priceByRow.get(row.attr('data-source-row')!);
      if (!item) throw new Error('Unknown price row in a specialist profile');
      row.find('td').first().text(item.name); row.find('td').last().text(amount(item.price));
    });
    raw = $.html();
  }
  return raw;
}
export const pageByName = (name: string) => {
  const page = pages.find(p => p.name === name);
  if (!page) throw new Error('Page not found: ' + name);
  return page;
};
export function searchIndex() {
  const index = pages.filter(p => !p.alias && p.name !== '404.html').map(page => {
    const html = page.blocks.filter(b => b.kind === 'legacy').map(b => fragment(b.file, page)).join(' ');
    const $ = load(html); $('script,style,form').remove();
    return { title: page.title, url: page.name + '?v=astro-20261108', text: $.text().replace(/\s+/g, ' ').trim().slice(0,32000) };
  });
  for (const c of catalog) for (const g of c.groups) for (const item of g.items) {
    index.push({ title: item.name, url: 'page178607409.html?q=' + encodeURIComponent(item.name) + '&center=' + c.id + '#price-list', text: c.title + ' ' + g.title + ' ' + item.code + ' ' + amount(item.price) });
  }
  return index;
}
