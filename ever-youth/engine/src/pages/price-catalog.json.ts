import { catalog } from '../lib/content';
export const GET = () => new Response(JSON.stringify(catalog), {headers:{'Content-Type':'application/json; charset=utf-8'}});
