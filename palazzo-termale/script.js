const selectors=[
  '.overviewHead>*','.overviewGrid>a','.arbatCopy>*','.programList>div',
  '.sectionHead>*','.therapyGrid article','.complexes>div','.hydroCopy>*','.hydroFacts>div',
  '.waterTitle>*','.waterGrid article','.homeCopy>*','.homeCards>div','.expertGrid article',
  '.researchCopy>*','.researchStats>div','.communityHead>*','.communityBody>*',
  '.italyTitle>*','.destinations article','.latest>*','.experienceCopy>*','.shop>*','.contactContent>*'
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
