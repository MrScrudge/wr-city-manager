'use strict';
const $=s=>document.querySelector(s);
const WORLD=20000,MIN=10,STORE='wrcity2';
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const num=(v,d)=>(v===null||v===''||v===undefined||!Number.isFinite(+v))?d:+v;
const clamp=(v,a,b)=>Math.min(b,Math.max(a,v));
// HOST: працює всередині W&R City Manager (вкладка «Планувальник»); міста й збереження — на боці програми
const HOST=/[?&]host=1(&|$)/.test(location.search);if(HOST)document.documentElement.classList.add('host');

// ---------- іконки: білі залиті піктограми у стилі гри (на кольоровій плашці блоку). Кожна — вміст SVG 24×24; отвори — evenodd
const f2=n=>+n.toFixed(2);
const pol=(a,r)=>[f2(12+r*Math.cos(a*Math.PI/180)),f2(12+r*Math.sin(a*Math.PI/180))].join(' ');
function gearPath(n,ro,ri,hole){let d='';const st=2*Math.PI/n,P=(g,r)=>f2(12+r*Math.cos(g))+' '+f2(12+r*Math.sin(g));
 for(let i=0;i<n;i++){const a=i*st;d+=(i?'L':'M')+[P(a-st*.3,ri),P(a-st*.17,ro),P(a+st*.17,ro),P(a+st*.3,ri)].join('L')}
 return d+`ZM${12+hole} 12a${hole} ${hole} 0 1 1${-2*hole} 0a${hole} ${hole} 0 1 1${2*hole} 0z`}
function arcArrow(a0,a1,rO,rI){const M=(rO+rI)/2,aH=a1-16;
 return `M${pol(a0,rO)}A${rO} ${rO} 0 0 1 ${pol(aH,rO)}L${pol(aH,rO+2.4)}L${pol(a1,M)}L${pol(aH,rI-2.4)}L${pol(aH,rI)}A${rI} ${rI} 0 0 0 ${pol(a0,rI)}z`}
const P=d=>`<path d="${d}"/>`,PN=d=>`<path fill-rule="nonzero" d="${d}"/>`;
const ICON={
 center:P('M12 2L22 8H2zM13.5 6.2a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0zM3 9.5h18v2H3zM4 12h2.6v6.5H4zM8.6 12h2.6v6.5H8.6zM12.8 12h2.6v6.5h-2.6zM17.4 12h2.6v6.5h-2.6zM2.5 19.5h19V22h-19z'),
 water:P('M12 2.5C9 7 5.5 10.5 5.5 14.5a6.5 6.5 0 0 0 13 0C18.5 10.5 15 7 12 2.5z'),
 tes:P('M2 21V10.5l6 3.5v-3.5l6 3.5v-3.5l8 4.5V21zM5 17h2.5v2.2H5zM10.5 17H13v2.2h-2.5zM16 17h2.5v2.2H16zM15.5 3h4v7.2h-4z'),
 tec:P('M3.5 21C5 16.5 5 12.5 3.5 8H10c-1.5 4.5-1.5 8.5 0 13zM14 21c1.5-4.5 1.5-8.5 0-13h6.5c-1.5 4.5-1.5 8.5 0 13zM8.5 4.4a1.7 1.7 0 1 1-3.4 0 1.7 1.7 0 0 1 3.4 0zM18.7 4.4a1.7 1.7 0 1 1-3.4 0 1.7 1.7 0 0 1 3.4 0z'),
 aes:P('M7 3.34A10 10 0 0 1 17 3.34L13.7 9.06A3.4 3.4 0 0 0 10.3 9.06zM22 12A10 10 0 0 1 17 20.66L13.7 14.94A3.4 3.4 0 0 0 15.4 12zM7 20.66A10 10 0 0 1 2 12L8.6 12A3.4 3.4 0 0 0 10.3 14.94zM14.1 12a2.1 2.1 0 1 1-4.2 0 2.1 2.1 0 0 1 4.2 0z'),
 industry:P(gearPath(8,10,7.4,3)),
 emergency:P('M12 2.5L22.5 20.5h-21zM11 9h2v6h-2zM13.2 17.8a1.2 1.2 0 1 1-2.4 0 1.2 1.2 0 0 1 2.4 0z'),
 freight:P('M2 5.5h20V15H2zM5 8h1.8v4.5H5zM9.2 8H11v4.5H9.2zM13 8h1.8v4.5H13zM17.2 8H19v4.5h-1.8zM3 16.3h18v1.6H3zM9.5 20.2a2 2 0 1 1-4 0 2 2 0 0 1 4 0zM18.5 20.2a2 2 0 1 1-4 0 2 2 0 0 1 4 0z'),
 station:P('M6 2.5h12a2 2 0 0 1 2 2V16a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4.5a2 2 0 0 1 2-2zM7 5.5h10v5.5H7zM9.2 14.2a1.3 1.3 0 1 1-2.6 0 1.3 1.3 0 0 1 2.6 0zM17.4 14.2a1.3 1.3 0 1 1-2.6 0 1.3 1.3 0 0 1 2.6 0zM6.6 19l-2 3h2.2l1.5-3zM17.4 19l2 3h-2.2l-1.5-3z'),
 bus:P('M5 2.5h14a1.5 1.5 0 0 1 1.5 1.5V17.5h-17V4A1.5 1.5 0 0 1 5 2.5zM6.5 5h11v5.5h-11zM9.2 14a1.2 1.2 0 1 1-2.4 0 1.2 1.2 0 0 1 2.4 0zM17.2 14a1.2 1.2 0 1 1-2.4 0 1.2 1.2 0 0 1 2.4 0zM5.5 18.5h3V21.5h-3zM15.5 18.5h3V21.5h-3z'),
 airport:P('M12 1.5c.9 0 1.5.9 1.5 2V9l8.5 5v2.3l-8.5-2.4V19l2.4 1.8V22.5L12 21.4 8.1 22.5v-1.7L10.5 19v-5.1L2 16.3V14l8.5-5V3.5c0-1.1.6-2 1.5-2z'),
 sewage:P('M12 2.5C9.5 6.5 7 9.2 7 12.4a5 5 0 0 0 10 0c0-3.2-2.5-5.9-5-9.9zM2 19.5c2.5-1.8 5-1.8 7.5 0s5 1.8 7.5 0c1.7-1.2 3.4-1.5 5-.8V22.5H2z'),
 recycle:P([0,1,2].map(k=>arcArrow(k*120-80,k*120+30,9,6)).join('')),
 depot:P('M2 21V9.5L12 3l10 6.5V21zM7 21v-7.5h10V21zM9 15.6h6v1.2H9zM9 18h6v1.2H9z'),
 resC:P('M12 2.5L2 11.5h2.8V21h14.4V11.5H22zM10 21v-5.5h4V21z'),
 resV:P('M12 2.5L2 11.5h2.8V21h14.4V11.5H22zM11.2 12.5h1.6v2.4h2.4v1.6h-2.4v2.4h-1.6v-2.4H8.8v-1.6h2.4z'),
 resZ:P('M4 21V3.5h9.5V21zM15.5 21V10h5v11zM6.2 6h2v2h-2zM9.6 6h2v2h-2zM6.2 10h2v2h-2zM9.6 10h2v2h-2zM6.2 14h2v2h-2zM9.6 14h2v2h-2zM17.2 12.6h1.6v1.8h-1.6zM17.2 16h1.6v1.8h-1.6z'),
 elec:P('M13.5 1.5L4.5 13.5h6l-1.5 9 9.5-13h-6.2z'),
 power:'<path d="M12 1.5L14 6H10z"/><path d="M2.5 7.5h19v1.8h-19z"/><path d="M5 12h14v1.7H5z"/><path d="M10.4 6.5h3.2L19 22h-2.3z"/><path d="M13.6 6.5H10.4L5 22h2.3z"/><path d="M9.4 14.8l5.2 5.4-.9.9-5.2-5.4zM14.6 14.8l-5.2 5.4.9.9 5.2-5.4z"/>',
 fun:P('M12 2a10 10 0 1 0 .01 0zM12 3.6a8.4 8.4 0 1 1-.01 0z')+PN('M3 11.2h18v1.6H3zM11.2 3h1.6v18h-1.6zM5.67 4.53L19.47 18.33L18.33 19.47L4.53 5.67zM18.33 4.53L19.47 5.67L5.67 19.47L4.53 18.33z')+'<circle cx="12" cy="12" r="2.6"/>'+PN('M12 13L6.5 22.5h2.2L12 16.6l3.3 5.9h2.2z'),
 stad:P('M2 12a10 6 0 1 0 20 0a10 6 0 1 0-20 0zM5 12a7 3.6 0 1 1 14 0a7 3.6 0 1 1-14 0zM8.5 12a3.5 1.6 0 1 0 7 0a3.5 1.6 0 1 0-7 0z'),
 admin:P('M4 22V9h10v13zM15.5 22V13h4.5v9zM6.2 11.5h2v2h-2zM9.8 11.5h2v2h-2zM6.2 15.5h2v2h-2zM9.8 15.5h2v2h-2zM17.2 15.5h1.6v2h-1.6zM8.4 9V2.5h1.2V9zM9.6 2.5h5l-1.4 1.8 1.4 1.8h-5z'),
 road:P('M8.5 2h7l5 20h-17zM11.2 3.5h1.6v4.5h-1.6zM11.2 10h1.6v4.5h-1.6zM11.2 16.5h1.6v4.5h-1.6z'),
 rail:PN('M8.4 2h1.8L7 22H4.6zM13.8 2h1.8l3.8 20H17zM7.4 5h9.2v1.5H7.4zM6.6 10h10.8v1.5H6.6zM5.7 15.5h12.6V17H5.7z'),
 river:P('M2 14.5h20l-3.2 6.5H5.2zM5 8.5h14v4.8H5zM7.2 10.3h2v1.6h-2zM11 10.3h2v1.6h-2zM14.8 10.3h2v1.6h-2zM9.5 4h5v3.3h-5z'),
 sea:'<g fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="5" r="2.2"/><path d="M12 7.2V21M7.5 11.5h9M4 14.5a8 8 0 0 0 16 0M4 14.5l-1.3-2.2M20 14.5l1.3-2.2"/></g>',
 metro:P('M12 2a10 10 0 1 0 .01 0zM6.6 16.8V7.2h2.1l3.3 4.7 3.3-4.7h2.1v9.6h-2v-6l-3.4 4.8-3.4-4.8v6z'),
 mline:P('M2 7h20v10H2zM4 11.2h16v1.6H4z'),
 text:P('M4 4h16v4.2h-1.6V5.8h-5.4v12.4h2.5V20H8.5v-1.8H11V5.8H5.6v2.4H4z')};
// id:[назва, колір, [ширина,висота] у метрах, вид]
const HEX=/^#[0-9a-f]{6}$/i;
const LC={road:'#4b4b4b',rail:'#9a8a70',mline:'#5b3a8a',power:'#f2c200'};
const defColor=ty=>TY[ty][1]||LC[ty]||(TY[ty][3]==='text'?'#ffffff':'#888888');
const TY={
 center:['Центр міста','#d9b44a',[120,100]],water:['Вода','#3b86c4',[160,120]],tes:['ТЕС','#7d7d7d',[120,100]],tec:['ТЕЦ','#b8643c',[120,100]],
 aes:['АЕС','#58b04a',[140,120]],industry:['Промисловість','#8a6d9e',[160,120]],emergency:['Аварійна Зона','#d64541',[100,80]],
 freight:['Вантажний Вокзал','#a0522d',[140,80]],station:['Вокзал','#c0392b',[120,80]],bus:['Автомобільний Вокзал','#e08e2b',[120,80]],
 airport:['Аеропорт','#5b8fa8',[240,140]],sewage:['Стічні Води','#7a6a45',[100,80]],recycle:['Переробка','#3f9b7f',[120,100]],
 depot:['Зона Депо','#a39560',[120,100]],resC:['Житлова зона С','#e6c36a',[140,120]],resV:['Житлова зона В','#e49aa0',[140,120]],
 resZ:['Житлова зона','#e8b27a',[160,120]],elec:['Електро вузли','#e6d23a',[100,80]],fun:['Зона розваг','#d65db1',[160,120]],
 stad:['Стадіон','#4fa36a',[200,140]],admin:['Адміністративна зона','#6a7fb5',[160,120]],
 road:['Дорога',null,[200,20],'road'],rail:['Колія',null,[200,20],'rail'],power:['Електромережа',null,[300,14],'power'],river:['Річковий Порт','#2f6fa0',[140,80]],sea:['Морський Порт','#245c8a',[160,100]],
 metro:['Станція метро','#d4202a',[80,60]],mline:['Лінія метро',null,[240,16],'mline'],text:['Текст',null,[240,60],'text']};
const HATCH=[['none','Без штрихування'],['d1','Діагональ /'],['d2','Діагональ \\'],['cr','Клітинка'],['hz','Горизонтальне'],['vt','Вертикальне'],['dt','Крапки']];
const HP={d1:'<pattern id="h-d1" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line y2="8" stroke="#0007" stroke-width="2"/></pattern>',
 d2:'<pattern id="h-d2" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)"><line y2="8" stroke="#0007" stroke-width="2"/></pattern>',
 cr:'<pattern id="h-cr" width="8" height="8" patternUnits="userSpaceOnUse"><path d="M0 0H8M0 0V8" stroke="#0007" stroke-width="1.5" fill="none"/></pattern>',
 hz:'<pattern id="h-hz" width="8" height="8" patternUnits="userSpaceOnUse"><line x2="8" stroke="#0007" stroke-width="2"/></pattern>',
 vt:'<pattern id="h-vt" width="8" height="8" patternUnits="userSpaceOnUse"><line y2="8" stroke="#0007" stroke-width="2"/></pattern>',
 dt:'<pattern id="h-dt" width="8" height="8" patternUnits="userSpaceOnUse"><circle cx="4" cy="4" r="1.6" fill="#0008"/></pattern>'};
// 3×3 клітинки блоку: індекс = рядок*3+колонка
const SHAPES=[['rect','Прямокутник',[1,1,1,1,1,1,1,1,1]],['g','Г-подібна',[1,1,1,1,0,0,1,0,0]],['l','L-подібна',[1,0,0,1,0,0,1,1,1]],
 ['t','Т-подібна',[1,1,1,0,1,0,0,1,0]],['u','П-подібна',[1,1,1,1,0,1,1,0,1]],['cross','Хрест',[0,1,0,1,1,1,0,1,0]]];
SHAPES.forEach(s=>s[2]=s[2].map(Boolean));
// T = верхня перекладина + ніжка по центру
SHAPES[3][2]=[1,1,1,0,1,0,0,1,0].map(Boolean);
SHAPES[4][2]=[1,1,1,1,0,1,1,0,1].map(Boolean);

// ---------- мови (укр — вихідні рядки; англійська й німецька — у TR)
let LANG='uk';const Q=new URLSearchParams(location.search);
const TR={
 'Міський планувальник':['City planner','Stadtplaner'],'Місто:':['City:','Stadt:'],'Створити місто':['New city','Stadt anlegen'],'Видалити місто':['Delete city','Stadt löschen'],
 'Експорт':['Export','Export'],'Імпорт':['Import','Import'],'Зберегти PNG':['Save PNG','PNG speichern'],'Друк / PDF':['Print / PDF','Drucken / PDF'],'Зберегти PDF':['Save PDF','PDF speichern'],
 'Інструменти':['Tools','Werkzeuge'],'Показати сітку':['Show grid','Raster anzeigen'],'Прив’язка до сітки':['Snap to grid','Am Raster ausrichten'],
 'Магніт блоків':['Block magnet','Block-Magnet'],'Показувати метри':['Show meters','Meter anzeigen'],'Крок сітки':['Grid step','Rasterweite'],
 '5 м':['5 m','5 m'],'10 м':['10 m','10 m'],'20 м':['20 m','20 m'],'м':['m','m'],
 'Масштаб 100%':['Zoom 100%','Zoom 100 %'],'До центру':['To center','Zur Mitte'],'Скасувати':['Undo','Rückgängig'],'Дублювати':['Duplicate','Duplizieren'],'Видалити':['Delete','Löschen'],
 'Полотно 20 000 × 20 000 м, клітинка = крок сітки. Колесо — масштаб, середня/права кнопка або тло — переміщення. Ctrl/Shift+клік — кілька блоків, Shift+рамка або Ctrl+A — виділити багато.':['Canvas 20,000 × 20,000 m, one cell = grid step. Wheel — zoom, middle/right button or background — pan. Ctrl/Shift+click — several blocks, Shift+drag or Ctrl+A — select many.',
  'Zeichenfläche 20.000 × 20.000 m, eine Zelle = Rasterweite. Mausrad — Zoom, mittlere/rechte Taste oder Hintergrund — Verschieben. Strg/Umschalt+Klick — mehrere Blöcke, Umschalt+Ziehen oder Strg+A — alle wählen.'],
 'Блоки':['Blocks','Blöcke'],'Видалити блок':['Delete block','Block löschen'],'Назва':['Name','Name'],'Додати свою іконку':['Add your own icon','Eigenes Symbol hinzufügen'],'Колір фону':['Background color','Hintergrundfarbe'],'Іконка (картинка)':['Icon (image)','Symbol (Bild)'],'Зробити іконку білою':['Make the icon white','Symbol weiß machen'],'Додати':['Add','Hinzufügen'],'Відміна':['Cancel','Abbrechen'],'Видалити зі своїх':['Remove from my icons','Aus eigenen entfernen'],'Видалити іконку «':['Remove icon «','Symbol entfernen «'],'» з бібліотеки? Блоки цього типу на картах теж зникнуть.':['» from the library? Blocks of this type will also disappear from the maps.','» aus der Bibliothek? Blöcke dieses Typs verschwinden auch von den Karten.'],'Своя іконка':['My icon','Eigenes Symbol'],'Бібліотека':['Library','Bibliothek'],
 'Спочатку додайте місто на вкладці «Міста».':['First add a city on the «Cities» tab.','Legen Sie zuerst im Reiter «Städte» eine Stadt an.'],
 'Центр міста':['City center','Stadtzentrum'],'Вода':['Water','Wasser'],'ТЕС':['Thermal power plant','Wärmekraftwerk'],'ТЕЦ':['Combined heat and power plant','Heizkraftwerk'],
 'АЕС':['Nuclear power plant','Kernkraftwerk'],'Промисловість':['Industry','Industrie'],'Аварійна Зона':['Emergency zone','Notfallzone'],
 'Вантажний Вокзал':['Freight station','Güterbahnhof'],'Вокзал':['Train station','Bahnhof'],'Автомобільний Вокзал':['Bus station','Busbahnhof'],'Аеропорт':['Airport','Flughafen'],
 'Стічні Води':['Sewage','Abwasser'],'Переробка':['Recycling','Recycling'],'Зона Депо':['Depot zone','Depotzone'],
 'Житлова зона С':['Housing zone S','Wohnzone M'],'Житлова зона В':['Housing zone H','Wohnzone H'],'Житлова зона':['Residential zone','Wohngebiet'],
 'Електро вузли':['Electrical substations','Umspannwerke'],'Зона розваг':['Entertainment zone','Unterhaltungszone'],'Стадіон':['Stadium','Stadion'],
 'Адміністративна зона':['Administrative zone','Verwaltungszone'],'Дорога':['Road','Straße'],'Колія':['Railway','Gleis'],'Електромережа':['Power line','Stromleitung'],
 'Річковий Порт':['River port','Flusshafen'],'Морський Порт':['Sea port','Seehafen'],'Станція метро':['Metro station','U-Bahn-Station'],'Лінія метро':['Metro line','U-Bahn-Linie'],'Текст':['Text','Text'],
 'Без штрихування':['No hatching','Keine Schraffur'],'Діагональ /':['Diagonal /','Diagonal /'],'Діагональ \\':['Diagonal \\','Diagonal \\'],'Клітинка':['Grid','Karo'],
 'Горизонтальне':['Horizontal','Horizontal'],'Вертикальне':['Vertical','Vertikal'],'Крапки':['Dots','Punkte'],
 'Прямокутник':['Rectangle','Rechteck'],'Г-подібна':['Γ-shape','Γ-Form'],'L-подібна':['L-shape','L-Form'],'Т-подібна':['T-shape','T-Form'],'П-подібна':['U-shape','U-Form'],'Хрест':['Cross','Kreuz'],'Власна':['Custom','Benutzerdefiniert'],
 'Шрифт (м)':['Font (m)','Schrift (m)'],'Колір':['Color','Farbe'],'Назва':['Name','Name'],'Нотатка (у блоці, 70%)':['Note (inside the block, 70%)','Notiz (im Block, 70 %)'],
 'Штрихування':['Hatching','Schraffur'],'Стандартний колір':['Default color','Standardfarbe'],'Ширина (м)':['Width (m)','Breite (m)'],'Висота (м)':['Height (m)','Höhe (m)'],
 'Центр X (м)':['Center X (m)','Mitte X (m)'],'Центр Y (м)':['Center Y (m)','Mitte Y (m)'],'Поворот (°)':['Rotation (°)','Drehung (°)'],'Форма':['Shape','Form'],
 'Вище':['Up','Höher'],'Нижче':['Down','Tiefer'],'Клітинка {n}':['Cell {n}','Zelle {n}'],'Показати / сховати':['Show / hide','Ein- / ausblenden'],'Налаштування блоку':['Block settings','Blockeinstellungen'],
 'У цьому місті ще немає блоків. Додайте їх із бібліотеки.':['There are no blocks in this city yet. Add them from the library.','In dieser Stadt gibt es noch keine Blöcke. Fügen Sie sie aus der Bibliothek hinzu.'],
 'Назва нового міста:':['Name of the new city:','Name der neuen Stadt:'],'Нове місто':['New city','Neue Stadt'],'Місто з такою назвою вже є.':['A city with this name already exists.','Eine Stadt mit diesem Namen gibt es schon.'],
 'Видалити місто «{n}»?':['Delete the city «{n}»?','Stadt «{n}» löschen?'],'Не вдалося прочитати файл.':['Could not read the file.','Datei konnte nicht gelesen werden.'],
 'Немає блоків для експорту.':['There are no blocks to export.','Keine Blöcke zum Exportieren.'],'Не вдалося створити зображення.':['Could not create the image.','Bild konnte nicht erstellt werden.']};
const tt=s=>{if(LANG==='uk')return s;const r=TR[s];return r?r[LANG==='en'?0:1]:s};
const lab=b=>b.label===TY[b.type][0]?tt(b.label):b.label;                       // стандартна назва блоку перекладається, власна — ні
const canonLabel=(type,v)=>v===tt(TY[type][0])?TY[type][0]:v;
const statics=new Map();
function translateStatic(){
 const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT,{acceptNode:n=>n.parentElement&&!n.parentElement.closest('#layers,#palette,#citySel,svg,script,style')?NodeFilter.FILTER_ACCEPT:NodeFilter.FILTER_REJECT});
 let n;while((n=w.nextNode())){if(!statics.has(n))statics.set(n,n.nodeValue);const o=statics.get(n),k=o.trim();if(!k)continue;n.nodeValue=o.replace(k,tt(k))}
 document.title=tt('Міський планувальник')}
function setLang(c){LANG=(c==='en'||c==='de')?c:'uk';document.documentElement.lang=LANG;buildPalette();translateStatic();if(typeof S!=='undefined'&&S.cur)render()}
const svg=$('#cv'),world=$('#world'),gridEl=$('#grid');
let sel=null,drag=null,hist=[],seq=0;const OPEN=new Set(),MS=new Set();
const CUST_MAX=60;
function cust(a){const out=[];if(!Array.isArray(a))a=[];
 for(const c of a.slice(0,CUST_MAX)){if(!c||typeof c!=='object')continue;const id=String(c.id||'');
  if(!/^c_[a-z0-9]{3,16}$/.test(id)||out.some(o=>o.id===id))continue;
  const img=typeof c.img==='string'&&/^data:image\/png;base64,[A-Za-z0-9+\/=]{1,200000}$/.test(c.img)?c.img:'';
  out.push({id,name:String(c.name||'').slice(0,40)||'—',color:typeof c.color==='string'&&HEX.test(c.color)?c.color:'#888888',img})}
 for(const k of Object.keys(TY))if(k.startsWith('c_'))delete TY[k];
 for(const k of Object.keys(ICON))if(k.startsWith('c_'))delete ICON[k];
 for(const c of out){TY[c.id]=[c.name,c.color,[120,100]];TY[c.id].custom=1;ICON[c.id]=c.img?`<image href="${c.img}" width="24" height="24"/>`:''}
 return out}
const iconSvg=(id,sw,col='#fff')=>`<svg viewBox="0 0 24 24" fill="${col}" fill-rule="evenodd">${ICON[id]||''}</svg>`;
const eyeIcon=off=>`<svg viewBox="0 0 24 24" fill="none" stroke="#4a2c1a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12zM12 9a3 3 0 100 6 3 3 0 000-6z"/>${off?'<path d="M3 3l18 18" stroke="#8f3430" stroke-width="2.5"/>':''}</svg>`;

// ---------- дані
function normBlock(b){
 if(!b||typeof b!=='object'||!TY[b.type])return null;const t=TY[b.type];
 const fx=Array.isArray(b.fx)&&b.fx.length===2&&+b.fx[0]>=.05&&+b.fx[1]<=.95&&+b.fx[1]-+b.fx[0]>=.05?[+b.fx[0],+b.fx[1]]:[1/3,2/3];
 const fy=Array.isArray(b.fy)&&b.fy.length===2&&+b.fy[0]>=.05&&+b.fy[1]<=.95&&+b.fy[1]-+b.fy[0]>=.05?[+b.fy[0],+b.fy[1]]:[1/3,2/3];
 const cells=Array.isArray(b.cells)&&b.cells.length===9&&b.cells.some(Boolean)?b.cells.map(Boolean):Array(9).fill(true);
 return{id:++seq,type:b.type,x:num(b.x,0),y:num(b.y,0),w:Math.max(MIN,num(b.w,t[2][0])),h:Math.max(MIN,num(b.h,t[2][1])),
  rot:((num(b.rot,0)%360)+360)%360,color:typeof b.color==='string'&&HEX.test(b.color)&&!(LC[b.type]&&b.color==='#888888')?b.color:defColor(b.type),
  hatch:HP[b.hatch]?b.hatch:'none',label:typeof b.label==='string'?(b.type==='metro'&&b.label==='Метро'?t[0]:b.label):(t[3]?'':t[0]),note:typeof b.note==='string'?b.note:'',
  text:typeof b.text==='string'?b.text:(t[3]==='text'?tt('Текст'):''),fs:clamp(num(b.fs,20),4,500),hide:!!b.hide,cells,fx,fy}}
function defView(){const z=.6;return{z,x:(svg.clientWidth||900)/2-WORLD/2*z,y:(svg.clientHeight||600)/2-WORLD/2*z,auto:true}}
function okView(v){return v&&Number.isFinite(+v.x)&&Number.isFinite(+v.y)&&Number.isFinite(+v.z)?{x:+v.x,y:+v.y,z:clamp(+v.z,.03,4)}:defView()}
function cleanOpts(r){const o={grid:true,snap:true,magnet:true,meters:false,G:10,custom:[]};o.custom=cust(r&&r.custom);if(r&&typeof r==='object'){for(const k of['grid','snap','magnet','meters'])if(typeof r[k]==='boolean')o[k]=r[k];if([5,10,20].includes(+r.G))o.G=+r.G}return o}
function sanitize(r,migrated){
 const o={cur:null,cities:{},opts:{grid:true,snap:true,magnet:true,meters:false,G:10,custom:[]}};
 if(r&&r.opts&&typeof r.opts==='object'){o.opts.custom=cust(r.opts.custom);for(const k of['grid','snap','magnet','meters'])if(typeof r.opts[k]==='boolean')o.opts[k]=r.opts[k];if([5,10,20].includes(+r.opts.G))o.opts.G=+r.opts.G}
 if(r&&r.cities&&typeof r.cities==='object')for(const[n,c]of Object.entries(r.cities)){if(!c||typeof c!=='object')continue;
  const bl=(Array.isArray(c.blocks)?c.blocks:[]).map(b=>(migrated&&b)?{...b,x:+b.x+WORLD/2,y:+b.y+WORLD/2}:b).map(normBlock).filter(Boolean);
  const v=c.view;o.cities[String(n).slice(0,80)]={name:String(n).slice(0,80),blocks:bl,view:(!migrated&&v&&Number.isFinite(+v.x)&&Number.isFinite(+v.y)&&Number.isFinite(+v.z))?{x:+v.x,y:+v.y,z:clamp(+v.z,.03,4)}:defView()}}
 o.cur=r&&o.cities[r.cur]?r.cur:(Object.keys(o.cities)[0]||null);return o}
function load(){let r=null,mig=false;
 try{r=JSON.parse(localStorage.getItem(STORE)||'null')}catch(e){}
 if(!r||!r.cities){try{const o=JSON.parse(localStorage.getItem('wrcity')||'null');if(o&&o.cities){r=o;mig=true}}catch(e){}}
 return sanitize(r,mig)}
let S=load();
const cur=()=>S.cities[S.cur],B=()=>cur().blocks,V=()=>cur().view,O=()=>S.opts;
const dirty=new Set();let pendingExport=null;
const save=()=>{if(HOST){if(S.cur&&S.cur!=='_')dirty.add(S.cur);return}try{localStorage.setItem(STORE,JSON.stringify(S))}catch(e){}};
const cb=()=>B().find(b=>b.id===sel);
const selBlocks=()=>B().filter(b=>MS.has(b.id));
function select(id,add){if(id==null){MS.clear();sel=null;return}
 if(add){if(MS.has(id)){MS.delete(id);sel=MS.size?[...MS].pop():null}else{MS.add(id);sel=id}}else{MS.clear();MS.add(id);sel=id}}
function selectMany(ids){MS.clear();ids.forEach(i=>MS.add(i));sel=ids.length?ids[ids.length-1]:null}
const byId=id=>B().find(b=>b.id===id);

// ---------- геометрія
const rad=b=>b.rot*Math.PI/180;
const ctr=b=>({x:b.x+b.w/2,y:b.y+b.h/2});
function toLocal(b,p){const c=ctr(b),r=rad(b),co=Math.cos(r),si=Math.sin(r),dx=p.x-c.x,dy=p.y-c.y;return{x:dx*co+dy*si+b.w/2,y:-dx*si+dy*co+b.h/2}}
function toWorld(b,lx,ly){const c=ctr(b),r=rad(b),co=Math.cos(r),si=Math.sin(r),dx=lx-b.w/2,dy=ly-b.h/2;return{x:c.x+dx*co-dy*si,y:c.y+dx*si+dy*co}}
const colEdges=b=>[0,b.fx[0]*b.w,b.fx[1]*b.w,b.w],rowEdges=b=>[0,b.fy[0]*b.h,b.fy[1]*b.h,b.h];
function hit(b,p){const l=toLocal(b,p);if(l.x<0||l.y<0||l.x>b.w||l.y>b.h)return false;
 const xs=colEdges(b),ys=rowEdges(b);return b.cells[(l.y<ys[1]?0:l.y<ys[2]?1:2)*3+(l.x<xs[1]?0:l.x<xs[2]?1:2)]}
function aabb(b){const q=[toWorld(b,0,0),toWorld(b,b.w,0),toWorld(b,b.w,b.h),toWorld(b,0,b.h)];
 const x0=Math.min(...q.map(p=>p.x)),x1=Math.max(...q.map(p=>p.x)),y0=Math.min(...q.map(p=>p.y)),y1=Math.max(...q.map(p=>p.y));return{x:x0,y:y0,w:x1-x0,h:y1-y0}}
function clampBlock(b){const a=aabb(b);
 if(a.x<0)b.x-=a.x;else if(a.x+a.w>WORLD)b.x-=a.x+a.w-WORLD;
 if(a.y<0)b.y-=a.y;else if(a.y+a.h>WORLD)b.y-=a.y+a.h-WORLD}
function bestRect(b){const xs=colEdges(b),ys=rowEdges(b);let best=null,ba=-1;
 for(let r0=0;r0<3;r0++)for(let r1=r0;r1<3;r1++)for(let c0=0;c0<3;c0++)for(let c1=c0;c1<3;c1++){
  let ok=true;for(let r=r0;r<=r1&&ok;r++)for(let c=c0;c<=c1;c++)if(!b.cells[r*3+c]){ok=false;break}
  if(!ok)continue;const a=(xs[c1+1]-xs[c0])*(ys[r1+1]-ys[r0]);if(a>ba){ba=a;best={x:xs[c0],y:ys[r0],w:xs[c1+1]-xs[c0],h:ys[r1+1]-ys[r0]}}}
 return best}
function edges(b){const xs=colEdges(b),ys=rowEdges(b),out=[],A=(r,c)=>r>=0&&r<3&&c>=0&&c<3&&b.cells[r*3+c];
 for(let r=0;r<3;r++)for(let c=0;c<3;c++){if(!b.cells[r*3+c])continue;
  if(!A(r-1,c))out.push([xs[c],ys[r],xs[c+1],ys[r]]);if(!A(r+1,c))out.push([xs[c],ys[r+1],xs[c+1],ys[r+1]]);
  if(!A(r,c-1))out.push([xs[c],ys[r],xs[c],ys[r+1]]);if(!A(r,c+1))out.push([xs[c+1],ys[r],xs[c+1],ys[r+1]])}
 return out}
const isRect=b=>b.cells.every(Boolean);

// ---------- прив’язка
function sn(v,ax,ex){let best=v,bd=Infinity;const G=O().G;
 if(O().magnet){const T=Math.min(10/V().z,50);
  for(const o of B()){if(o.id===ex||MS.has(o.id)||o.hide)continue;const a=aabb(o);
   for(const c of ax==='x'?[a.x,a.x+a.w]:[a.y,a.y+a.h]){const d=Math.abs(c-v);if(d<T&&d<bd){best=c;bd=d}}}}
 if(bd===Infinity&&O().snap)best=Math.round(v/G)*G;
 return[best,Math.abs(best-v)]}

// ---------- текст
const mc=document.createElement('canvas').getContext('2d');
function wrap(str,maxW,fs){mc.font=fs+'px Arial';const out=[];
 for(const para of String(str||'').split('\n')){if(out.length>200)break;if(!para.trim()){out.push('');continue}
  let line='';
  for(const word of para.split(/\s+/)){if(!word)continue;const test=line?line+' '+word:word;
   if(mc.measureText(test).width<=maxW){line=test;continue}
   if(line){out.push(line);line=''}
   let rest=word;
   while(mc.measureText(rest).width>maxW&&rest.length>1){let i=rest.length-1;while(i>1&&mc.measureText(rest.slice(0,i)).width>maxW)i--;out.push(rest.slice(0,i));rest=rest.slice(i)}
   line=rest}
  out.push(line)}
 return out}
const HALO='stroke="#000b" stroke-width="3" paint-order="stroke" stroke-linejoin="round"';
const T=(x,y,fs,txt,extra='')=>`<text x="${x}" y="${y}" text-anchor="middle" font-size="${fs}" font-family="Arial" fill="#fff" ${HALO} ${extra}>${esc(txt)}</text>`;

// ---------- малювання
function contentSVG(b,box){
 const w=box.w,h=box.h,hasI=!!ICON[b.type];
 // усе (іконка + назва + нотатка) малюється в «природних» розмірах і разом зменшується, поки не влізе
 const lay=W=>{const mw=Math.max(8,W-8),LL=lab(b)?wrap(lab(b),mw,12):[],NL=b.note?wrap(b.note,mw,9):[],iz=hasI?40:0;
  return{LL,NL,iz,H:iz+(LL.length?(iz?4:0)+LL.length*14:0)+(NL.length?((iz||LL.length)?5:0)+NL.length*11:0)}};
 let k=1,L=lay(w);
 for(;k>.1;k=+(k-.04).toFixed(2)){L=lay(w/k);if(L.H<=h/k)break}
 if(k<=.1||(!L.iz&&!L.LL.length&&!L.NL.length))return '';
 const W=w/k,Hh=h/k,{LL,NL,iz}=L;let y=Math.max(0,(Hh-L.H)/2),s=`<svg x="${box.x}" y="${box.y}" width="${w}" height="${h}"><g transform="scale(${k})">`;
 if(iz){s+=`<g transform="translate(${(W-iz)/2} ${y}) scale(${iz/24})" fill="#fff" fill-rule="evenodd" style="filter:drop-shadow(0 0 .6px #000) drop-shadow(0 0 .6px #000)">${ICON[b.type]}</g>`;y+=iz+(LL.length||NL.length?4:0)}
 for(const l of LL){s+=T(W/2,y+11,12,l);y+=14}
 if(NL.length){if(LL.length)y+=5;s+='<g opacity="0.7">';for(const l of NL){s+=T(W/2,y+8,9,l);y+=11}s+='</g>'}
 return s+'</g></svg>'}
function blockSVG(b){
 const t=TY[b.type],k=t[3],w=b.w,h=b.h,c=ctr(b);
 let s=`<g class="blk" data-id="${b.id}" transform="translate(${c.x} ${c.y}) rotate(${b.rot}) translate(${-w/2} ${-h/2})">`;
 if(k==='road'){const H=w>=h;s+=`<rect width="${w}" height="${h}" fill="${b.color}" stroke="#222" stroke-width="1.5"/>`+(H?`<line x1="4" x2="${w-4}" y1="${h/2}" y2="${h/2}"`:`<line y1="4" y2="${h-4}" x1="${w/2}" x2="${w/2}"`)+` stroke="#e8d36a" stroke-width="2" stroke-dasharray="10 8" pointer-events="none"/>`}
 else if(k==='rail'){const H=w>=h,Tk=Math.min(w,h);s+=`<rect width="${w}" height="${h}" fill="${b.color}" stroke="#4a3a28" stroke-width="1.5"/>`;
  s+=H?`<g pointer-events="none"><line x1="0" x2="${w}" y1="${h/2}" y2="${h/2}" stroke="#5a4026" stroke-width="${Tk*.8}" stroke-dasharray="3 7"/><line x1="0" x2="${w}" y1="${h*.3}" y2="${h*.3}" stroke="#333" stroke-width="2"/><line x1="0" x2="${w}" y1="${h*.7}" y2="${h*.7}" stroke="#333" stroke-width="2"/></g>`
   :`<g pointer-events="none"><line y1="0" y2="${h}" x1="${w/2}" x2="${w/2}" stroke="#5a4026" stroke-width="${Tk*.8}" stroke-dasharray="3 7"/><line y1="0" y2="${h}" x1="${w*.3}" x2="${w*.3}" stroke="#333" stroke-width="2"/><line y1="0" y2="${h}" x1="${w*.7}" x2="${w*.7}" stroke="#333" stroke-width="2"/></g>`}
 else if(k==='power'){const H=w>=h,len=H?w:h,mid=(H?h:w)/2,P=u=>H?[u,mid]:[mid,u],a=P(0),e2=P(len);
  s+=`<rect width="${w}" height="${h}" fill="#fff" fill-opacity="0.001"/><g pointer-events="none"><line x1="${a[0]}" y1="${a[1]}" x2="${e2[0]}" y2="${e2[1]}" stroke="#000a" stroke-width="5" stroke-linecap="round"/><line x1="${a[0]}" y1="${a[1]}" x2="${e2[0]}" y2="${e2[1]}" stroke="${b.color}" stroke-width="2.5" stroke-linecap="round"/>`;
  const us=[];for(let u=0;u<len;u+=50)us.push(u);us.push(len);
  for(const u of us){const q=P(u);s+=`<circle cx="${q[0]}" cy="${q[1]}" r="4" fill="${b.color}" stroke="#000a" stroke-width="1.5"/>`}
  s+='</g>'}
 else if(k==='mline'){const H=w>=h,Tk=Math.min(w,h);s+=`<rect width="${w}" height="${h}" fill="${b.color}" stroke="#2d1a4a" stroke-width="1.5"/><g pointer-events="none">`+(H?`<line x1="0" x2="${w}" y1="${h/2}" y2="${h/2}"`:`<line y1="0" y2="${h}" x1="${w/2}" x2="${w/2}"`)+` stroke="#fff" stroke-width="${Math.max(1.5,Tk*.28)}" stroke-dasharray="${Tk*1.2} ${Tk*.8}" opacity=".85"/></g>`}
 else if(k==='text'){
  s+=`<rect width="${w}" height="${h}" fill="#fff" fill-opacity="0.001"/>`;
  const fs=b.fs,lines=wrap(b.text,Math.max(8,w-8),fs),lh=fs*1.2,y0=(h-lines.length*lh)/2;
  s+=`<svg width="${w}" height="${h}" pointer-events="none">`+lines.map((l,i)=>`<text x="${w/2}" y="${y0+i*lh+fs*.85}" text-anchor="middle" font-size="${fs}" font-family="Arial" fill="${b.color}" stroke="#000b" stroke-width="${Math.max(1,fs*.12)}" paint-order="stroke" stroke-linejoin="round">${esc(l)}</text>`).join('')+'</svg>'}
 else{
  const xs=colEdges(b),ys=rowEdges(b);let cells='',hat='';
  for(let r=0;r<3;r++)for(let q=0;q<3;q++){if(!b.cells[r*3+q])continue;const x=xs[q],y=ys[r],cw=xs[q+1]-x,ch=ys[r+1]-y;
   cells+=`<rect x="${x}" y="${y}" width="${cw}" height="${ch}" fill="${b.color}" stroke="${b.color}" stroke-width=".6"/>`;
   if(b.hatch!=='none')hat+=`<rect x="${x}" y="${y}" width="${cw}" height="${ch}" fill="url(#h-${b.hatch})"/>`}
  s+=cells+`<g pointer-events="none">${hat}<path d="${edges(b).map(e=>`M${e[0]} ${e[1]}L${e[2]} ${e[3]}`).join('')}" fill="none" stroke="#0008" stroke-width="2" stroke-linecap="square" vector-effect="non-scaling-stroke"/>`+contentSVG(b,bestRect(b))+'</g>'}
 if(k&&k!=='text'&&lab(b))s+=`<g pointer-events="none">${T(w/2,h/2+4,11,lab(b))}</g>`;
 return s+'</g>'}
function drawMeters(){$('#mt').innerHTML=O().meters?metersMarkup(V().z):''}
function metersMarkup(z){
 const fs=11/z;let s='';
 const L=(mid,n,txt)=>{const len=txt.length*fs*.55,off=6/z+len/2*Math.abs(n.x)+fs*.6*Math.abs(n.y);
  return `<text x="${mid.x+n.x*off}" y="${mid.y+n.y*off+fs*.35}" text-anchor="middle" font-size="${fs}" font-family="Arial" fill="#fff" stroke="#000c" stroke-width="${3/z}" paint-order="stroke">${txt}</text>`};
 for(const b of B()){if(b.hide||Math.max(b.w,b.h)*z<30)continue;const r=rad(b),co=Math.cos(r),si=Math.sin(r),f=v=>(+v.toFixed(1))+' '+tt('м');
  s+=L(toWorld(b,b.w/2,0),{x:si,y:-co},f(b.w))+L(toWorld(b,b.w,b.h/2),{x:co,y:si},f(b.h))}
 return s}
function outlineOnly(b,z){const c=ctr(b);return `<g transform="translate(${c.x} ${c.y}) rotate(${b.rot}) translate(${-b.w/2} ${-b.h/2})"><path d="${edges(b).map(e=>`M${e[0]} ${e[1]}L${e[2]} ${e[3]}`).join('')}" fill="none" stroke="#ffd54a" stroke-width="${3.5/z}" stroke-linecap="square" pointer-events="none"/><rect width="${b.w}" height="${b.h}" fill="none" stroke="#fff" stroke-width="${1.5/z}" stroke-dasharray="${6/z} ${4/z}" pointer-events="none"/></g>`}
function fullOverlay(b,z){
 const hs=10/z,w=b.w,h=b.h,c=ctr(b),xs=colEdges(b),ys=rowEdges(b);
 const P={nw:[0,0],n:[.5,0],ne:[1,0],e:[1,.5],se:[1,1],s:[.5,1],sw:[0,1],w:[0,.5]};
 let s=`<g transform="translate(${c.x} ${c.y}) rotate(${b.rot}) translate(${-w/2} ${-h/2})">`;
 s+=`<path d="${edges(b).map(e=>`M${e[0]} ${e[1]}L${e[2]} ${e[3]}`).join('')}" fill="none" stroke="#ffd54a" stroke-width="${3.5/z}" stroke-linecap="square" pointer-events="none"/>`;
 s+=`<rect width="${w}" height="${h}" fill="none" stroke="#fff" stroke-width="${1.5/z}" stroke-dasharray="${6/z} ${4/z}" pointer-events="none"/>`;
 if(!isRect(b)){s+=`<path d="M${xs[1]} 0V${h}M${xs[2]} 0V${h}M0 ${ys[1]}H${w}M0 ${ys[2]}H${w}" stroke="#ffd54a" stroke-width="${1/z}" stroke-dasharray="${4/z} ${4/z}" fill="none" pointer-events="none"/>`;
  for(const[i,j]of[[0,0],[1,0],[0,1],[1,1]]){const x=xs[i+1],y=ys[j+1],d=7/z;
   s+=`<path data-sp="${i}${j}" d="M${x} ${y-d}L${x+d} ${y}L${x} ${y+d}L${x-d} ${y}Z" fill="#ffd54a" stroke="#4a2c1a" stroke-width="${1.5/z}" style="cursor:move"/>`}}
 s+=Object.entries(P).map(([d,q])=>`<rect data-h="${d}" x="${w*q[0]-hs/2}" y="${h*q[1]-hs/2}" width="${hs}" height="${hs}" fill="#8f3430" stroke="#fff" stroke-width="${1/z}" style="cursor:pointer"/>`).join('');
 s+=`<line x1="${w/2}" y1="0" x2="${w/2}" y2="${-26/z}" stroke="#fff" stroke-width="${1.5/z}" pointer-events="none"/><circle data-h="rot" cx="${w/2}" cy="${-26/z}" r="${6/z}" fill="#ffd54a" stroke="#4a2c1a" stroke-width="${1.5/z}" style="cursor:grab"/>`;
 return s+'</g>'}
function drawOverlay(){const ov=$('#ov'),z=V().z,bs=selBlocks().filter(b=>!b.hide);let s='';
 if(bs.length===1)s+=fullOverlay(bs[0],z);else for(const b of bs)s+=outlineOnly(b,z);
 if(drag&&drag.k==='box'&&drag.moved){const x=Math.min(drag.p.x,drag.p2.x),y=Math.min(drag.p.y,drag.p2.y);s+=`<rect x="${x}" y="${y}" width="${Math.abs(drag.p.x-drag.p2.x)}" height="${Math.abs(drag.p.y-drag.p2.y)}" fill="#ffd54a30" stroke="#ffd54a" stroke-width="${1.5/z}" stroke-dasharray="${5/z} ${4/z}" pointer-events="none"/>`}
 ov.innerHTML=s}
function render(light){const v=V(),G=O().G;
 world.setAttribute('transform',`translate(${v.x} ${v.y}) scale(${v.z})`);
 gridEl.style.display=(O().grid&&G*v.z>=3)?'':'none';
 $('#blocks').innerHTML=B().filter(b=>!b.hide).map(blockSVG).join('');
 drawMeters();drawOverlay();$('#empty').classList.toggle('hidden',!(HOST&&S.cur==='_'));if(!light)renderLayers()}

// ---------- панель «Блоки»
const nameOf=b=>{const t=TY[b.type];return t[3]==='text'?((b.text||'').split('\n')[0]||tt('Текст')).slice(0,24):(lab(b)||tt(t[0]))};
function listBlocks(){return[...B()].reverse()}
function settingsHTML(b){const t=TY[b.type],k=t[3],c=ctr(b);
 const R=(f,l,v,st=1)=>`<label>${l}<input type="number" data-f="${f}" value="${+(+v).toFixed(2)}" step="${st}"></label>`;
 let s='<div class="lb2">';
 if(k==='text')s+=`<label>${tt('Текст')}<textarea rows="3" data-f="text">${esc(b.text)}</textarea></label><div class="fr">${R('fs',tt('Шрифт (м)'),b.fs)}<label>${tt('Колір')}<input type="color" data-f="color" value="${b.color}"></label></div>`;
 else{s+=`<label>${tt('Назва')}<input data-f="label" value="${esc(lab(b))}"></label><label>${tt('Нотатка (у блоці, 70%)')}<textarea rows="2" data-f="note">${esc(b.note)}</textarea></label>`;
  if(!k)s+=`<div class="fr"><label>${tt('Колір')}<input type="color" data-f="color" value="${b.color}"></label><label>${tt('Штрихування')}<select data-f="hatch">${HATCH.map(h=>`<option value="${h[0]}"${h[0]===b.hatch?' selected':''}>${tt(h[1])}</option>`).join('')}</select></label></div><button data-act="resetColor">${tt('Стандартний колір')}</button>`;
  else s+=`<div class="fr"><label>${tt('Колір')}<input type="color" data-f="color" value="${b.color}"></label><button data-act="resetColor" style="align-self:flex-end">${tt('Стандартний колір')}</button></div>`}
 s+=`<div class="fr">${R('w',tt('Ширина (м)'),b.w,O().G)}${R('h',tt('Висота (м)'),b.h,O().G)}${R('cx',tt('Центр X (м)'),c.x,O().G)}${R('cy',tt('Центр Y (м)'),c.y,O().G)}</div>`;
 s+=`<div class="fr">${R('rot',tt('Поворот (°)'),b.rot,15)}<div class="rowb" style="align-items:flex-end"><button data-act="rotL">⟲ 90</button><button data-act="rotR">⟳ 90</button></div></div>`;
 if(!k){const cur=SHAPES.find(sh=>sh[2].every((v,i)=>v===b.cells[i]));
  s+=`<div class="shp"><div class="cg">${b.cells.map((v,i)=>`<button data-act="cell" data-i="${i}" class="${v?'on':''}" title="${tt('Клітинка {n}').replace('{n}',i+1)}"></button>`).join('')}</div><label>${tt('Форма')}<select data-f="shape">${cur?'':`<option value="custom" selected>${tt('Власна')}</option>`}${SHAPES.map(sh=>`<option value="${sh[0]}"${cur&&cur[0]===sh[0]?' selected':''}>${tt(sh[1])}</option>`).join('')}</select></label></div>`}
 s+=`<div class="rowb"><button data-act="up" title="${tt('Вище')}">▲</button><button data-act="down" title="${tt('Нижче')}">▼</button><button data-act="dup">${tt('Дублювати')}</button><button data-act="del">${tt('Видалити')}</button></div></div>`;
 return s}
function layerHTML(b){const t=TY[b.type],open=OPEN.has(b.id);
 return `<div class="ly${MS.has(b.id)?' sel':''}${b.hide?' off':''}" data-id="${b.id}"><div class="lh" data-act="sel"><span class="chip" style="background:${t[3]==='text'?'#555':(b.color||'#555')}">${iconSvg(b.type,2.2)}</span><span class="nm">${esc(nameOf(b))}</span><button class="ib" data-act="eye" title="${tt('Показати / сховати')}">${eyeIcon(b.hide)}</button><button class="ib" data-act="trash" title="${tt('Видалити блок')}">${trashIcon}</button><button class="ib" data-act="exp" title="${tt('Налаштування блоку')}">${open?'▾':'▸'}</button></div>${open?settingsHTML(b):''}</div>`}
function renderLayers(){const box=$('#layers'),sc=$('.left').scrollTop,l=listBlocks();
 box.innerHTML=l.length?l.map(layerHTML).join(''):`<p class="hint">${tt('У цьому місті ще немає блоків. Додайте їх із бібліотеки.')}</p>`;
 $('.left').scrollTop=sc}

// ---------- історія
function pushHist(){const j=JSON.stringify(B());if(hist[hist.length-1]===j)return;hist.push(j);if(hist.length>80)hist.shift()}
function commit(){pushHist();save();render()}
function undo(){if(hist.length<2)return;hist.pop();cur().blocks=JSON.parse(hist[hist.length-1]);selectMany([...MS].filter(i=>byId(i)));save();render()}
function del(){if(!MS.size)return;const ids=new Set(MS);cur().blocks=B().filter(b=>!ids.has(b.id));ids.forEach(i=>OPEN.delete(i));select(null);commit()}
function dup(){const bs=selBlocks();if(!bs.length)return;const ids=[];for(const b of bs){const n=JSON.parse(JSON.stringify(b));n.id=++seq;n.x+=O().G*2;n.y+=O().G*2;clampBlock(n);B().push(n);ids.push(n.id)}selectMany(ids);commit()}
function makeBlock(type,cx,cy){const t=TY[type];return normBlock({type,x:cx-t[2][0]/2,y:cy-t[2][1]/2,w:t[2][0],h:t[2][1]})}
function addBlock(type,px,py){if(!TY[type])return;const v=V();
 if(px==null){px=(svg.clientWidth/2-v.x)/v.z;py=(svg.clientHeight/2-v.y)/v.z}
 const b=makeBlock(type,px,py);if(O().snap){const G=O().G;b.x=Math.round(b.x/G)*G;b.y=Math.round(b.y/G)*G}
 clampBlock(b);B().push(b);select(b.id);commit()}
function unionBox(bs){let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;for(const b of bs){const a=aabb(b);x0=Math.min(x0,a.x);y0=Math.min(y0,a.y);x1=Math.max(x1,a.x+a.w);y1=Math.max(y1,a.y+a.h)}return{x:x0,y:y0,w:x1-x0,h:y1-y0}}
function shiftIntoWorld(bs){const u=unionBox(bs);let sx=0,sy=0;if(u.x<0)sx=-u.x;else if(u.x+u.w>WORLD)sx=WORLD-u.x-u.w;if(u.y<0)sy=-u.y;else if(u.y+u.h>WORLD)sy=WORLD-u.y-u.h;if(sx||sy)for(const b of bs){b.x+=sx;b.y+=sy}}
function rotateBy(d){const bs=selBlocks();if(!bs.length)return;
 if(bs.length===1){const b=bs[0];b.rot=((b.rot+d)%360+360)%360;
  if(O().snap&&b.rot%90===0){const G=O().G,a=aabb(b);b.x+=Math.round(a.x/G)*G-a.x;b.y+=Math.round(a.y/G)*G-a.y}
  clampBlock(b)}
 else{const u=unionBox(bs),gx=u.x+u.w/2,gy=u.y+u.h/2,r=d*Math.PI/180,co=Math.cos(r),si=Math.sin(r);
  for(const b of bs){const c=ctr(b),dx=c.x-gx,dy=c.y-gy;b.rot=((b.rot+d)%360+360)%360;b.x=gx+dx*co-dy*si-b.w/2;b.y=gy+dx*si+dy*co-b.h/2}
  shiftIntoWorld(bs)}
 commit()}
function moveZ(d){const a=B(),i=a.findIndex(b=>b.id===sel),j=i+d;if(i<0||j<0||j>=a.length)return;[a[i],a[j]]=[a[j],a[i]];commit()}

// ---------- місто, файли
function applyOpts(){const o=O();$('#tGrid').checked=o.grid;$('#tSnapGrid').checked=o.snap;$('#tMagnet').checked=o.magnet;$('#tMeters').checked=o.meters;$('#gridSize').value=o.G;
 $('#gp').setAttribute('width',o.G);$('#gp').setAttribute('height',o.G);$('#gpp').setAttribute('d',`M${o.G} 0H0V${o.G}`)}
function fillCities(){$('#citySel').innerHTML=Object.entries(S.cities).map(([k,c])=>`<option value="${esc(k)}">${esc(c.name||k)}</option>`).join('');$('#citySel').value=S.cur}
function openCity(n){S.cur=n;select(null);OPEN.clear();hist=[JSON.stringify(B())];fillCities();applyOpts();render();save()}
function newCity(){let n=prompt(tt('Назва нового міста:'),tt('Нове місто'));if(!n)return;n=n.trim().slice(0,80);if(!n)return;if(S.cities[n]){alert(tt('Місто з такою назвою вже є.'));return}
 S.cities[n]={blocks:[],view:defView()};openCity(n)}
$('#cityNew').onclick=newCity;$('#citySel').onchange=e=>openCity(e.target.value);
$('#cityDel').onclick=()=>{if(!confirm(tt('Видалити місто «{n}»?').replace('{n}',(cur().name||S.cur))))return;delete S.cities[S.cur];
 const k=Object.keys(S.cities);if(!k.length){S.cities['Нове місто']={blocks:[],view:defView()};k.push('Нове місто')}openCity(k[0])};
$('#expBtn').onclick=()=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(S,null,1)],{type:'application/json'}));a.download='city-planner-backup.json';document.body.appendChild(a);a.click();a.remove()};
$('#impBtn').onclick=()=>$('#impFile').click();
$('#impFile').onchange=e=>{const f=e.target.files[0];e.target.value='';if(!f)return;const r=new FileReader();
 r.onload=()=>{try{const d=sanitize(JSON.parse(r.result),false);const names=Object.keys(d.cities);if(!names.length)throw 0;let first=null;
  for(let n of names){const base=n;while(S.cities[n])n=base+' (імпорт)';S.cities[n]=d.cities[n];first=first||n}openCity(first)}catch(err){alert(tt('Не вдалося прочитати файл.'))}};r.readAsText(f)};

// ---------- інструменти
$('#defs').innerHTML=Object.values(HP).join('')+'<pattern id="gp" width="10" height="10" patternUnits="userSpaceOnUse"><path id="gpp" d="M10 0H0V10" fill="none" stroke="#fff6" stroke-width="1"/></pattern>';
function buildPalette(){$('#palette').innerHTML=Object.entries(TY).map(([id,t])=>`<div class="item" draggable="true" data-t="${id}"><i style="background:${t[1]||LC[id]||'#555'}">${iconSvg(id)}</i><span class="nm">${t.custom?esc(t[0]):tt(t[0])}</span>${t.custom?`<button class="ib del" data-del="${id}" title="${tt('Видалити зі своїх')}">${trashIcon}</button>`:''}</div>`).join('');}
const trashIcon='<svg viewBox="0 0 24 24" fill="none" stroke="#8f3430" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13M10 11v6M14 11v6"/></svg>';
let optsDirty=false;
buildPalette();
$('#palette').onclick=e=>{const d=e.target.closest('[data-del]');if(d){delCustom(d.dataset.del);return}const i=e.target.closest('.item');if(i)addBlock(i.dataset.t)};
function delCustom(id){if(!TY[id]||!TY[id].custom)return;if(!confirm(tt('Видалити іконку «')+TY[id][0]+tt('» з бібліотеки? Блоки цього типу на картах теж зникнуть.')))return;
 O().custom=O().custom.filter(c=>c.id!==id);cust(O().custom);
 for(const[k,c]of Object.entries(S.cities)){const n=c.blocks.length;c.blocks=c.blocks.filter(b=>b.type!==id);if(c.blocks.length!==n&&k!=='_')dirty.add(k)}
 if(S.cur){const c=cur();hist=[JSON.stringify(c.blocks)]}
 select(null);optsDirty=true;if(!HOST)save();buildPalette();render()}
// вікно «додати свою іконку»
let cImg='';
function dlgOpen(){$('#cName').value='';$('#cColor').value='#3b86c4';$('#cWhite').checked=true;$('#cFile').value='';cImg='';$('#cPrev').innerHTML='';$('#cOk').disabled=true;$('#dlg').classList.remove('hidden');$('#cName').focus()}
const dlgClose=()=>$('#dlg').classList.add('hidden');
function cPrev(){$('#cPrev').style.background=$('#cColor').value;$('#cPrev').innerHTML=cImg?`<img src="${cImg}">`:''}
function cBuild(file){const rd=new FileReader();rd.onload=()=>{const im=new Image();im.onload=()=>{const N=96,cv=document.createElement('canvas');cv.width=cv.height=N;const x=cv.getContext('2d');
  const r=Math.min(N/im.width,N/im.height);const w=im.width*r,h=im.height*r;x.drawImage(im,(N-w)/2,(N-h)/2,w,h);
  if($('#cWhite').checked){const d=x.getImageData(0,0,N,N),p=d.data;for(let i=0;i<p.length;i+=4){p[i]=p[i+1]=p[i+2]=255}x.putImageData(d,0,0)}
  cImg=cv.toDataURL('image/png');cPrev();$('#cOk').disabled=false};im.onerror=()=>{cImg='';cPrev();$('#cOk').disabled=true};im.src=rd.result};rd.readAsDataURL(file)}
let cSrc=null;
$('#libAdd').onclick=dlgOpen;$('#cCancel').onclick=dlgClose;
$('#cColor').oninput=cPrev;
$('#cFile').onchange=e=>{cSrc=e.target.files[0]||null;if(cSrc)cBuild(cSrc)};
$('#cWhite').onchange=()=>{if(cSrc)cBuild(cSrc)};
$('#cOk').onclick=()=>{if(!cImg||O().custom.length>=CUST_MAX)return;const id='c_'+Date.now().toString(36)+Math.random().toString(36).slice(2,5).replace(/[^a-z0-9]/g,'x');
 O().custom.push({id,name:($('#cName').value.trim()||tt('Своя іконка')).slice(0,40),color:$('#cColor').value,img:cImg});cust(O().custom);
 optsDirty=true;if(!HOST)save();buildPalette();dlgClose()};
$('#dlg').onclick=e=>{if(e.target.id==='dlg')dlgClose()};
$('#palette').ondragstart=e=>{const i=e.target.closest('.item');if(i)e.dataTransfer.setData('text/plain',i.dataset.t)};
svg.ondragover=e=>e.preventDefault();
svg.ondrop=e=>{e.preventDefault();const p=pt(e);addBlock(e.dataTransfer.getData('text/plain'),p.x,p.y)};
const opt=(id,k)=>$(id).onchange=e=>{O()[k]=e.target.checked;save();render(1)};
opt('#tGrid','grid');opt('#tSnapGrid','snap');opt('#tMagnet','magnet');opt('#tMeters','meters');
$('#gridSize').onchange=e=>{O().G=+e.target.value;applyOpts();save();render(1)};
function zoom(f,cx=svg.clientWidth/2,cy=svg.clientHeight/2){const v=V(),z=clamp(v.z*f,.03,4);f=z/v.z;v.x=cx-(cx-v.x)*f;v.y=cy-(cy-v.y)*f;v.z=z;delete v.auto;render(1);save()}
$('#zIn').onclick=()=>zoom(1.2);$('#zOut').onclick=()=>zoom(1/1.2);$('#zReset').onclick=()=>zoom(1/V().z);
$('#zCenter').onclick=()=>{const v=V();v.x=svg.clientWidth/2-WORLD/2*v.z;v.y=svg.clientHeight/2-WORLD/2*v.z;render(1);save()};
svg.addEventListener('wheel',e=>{e.preventDefault();const r=svg.getBoundingClientRect();zoom(e.deltaY<0?1.1:1/1.1,e.clientX-r.left,e.clientY-r.top)},{passive:false});
$('#bUndo').onclick=undo;$('#bDup').onclick=dup;$('#bRotL').onclick=()=>rotateBy(-90);$('#bRotR').onclick=()=>rotateBy(90);
document.addEventListener('selectstart',e=>{if(!/INPUT|TEXTAREA/.test(e.target.tagName||(e.target.parentElement||{}).tagName||''))e.preventDefault()});
addEventListener('keydown',e=>{if(/INPUT|SELECT|TEXTAREA/.test(e.target.tagName))return;
 if(e.key==='Delete'||e.key==='Backspace'){e.preventDefault();del()}
 else if(e.ctrlKey&&e.key.toLowerCase()==='z'){e.preventDefault();undo()}
 else if(e.ctrlKey&&e.key.toLowerCase()==='d'){e.preventDefault();dup()}
 else if(e.key==='Escape'){select(null);render()}
 else if(e.ctrlKey&&e.key.toLowerCase()==='a'){e.preventDefault();selectMany(B().filter(b=>!b.hide).map(b=>b.id));render()}
 else if(!e.ctrlKey&&e.key.toLowerCase()==='r'&&cb())rotateBy(e.shiftKey?-90:90);
 else if(e.key.startsWith('Arrow')&&MS.size){e.preventDefault();const bs=selBlocks(),st=e.shiftKey?1:O().G;
  for(const b of bs){if(e.key==='ArrowLeft')b.x-=st;if(e.key==='ArrowRight')b.x+=st;if(e.key==='ArrowUp')b.y-=st;if(e.key==='ArrowDown')b.y+=st}shiftIntoWorld(bs);render(1);pushHist();save()}});

// ---------- події панелі «Блоки»
const L=$('#layers');
L.addEventListener('click',e=>{const a=e.target.closest('[data-act]');if(!a)return;const ly=a.closest('.ly');const id=ly?+ly.dataset.id:null,b=id?byId(id):null,act=a.dataset.act;
 if(!b)return;const add=e.ctrlKey||e.shiftKey||e.metaKey;if(!['sel','eye','exp'].includes(act))select(id);
 if(act==='sel'){select(id,add);render()}
 else if(act==='exp'){if(!MS.has(id))select(id);OPEN.has(id)?OPEN.delete(id):OPEN.add(id);render()}
 else if(act==='eye'){b.hide=!b.hide;commit()}
 else if(act==='trash'){select(id);del()}
 else if(act==='rotL'){rotateBy(-90)}else if(act==='rotR'){rotateBy(90)}
 else if(act==='up')moveZ(1);else if(act==='down')moveZ(-1);else if(act==='dup')dup();else if(act==='del')del();
 else if(act==='resetColor'){b.color=defColor(b.type);commit()}
 else if(act==='cell'){const i=+a.dataset.i;b.cells[i]=!b.cells[i];if(!b.cells.some(Boolean))b.cells[i]=true;commit()}});
L.addEventListener('input',e=>{const el=e.target,f=el.dataset.f,ly=el.closest('.ly');if(!f||!ly)return;const b=byId(+ly.dataset.id);if(!b)return;
 if(f==='label'||f==='note'||f==='text'||f==='color'){b[f]=f==='label'?canonLabel(b.type,el.value):el.value;if(f==='label'||f==='text')ly.querySelector('.nm').textContent=nameOf(b);
  if(f==='color'&&TY[b.type][3]!=='text')ly.querySelector('.chip').style.background=b.color;render(1)}});
L.addEventListener('change',e=>{const el=e.target,f=el.dataset.f,ly=el.closest('.ly');if(!f||!ly)return;const b=byId(+ly.dataset.id);if(!b)return;if(!MS.has(b.id))select(b.id);
 if(f==='label'||f==='note'||f==='text'||f==='color'){pushHist();save();return}
 if(f==='hatch'){b.hatch=HP[el.value]?el.value:'none';commit();return}
 if(f==='shape'){const sh=SHAPES.find(s=>s[0]===el.value);if(sh){b.cells=sh[2].slice();b.fx=[1/3,2/3];b.fy=[1/3,2/3];commit()}return}
 const c=ctr(b),v=num(el.value,NaN);if(!Number.isFinite(v)){render();return}
 if(f==='w'||f==='h'){const n=Math.max(MIN,Math.min(WORLD,v));if(f==='w')b.w=n;else b.h=n;b.x=c.x-b.w/2;b.y=c.y-b.h/2}
 else if(f==='cx')b.x=v-b.w/2;else if(f==='cy')b.y=v-b.h/2;
 else if(f==='rot')b.rot=((v%360)+360)%360;else if(f==='fs')b.fs=clamp(v,4,500);
 clampBlock(b);pushHist();save();render()});

// ---------- миша
function pt(e){const r=svg.getBoundingClientRect(),v=V();return{x:(e.clientX-r.left-v.x)/v.z,y:(e.clientY-r.top-v.y)/v.z}}
svg.addEventListener('pointerdown',e=>{
 e.preventDefault();if(drag)return;const ae=document.activeElement;if(ae&&/INPUT|TEXTAREA|SELECT/.test(ae.tagName))ae.blur();
 svg.setPointerCapture(e.pointerId);const p=pt(e),t=e.target,ds=t.dataset||{},left=e.button===0,add=e.shiftKey||e.ctrlKey||e.metaKey,b=MS.size===1?cb():null;
 if(left&&b&&ds.h==='rot')drag={k:'rot',o:{...b},p};
 else if(left&&b&&ds.h)drag={k:'rs',dir:ds.h,o:{...b},p};
 else if(left&&b&&ds.sp)drag={k:'sp',w:ds.sp,o:{...b},p};
 else{const g=t.closest&&t.closest('.blk');
  if(g&&left){const id=+g.dataset.id;let collapse=null;
   if(add)select(id,true);else if(!MS.has(id))select(id);else if(MS.size>1)collapse=id;
   drag={k:'mv',os:selBlocks().map(x=>({...x})),p,collapse};render()}
  else if(left&&add)drag={k:'box',p,p2:p};
  else{if(left)select(null);drag={k:'pan',sx:e.clientX,sy:e.clientY,v:{...V()}};svg.classList.add('pan');render()}}
 drag.cx=e.clientX;drag.cy=e.clientY});
svg.addEventListener('pointermove',e=>{if(!drag)return;
 if(!drag.moved&&Math.hypot(e.clientX-drag.cx,e.clientY-drag.cy)>3)drag.moved=true;if(!drag.moved)return;
 if(drag.k==='pan'){const v=V();delete v.auto;v.x=drag.v.x+e.clientX-drag.sx;v.y=drag.v.y+e.clientY-drag.sy;render(1);return}
 const p=pt(e);
 if(drag.k==='box'){drag.p2=p;render(1);return}
 if(drag.k==='mv'){if(!drag.os.length)return;const dx=p.x-drag.p.x,dy=p.y-drag.p.y,ab=unionBox(drag.os);
  const[a,da]=sn(ab.x+dx,'x'),[c,dc]=sn(ab.x+ab.w+dx,'x'),[d,dd]=sn(ab.y+dy,'y'),[f,df]=sn(ab.y+ab.h+dy,'y');
  let mx=da<=dc?a-ab.x:c-ab.x-ab.w,my=dd<=df?d-ab.y:f-ab.y-ab.h;
  if(ab.x+mx<0)mx=-ab.x;else if(ab.x+ab.w+mx>WORLD)mx=WORLD-ab.x-ab.w;if(ab.y+my<0)my=-ab.y;else if(ab.y+ab.h+my>WORLD)my=WORLD-ab.y-ab.h;
  for(const o of drag.os){const b=byId(o.id);if(b){b.x=o.x+mx;b.y=o.y+my}}render(1);return}
 const b=cb();if(!b)return;const o=drag.o;
 if(drag.k==='rot'){const c=ctr(o);let ang=Math.atan2(p.y-c.y,p.x-c.x)*180/Math.PI+90;if(O().snap)ang=Math.round(ang/15)*15;b.rot=((Math.round(ang)%360)+360)%360}
 else if(drag.k==='sp'){const l=toLocal(o,p),G=O().G,i=+drag.w[0],j=+drag.w[1];
  let lx=l.x,ly=l.y;if(O().snap){lx=Math.round(lx/G)*G;ly=Math.round(ly/G)*G}
  const fx=o.fx.slice(),fy=o.fy.slice();
  fx[i]=i===0?clamp(lx/o.w,.05,fx[1]-.05):clamp(lx/o.w,fx[0]+.05,.95);fy[j]=j===0?clamp(ly/o.h,.05,fy[1]-.05):clamp(ly/o.h,fy[0]+.05,.95);b.fx=fx;b.fy=fy}
 else if(drag.k==='rs')resize(b,o,drag.dir,{x:clamp(p.x,0,WORLD),y:clamp(p.y,0,WORLD)});
 render(1)});
function resize(b,o,D,p){const r=rad(o),co=Math.cos(r),si=Math.sin(r),c0=ctr(o),dx=p.x-c0.x,dy=p.y-c0.y;
 const lx=dx*co+dy*si,ly=-dx*si+dy*co,ortho=Math.abs(o.rot%90)<1e-6;
 const snapL=(ax,val)=>{if(!ortho)return val;const u=ax==='x'?{x:co,y:si}:{x:-si,y:co},wa=Math.abs(u.x)>.5?'x':'y',sg=Math.sign(u[wa]);return(sn(c0[wa]+sg*val,wa,o.id)[0]-c0[wa])*sg};
 let l=-o.w/2,rr=o.w/2,t=-o.h/2,bt=o.h/2;
 if(D.includes('w'))l=Math.min(snapL('x',lx),rr-MIN);if(D.includes('e'))rr=Math.max(snapL('x',lx),l+MIN);
 if(D.includes('n'))t=Math.min(snapL('y',ly),bt-MIN);if(D.includes('s'))bt=Math.max(snapL('y',ly),t+MIN);
 const mx=(l+rr)/2,my=(t+bt)/2,cx=c0.x+mx*co-my*si,cy=c0.y+mx*si+my*co;
 b.w=rr-l;b.h=bt-t;b.x=cx-b.w/2;b.y=cy-b.h/2}
function endDrag(){if(!drag)return;const d=drag;drag=null;svg.classList.remove('pan');
 if(d.k==='box'){const x0=Math.min(d.p.x,d.p2.x),x1=Math.max(d.p.x,d.p2.x),y0=Math.min(d.p.y,d.p2.y),y1=Math.max(d.p.y,d.p2.y),ids=new Set(MS);
  if(d.moved)for(const b of B()){if(b.hide)continue;const a=aabb(b);if(a.x<x1&&a.x+a.w>x0&&a.y<y1&&a.y+a.h>y0)ids.add(b.id)}
  selectMany([...ids]);render();return}
 if(d.moved&&d.k!=='pan'){const b=cb();if(b&&d.k!=='mv')clampBlock(b);commit()}
 else{if(d.k==='mv'&&d.collapse)select(d.collapse);save();if(d.k==='pan'||d.collapse)render()}}
svg.addEventListener('pointerup',endDrag);svg.addEventListener('pointercancel',endDrag);
svg.addEventListener('contextmenu',e=>e.preventDefault());
let rw=0,rh=0;
function onResize(){const w=svg.clientWidth,h=svg.clientHeight;if(w===rw&&h===rh)return;rw=w;rh=h;const c=S.cur&&cur();if(c&&c.view.auto){const v=c.view;v.x=svg.clientWidth/2-WORLD/2*v.z;v.y=svg.clientHeight/2-WORLD/2*v.z}render(1)}
window.addEventListener('resize',onResize);if(window.ResizeObserver)new ResizeObserver(onResize).observe(svg);

// ---------- експорт карти
function hostExport(kind,c){pendingExport={kind,name:(cur().name||'city'),data:c.toDataURL('image/png')}}
function mapImage(done){const bs=B().filter(b=>!b.hide);if(!bs.length){alert(tt('Немає блоків для експорту.'));return}
 const u=unionBox(bs),m=40,x=Math.max(0,u.x-m),y=Math.max(0,u.y-m),w=Math.min(WORLD,u.x+u.w+m)-x,h=Math.min(WORLD,u.y+u.h+m)-y,o=O();
 const sc=Math.min(2,4096/Math.max(w,h)),pw=Math.max(1,Math.round(w*sc)),ph=Math.max(1,Math.round(h*sc));
 const defs=Object.values(HP).join('')+`<pattern id="gp" width="${o.G}" height="${o.G}" patternUnits="userSpaceOnUse"><path d="M${o.G} 0H0V${o.G}" fill="none" stroke="#fff6" stroke-width="1"/></pattern>`;
 const R=(f)=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${f}"/>`;
 const str=`<svg xmlns="http://www.w3.org/2000/svg" width="${pw}" height="${ph}" viewBox="${x} ${y} ${w} ${h}"><defs>${defs}</defs>${R('#6f9c4c')}${o.grid?R('url(#gp)'):''}${bs.map(blockSVG).join('')}${o.meters?metersMarkup(sc):''}</svg>`;
 const img=new Image();img.onload=()=>{const c=document.createElement('canvas');c.width=pw;c.height=ph;c.getContext('2d').drawImage(img,0,0,pw,ph);done(c)};
 img.onerror=()=>alert(tt('Не вдалося створити зображення.'));img.src='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(str)}
$('#expPng').onclick=()=>mapImage(c=>HOST?hostExport('png',c):c.toBlob(bl=>{const a=document.createElement('a');a.href=URL.createObjectURL(bl);a.download=(S.cur||'city').replace(/[\\/:*?"<>|]/g,'_')+'.png';document.body.appendChild(a);a.click();a.remove()},'image/png'));
$('#expPdf').onclick=()=>mapImage(c=>{if(HOST){hostExport('pdf',c);return}const f=document.createElement('iframe');f.style.cssText='position:fixed;left:-9999px;top:0;width:0;height:0;border:0';document.body.appendChild(f);
 f.srcdoc='<!doctype html><meta charset="utf-8"><style>@page{margin:8mm}html,body{margin:0}img{display:block;max-width:100%;max-height:185mm;margin:auto}</style><img src="'+c.toDataURL('image/png')+'">';
 f.onload=()=>{const go=()=>{f.contentWindow.focus();f.contentWindow.print();setTimeout(()=>f.remove(),60000)},im=f.contentDocument.querySelector('img');im.complete?go():im.onload=go}});

// ---------- старт
let lastSig='';
if(HOST){
 $('#expPdf').textContent='Зберегти PDF';
 S.opts=cleanOpts(null);S.cities={_:{host:true,name:'—',blocks:[],view:defView()}};S.cur='_';openCity('_');setLang(Q.get('lang')||'uk');
 window.CM={
  apply(j){if(j.bg)document.documentElement.style.setProperty('--paper',j.bg);if(j.lang&&j.lang!==LANG)setLang(j.lang);
   const sig=JSON.stringify((j.cities||[]).map(c=>[c.id,c.name]));if(!j.planner&&!j.cur&&sig===lastSig)return;lastSig=sig;
   const pl=j.planner,old=S.cities,nc={};if(pl){S.opts=cleanOpts(pl.opts);buildPalette()}
   for(const c of j.cities||[]){const prev=old[c.id];if(prev&&prev.host){prev.name=c.name;nc[c.id]=prev;continue}
    const d=((pl&&pl.cities)||{})[c.id]||{};
    nc[c.id]={host:true,name:c.name,blocks:(Array.isArray(d.blocks)?d.blocks:[]).map(normBlock).filter(Boolean),view:okView(d.view)}}
   if(!Object.keys(nc).length)nc._={host:true,name:'—',blocks:[],view:defView()};
   const prevCur=S.cur;S.cities=nc;for(const k of[...dirty])if(!nc[k])dirty.delete(k);
   const want=j.cur&&nc[j.cur]?j.cur:(nc[prevCur]?prevCur:(pl&&pl.cur&&nc[pl.cur]?pl.cur:Object.keys(nc)[0]));
   if(want===prevCur&&old[want]){fillCities();applyOpts();render()}else openCity(want)},
  take(){if(!dirty.size&&!pendingExport&&!optsDirty)return null;const out={cur:S.cur,opts:S.opts,cities:{}};
   for(const k of dirty){const c=S.cities[k];if(c&&k!=='_')out.cities[k]={blocks:c.blocks,view:{x:c.view.x,y:c.view.y,z:c.view.z}}}
   if(pendingExport){out.export=pendingExport;pendingExport=null}dirty.clear();optsDirty=false;return JSON.stringify(out)},
  undo};
}else{
if(!Object.keys(S.cities).length){S.cities['Нове місто']={blocks:[],view:defView()};S.cur='Нове місто'}
openCity(S.cities[S.cur]?S.cur:Object.keys(S.cities)[0]);
 setLang(Q.get('lang')||'uk');
}
