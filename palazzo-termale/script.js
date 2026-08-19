// Official-content extensions. All informational text in injected sections is sourced from palazzotermale.ru.
const extensionStyles=document.createElement('link');
extensionStyles.rel='stylesheet';
extensionStyles.href='./official-extensions.css';
document.head.appendChild(extensionStyles);

// Keep ambiguous aquabar status conservative: the official homepage says "скоро открытие".
const programRows=[...document.querySelectorAll('.programList>div')];
if(programRows[0]) programRows[0].innerHTML='<b>Доступно</b><span>Гидропинотерапия: питьевые курсы природных минеральных вод.</span>';
if(programRows[1]) programRows[1].insertAdjacentHTML('afterend','<div class="soon"><b>Скоро открытие</b><span>Термальный аквабар с минеральными водами.</span></div>');

// Equipment branch: present in current official navigation.
const homeCards=document.querySelector('.homeCards');
if(homeCards) homeCards.insertAdjacentHTML('beforeend','<div><b>Дыхательные тренажёры</b><span>Отдельное направление оборудования для ингаляций, представленное в актуальном меню Palazzo Termale.</span></div>');

// Hydrosommelier / Mineral Water Experience.
const home=document.querySelector('#home');
if(home){
  home.insertAdjacentHTML('beforebegin',`
<section class="hydrosommelier" id="hydrosommelier">
  <div class="hydroSomVisual"></div>
  <div class="hydroSomCopy">
    <div class="eyebrow">ГИДРОСОМЕЛЬЕ</div>
    <h2>Оксана<br>Ноччоли.</h2>
    <div class="hydroSomRole">Первый гидросомелье в России</div>
    <p>На официальном сайте Palazzo Termale Оксана Ноччоли представлена как эксперт по природным минеральным водам, water pairing, wellness-гастрономии и event-форматам и как автор концепции Mineral Water Experience.</p>
    <div class="waterServices">
      <div><b>Водные карты</b><span>Разработка водных карт и сценариев подачи воды для ресторанов, отелей и мероприятий.</span></div>
      <div><b>Water pairing</b><span>Подбор воды по минерализации, температуре и роли в гастрономическом сценарии.</span></div>
      <div><b>Mineral tasting</b><span>Знакомство гостей с разными типами природных минеральных вод.</span></div>
      <div><b>Wellness / Events</b><span>Форматы для fine dining, отелей и курортов, private events, кейтеринга и wellness-пространств.</span></div>
    </div>
    <a class="officialLink" href="https://palazzotermale.ru/whiteawards2025" target="_blank" rel="noopener">Mineral Water Experience на официальном сайте →</a>
  </div>
</section>`);
}

// MICE / professional education and current 2026 internship.
const italy=document.querySelector('#italy');
if(italy){
  italy.insertAdjacentHTML('beforebegin',`
<section class="mice" id="mice">
  <div class="miceHead">
    <div><div class="eyebrow">MICE · ОБУЧЕНИЕ · МЕДИЦИНСКИЙ ТУРИЗМ</div><h2>Практика.<br>Стажировки.<br>Италия.</h2></div>
    <p>В актуальном меню Palazzo Termale MICE объединяет международное экспертное сообщество, обучение и стажировки, практикумы, образовательные туры, материалы о термальных курортах Италии, их услугах и размещении.</p>
  </div>
  <div class="miceGrid">
    <article class="miceCard feature"><small>5–12 ИЮЛЯ 2026 · МОНТЕКАТИНИ ТЕРМЕ</small><h3>Стажировка с МИИН.<br>Поток 3.</h3><p>Организаторы — Palazzo Termale, Международный Институт Интегративной Нутрициологии и термальный курорт Монтекатини Терме. В программе: питьевое лечение минеральными водами, гидропинотерапия, практическая ингаляционная терапия, разбор клинических случаев и профессиональный нетворкинг.</p><div class="miceFacts"><span>лекции</span><span>практикумы</span><span>гидропинотерапия</span><span>ингаляции</span><span>сертификат</span></div><a class="officialLink" href="https://palazzotermale.ru/montecatini_5_12_luglio_26" target="_blank" rel="noopener">Программа 2026 →</a></article>
    <article class="miceCard"><small>ПРОФЕССИОНАЛЬНОЕ ОБУЧЕНИЕ</small><h3>Обучение.<br>Обмен опытом.</h3><p>Palazzo Termale организует образовательные программы и профессиональные стажировки на термальных курортах Италии с посещением термальных комплексов, знакомством с бальнеотерапией и ингаляционными методиками.</p><a class="officialLink" href="https://palazzotermale.ru/eventi" target="_blank" rel="noopener">Обучение →</a></article>
    <article class="miceCard"><small>РАЗМЕЩЕНИЕ</small><h3>Термальные<br>курорты.</h3><p>В текущем меню проекта отдельно представлены курорты Кьянчано, Телезе, Монтекатини и Нитроди, а также страницы размещения, включая Alexander Hotel Palme 4* в Кьянчано Терме.</p><a class="officialLink" href="https://palazzotermale.ru/alexander_hotel_palme" target="_blank" rel="noopener">Alexander Hotel Palme →</a></article>
  </div>
  <div class="miceCurrent"><span>АКТУАЛЬНО</span><b>5–12 июля 2026</b><p>Выездной семинар в Монтекатини Терме для руководителей, врачей, нутрициологов и ЗОЖ-коучей.</p></div>
</section>`);
}

// Other official project branches that exist as standalone Palazzo pages.
const contact=document.querySelector('#contact');
if(contact){
  contact.insertAdjacentHTML('beforebegin',`
<section class="ecosystem" id="ecosystem">
  <div class="ecosystemHead">
    <div><div class="eyebrow">ДРУГИЕ НАПРАВЛЕНИЯ PALAZZO TERMALE</div><h2>Проект<br>шире курорта.</h2></div>
    <p>На официальном сайте отдельно представлены программа лояльности, Институт обоняния и ольфакторной патологии, новости и клинические материалы. В прототипе они вынесены в отдельный уровень, чтобы не смешивать их с основным маршрутом гостя термального курорта.</p>
  </div>
  <div class="ecosystemGrid">
    <article class="ecoCard"><small>КЛУБ PALAZZO TERMALE</small><h3>«Орден<br>7 капель»</h3><p>Официальная программа лояльности и реферальная программа. На странице клуба опубликованы условия участия 2025–2026 и уровни «Путь», «Течение» и «Глубина».</p><div class="clubLevels"><span>Via · Путь</span><span>Flusso · Течение</span><span>Profondità · Глубина</span></div><a class="officialLink" href="https://palazzotermale.ru/club_palazzo_termale" target="_blank" rel="noopener">Клуб →</a></article>
    <article class="ecoCard"><small>МЕДИЦИНСКОЕ НАПРАВЛЕНИЕ</small><h3>Институт<br>обоняния.</h3><p>Институт обоняния и ольфакторной патологии занимается диагностикой и лечением нарушений обоняния. Руководитель — доктор медицинских наук Константин Григорьевич Добрецов.</p><a class="officialLink" href="https://palazzotermale.ru/institute_of_olfaction" target="_blank" rel="noopener">Институт →</a></article>
    <article class="ecoCard"><small>НОВОСТИ · ИССЛЕДОВАНИЯ</small><h3>Блог<br>Palazzo.</h3><p>Новости проекта, рекомендации специалистов, клинические исследования по минеральным водам, стажировки, конференции, акции и материалы партнёров.</p><a class="officialLink" href="https://palazzotermale.ru/blog" target="_blank" rel="noopener">Новости и акции →</a></article>
  </div>
</section>`);
}

// Add sourced navigation shortcuts without removing the existing ones.
const nav=document.querySelector('.topbar nav');
if(nav){
  const hydroLink=document.createElement('a'); hydroLink.href='#hydrosommelier'; hydroLink.textContent='Гидросомелье'; nav.appendChild(hydroLink);
  const miceLink=document.createElement('a'); miceLink.href='#mice'; miceLink.textContent='MICE'; nav.appendChild(miceLink);
}

const selectors=[
  '.overviewHead>*','.overviewGrid>a','.arbatCopy>*','.programList>div',
  '.sectionHead>*','.therapyGrid article','.complexes>div','.hydroCopy>*','.hydroFacts>div',
  '.waterTitle>*','.waterGrid article','.hydroSomCopy>*','.waterServices>div',
  '.homeCopy>*','.homeCards>div','.expertGrid article',
  '.researchCopy>*','.researchStats>div','.communityHead>*','.communityBody>*',
  '.miceHead>*','.miceCard','.miceCurrent>*',
  '.italyTitle>*','.destinations article','.latest>*','.experienceCopy>*','.shop>*',
  '.ecosystemHead>*','.ecoCard','.contactContent>*'
];
const revealTargets=[...document.querySelectorAll(selectors.join(','))];
revealTargets.forEach(el=>el.classList.add('reveal'));
const observer=new IntersectionObserver(entries=>{
  entries.forEach(entry=>{
    if(entry.isIntersecting){entry.target.classList.add('visible');observer.unobserve(entry.target)}
  })
},{threshold:.1,rootMargin:'0px 0px -40px 0px'});
revealTargets.forEach(el=>observer.observe(el));

const media=[...document.querySelectorAll('video')];
function playMedia(){media.forEach(v=>{if(v.paused){const p=v.play();if(p&&p.catch)p.catch(()=>{})}})}
addEventListener('pointerdown',playMedia,{once:true});
addEventListener('touchstart',playMedia,{once:true});

const heroVideo=document.querySelector('.hero video');
let ticking=false;
addEventListener('scroll',()=>{
  if(ticking)return;
  ticking=true;
  requestAnimationFrame(()=>{
    if(heroVideo && scrollY<innerHeight*1.15){
      const shift=Math.min(30,scrollY*.022);
      heroVideo.style.transform=`scale(1.025) translateY(${shift}px)`;
    }
    ticking=false;
  });
},{passive:true});
