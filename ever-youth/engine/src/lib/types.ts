export interface PriceItem{name:string;price:number|null;code:string;source:string;sourceRow:number}
export interface PriceGroup{title:string;items:PriceItem[];open?:boolean}
export interface PriceSection{id:string;title:string;groups:PriceGroup[]}
export interface Picture{src:string;srcset:string;width:number;height:number;alt:string}
export interface ContentLink{href:string;title:string}
export interface ContentCard extends ContentLink{text:string;image?:Picture|null}
export interface Video{src:string;kind:string;title:string}
export interface ContentSection{id:string;title:string;html:string;images:Picture[];links:ContentLink[];videos:Video[];cards?:ContentCard[];slides?:Slide[];model?:{src:string;poster?:string;label:string}}
export interface ClinicPage{name:string;title:string;description:string;kind:string;alias?:string;sections:ContentSection[];priceRows:number[];portrait?:Picture|null}
export interface Slide{image:string;alt:string;title?:string;text?:string;href?:string}
