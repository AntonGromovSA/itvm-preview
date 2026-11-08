export interface PriceItem { name: string; price: number | null; code: string; source: string; sourceRow: number }
export interface PriceGroup { title: string; items: PriceItem[]; open?: boolean }
export interface PriceSection { id: string; title: string; groups: PriceGroup[] }
export interface Slide { image: string; alt: string; title?: string; text?: string; href?: string }
export type PageBlock =
  | { kind: 'legacy'; id: string; file: string }
  | { kind: 'header' | 'footer'; id: string; file: string }
  | { kind: 'slides'; id: string; slides: Slide[]; label: string }
  | { kind: 'model'; id: string; src: string; poster?: string; label: string };
export interface PageDefinition {
  name: string; title: string; headFile: string;
  htmlAttributes: Record<string, string>; bodyAttributes: Record<string, string>;
  recordAttributes: Record<string, string> | null;
  beforeFile: string; afterFile: string; blocks: PageBlock[]; alias: boolean;
}
