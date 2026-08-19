const revealTargets=[...document.querySelectorAll('.manifestText,.manifestCopy,.numbers>div,.sectionHead>*,.ritual,.waterCopy,.waterCards article,.sommelierCopy>*,.italyTitle>*,.destinations article,.expertWorld>*,.finalContent>*')];
revealTargets.forEach(el=>el.classList.add('reveal'));
const observer=new IntersectionObserver(entries=>{entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('visible');observer.unobserve(entry.target)}})},{threshold:.12,rootMargin:'0px 0px -45px 0px'});
revealTargets.forEach(el=>observer.observe(el));

const heroVideo=document.querySelector('.hero video');
const finalVideo=document.querySelector('.final video');
function playMedia(){[heroVideo,finalVideo].forEach(v=>{if(v&&v.paused){const p=v.play();if(p&&p.catch)p.catch(()=>{})}})}
addEventListener('pointerdown',playMedia,{once:true});
addEventListener('touchstart',playMedia,{once:true});

let ticking=false;
addEventListener('scroll',()=>{
  if(ticking)return;
  ticking=true;
  requestAnimationFrame(()=>{
    const y=scrollY;
    const hero=document.querySelector('.hero');
    if(hero&&y<innerHeight*1.15){
      const shift=Math.min(34,y*.025);
      if(heroVideo)heroVideo.style.transform=`scale(1.025) translateY(${shift}px)`;
    }
    ticking=false;
  });
},{passive:true});
