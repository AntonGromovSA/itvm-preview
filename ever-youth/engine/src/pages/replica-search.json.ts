import { searchIndex } from '../lib/content';
export const GET = () => new Response(JSON.stringify(searchIndex()), {headers:{'Content-Type':'application/json; charset=utf-8'}});
