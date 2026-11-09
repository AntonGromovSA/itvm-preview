import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

// Independently authored geometry and shaders. No reference-site assets or source code.
const TAU = Math.PI * 2;
function generator(seed: number) { return () => { seed = (1664525 * seed + 1013904223) >>> 0; return seed / 4294967296; }; }
const deform = `
  vec3 drift(vec3 p) {
    p.x += sin(p.y * .55 + uTime * .28) * .16;
    p.z += cos(p.y * .42 - uTime * .21) * .15;
    return p;
  }
`;

export function createScene(stage: HTMLElement, initialPaused: boolean) {
  const canvas = stage.querySelector('canvas')!;
  let renderer: THREE.WebGLRenderer;
  try { renderer = new THREE.WebGLRenderer({ canvas, alpha: false, antialias: false, powerPreference: 'high-performance' }); }
  catch { return; }
  const mobile = matchMedia('(max-width: 650px)').matches;
  const rand = generator(198704);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(44, 1, .1, 90);
  camera.position.z = 11;
  renderer.setPixelRatio(Math.min(devicePixelRatio, mobile ? 1.25 : 1.6));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.08;
  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  const bloom = new UnrealBloomPass(new THREE.Vector2(1, 1), .62, .7, .72);
  composer.addPass(bloom);
  composer.addPass(new OutputPass());

  const world = new THREE.Group();
  scene.add(world);
  const time = { value: 0 }, pointerUniform = { value: new THREE.Vector2() };
  const dnaOpacity = { value: 1 }, moleculeOpacity = { value: 1 }, membraneOpacity = { value: 0 };
  const heightUniform = { value: 900 };

  // Ink-wash landscape: layered jade mountains, drifting mist and a muted bronze moon.
  const atmosphere = new THREE.ShaderMaterial({
    uniforms: { uTime: time, uPointer: pointerUniform, uAspect: { value: 1 } },
    depthTest: false, depthWrite: false,
    vertexShader: `varying vec2 vUv;void main(){vUv=uv;gl_Position=vec4(position.xy, .999, 1.);}`,
    fragmentShader: `
      varying vec2 vUv; uniform float uTime; uniform vec2 uPointer; uniform float uAspect;
      float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
      float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1.,0.)),f.x),mix(hash(i+vec2(0.,1.)),hash(i+1.),f.x),f.y);}
      float fbm(vec2 p){float n=0.,a=.5;for(int i=0;i<5;i++){n+=a*noise(p);p=mat2(.8,.6,-.6,.8)*p*2.04;a*=.5;}return n;}
      void main(){
        vec2 uv=vUv+uPointer*vec2(.025,.02); vec2 p=uv*vec2(uAspect,1.);
        float clouds=fbm(p*3.2+vec2(uTime*.007,-uTime*.004));
        float green=exp(-length((uv-vec2(.75,.6))*vec2(1.,.8))*2.);
        vec3 color=vec3(.012,.024,.022);
        color+=vec3(.026,.059,.047)*green*(.6+clouds*.65);
        // Paper fibres remain still; only the atmosphere drifts.
        float fibres=noise(vec2(p.x*260.,p.y*48.))*.6+noise(p*650.)*.4;
        color+=(fibres-.5)*.009;
        vec2 moonP=(uv-vec2(.79,.76))*vec2(uAspect,1.);
        float moonR=length(moonP);
        float moon=1.-smoothstep(.086,.089,moonR);
        float patina=fbm(p*35.);
        color=mix(color,vec3(.16,.145,.087)*(.7+patina*.4),moon*.55);
        color+=vec3(.026,.023,.011)*exp(-moonR*8.);
        // Each ridge is a different plane; cursor parallax increases toward the viewer.
        for(int i=0;i<4;i++){
          float layer=float(i);
          float x=uv.x+uPointer.x*(.006+layer*.009);
          float ridge=.21+layer*.045
            +pow(.5+.5*sin(x*6.2+layer*1.9),3.)*(.16-layer*.014)
            +noise(vec2(x*9.+layer*5.,layer+1.))*.085;
          float edge=smoothstep(ridge+.012,ridge-.012,uv.y);
          vec3 ink=mix(vec3(.032,.065,.054),vec3(.007,.023,.021),layer/3.);
          color=mix(color,ink,edge*(.48+layer*.12));
          float mist=exp(-pow((uv.y-ridge-.018)/.055,2.));
          color+=vec3(.014,.023,.019)*mist*(.4+clouds);
        }
        float cloudRibbon=exp(-pow((uv.y-.39-sin(uv.x*3.+uTime*.015)*.045)/.13,2.));
        color+=vec3(.013,.023,.018)*cloudRibbon*clouds;
        float vignette=smoothstep(.9,.16,length((vUv-.5)*vec2(.9,1.)));
        color*=.64+.36*vignette;
        float grain=(hash(gl_FragCoord.xy)-.5)*.004;
        gl_FragColor=vec4(color+grain,1.);
      }
    `
  });
  const backdrop = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), atmosphere);
  backdrop.frustumCulled = false; backdrop.renderOrder = -100; scene.add(backdrop);

  function cloud(positions: number[], colors: number[], sizes: number[], opacity: {value:number}, options: {dna?:boolean; haze?:boolean} = {}) {
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    geometry.setAttribute('aSize', new THREE.Float32BufferAttribute(sizes, 1));
    const material = new THREE.ShaderMaterial({
      uniforms: {uTime:time,uOpacity:opacity,uHeight:heightUniform,uDna:{value:options.dna?1:0},uHaze:{value:options.haze?1:0}},
      vertexColors: true, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
      vertexShader: `
        attribute float aSize; uniform float uTime,uHeight,uDna; varying vec3 vColor; varying float vDepth,vPulse;
        ${deform}
        void main(){vec3 p=position;if(uDna>.5)p=drift(p);else{p.x+=sin(uTime*.065+p.y*.4)*.08;p.y+=cos(uTime*.08+p.x)*.06;}
          vec4 mv=modelViewMatrix*vec4(p,1.);vDepth=-mv.z;vColor=color;
          vPulse=uDna>.5?.7+.3*sin(p.y*3.-uTime*1.1):.82+.18*sin(position.x*2.+uTime*.6);
          float blur=1.+max(0.,5.5-vDepth)*1.1+max(0.,vDepth-15.)*.14;
          gl_PointSize=clamp(aSize*uHeight/max(1.,vDepth)*blur,1.,110.);gl_Position=projectionMatrix*mv;
        }`,
      fragmentShader: `
        uniform float uOpacity,uHaze,uDna;varying vec3 vColor;varying float vDepth,vPulse;
        void main(){float d=length(gl_PointCoord-.5)*2.;if(d>1.)discard;
          float focused=smoothstep(4.,8.,vDepth)*(1.-smoothstep(18.,30.,vDepth));
          float bokeh=pow(max(0.,1.-d*d),1.65)*.25;
          float sharp=pow(max(0.,1.-d),1.8);
          float alpha=mix(bokeh,sharp,focused)*(1.-smoothstep(24.,48.,vDepth));
          alpha*=uHaze>.5?.32:1.;
          gl_FragColor=vec4(vColor*vPulse,alpha*uOpacity);
        }`
    });
    const mesh = new THREE.Points(geometry, material); mesh.frustumCulled = false;
    return mesh;
  }

  const dna = new THREE.Group(); world.add(dna);
  const linePositions: number[] = [], lineColors: number[] = [];
  const seedPositions: number[] = [], seedColors: number[] = [], seedSizes: number[] = [];
  function helix(y: number, side: number, strand: number) {
    const phase = strand * 2.39996;
    const a = y * .73 + side * Math.PI + Math.sin(y * .77 + phase) * .15 + Math.sin(y*2.2+phase*3.)*.018;
    const r = 1.14 + Math.cos(phase) * .13 + Math.sin(y * 1.55 + phase) * .08;
    return new THREE.Vector3(Math.cos(a) * r + Math.sin(y * .32) * .25, y, Math.sin(a) * r + Math.cos(y * .23) * .3 + Math.sin(phase) * .12);
  }
  function segment(a: THREE.Vector3, b: THREE.Vector3, brightness: number) {
    linePositions.push(...a.toArray(), ...b.toArray());
    for (let i=0;i<2;i++) lineColors.push(1.2*brightness,.48*brightness,.13*brightness);
  }
  const strandCount = mobile ? 15 : 28;
  const samples = mobile ? 300 : 500;
  for(let side=0;side<2;side++)for(let strand=0;strand<strandCount;strand++) {
    let previous = helix(-10,side,strand);
    const base = .2+rand()*.48;
    for(let i=1;i<=samples;i++) {
      const y=i/samples*20-10;
      const p=helix(y,side,strand);
      const sparkle=.65+.35*Math.sin(y*4.2+strand*3.8);
      segment(previous,p,base*sparkle);
      if(i%2===0&&rand()>.35){seedPositions.push(...p.toArray());const b=.5+Math.pow(rand(),4)*2;seedColors.push(1.5*b,.67*b,.2*b);seedSizes.push(.017+rand()*.023);}
      previous=p;
    }
  }
  // Irregular bundles connect the two backbones; never perfectly straight ladder rungs.
  for(let rung=0;rung<29;rung++)for(let thread=0;thread<(mobile?3:7);thread++) {
    const y=-9.5+rung*.68;
    const a=helix(y+thread*.017,0,thread*2),b=helix(y+thread*.017,1,thread*2);
    let previous=a;
    for(let s=1;s<=28;s++) {
      const t=s/28,p=a.clone().lerp(b,t);
      p.y+=Math.sin(t*Math.PI)*(.05*Math.sin(thread*2+rung)+.065);
      p.z+=Math.sin(t*Math.PI)*.13*Math.cos(rung+thread);
      segment(previous,p,.13+rand()*.18);
      if(s%4===0){seedPositions.push(...p.toArray());seedColors.push(.65,.31,.075);seedSizes.push(.022);}
      previous=p;
    }
  }
  const filamentGeometry=new THREE.BufferGeometry();
  filamentGeometry.setAttribute('position',new THREE.Float32BufferAttribute(linePositions,3));
  filamentGeometry.setAttribute('color',new THREE.Float32BufferAttribute(lineColors,3));
  const filamentMaterial=new THREE.ShaderMaterial({
    uniforms:{uTime:time,uOpacity:dnaOpacity},vertexColors:true,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,
    vertexShader:`uniform float uTime;varying vec3 vColor;varying float vY,vDepth;${deform}void main(){vec3 p=drift(position);vec4 mv=modelViewMatrix*vec4(p,1.);vDepth=-mv.z;vColor=color;vY=p.y;gl_Position=projectionMatrix*mv;}`,
    fragmentShader:`uniform float uOpacity,uTime;varying vec3 vColor;varying float vY,vDepth;void main(){float pulse=.7+.3*sin(vY*2.7-uTime*.7);float fog=1.-smoothstep(12.,24.,vDepth);gl_FragColor=vec4(vColor*pulse,.6*uOpacity*fog);}`
  });
  dna.add(new THREE.LineSegments(filamentGeometry,filamentMaterial));
  dna.add(cloud(seedPositions,seedColors,seedSizes,dnaOpacity,{dna:true}));

  // Curving molecular chains at different distances, with actual three-dimensional bonds.
  const molecules=new THREE.Group();world.add(molecules);
  const atomPositions:number[]=[],atomColors:number[]=[],atomSizes:number[]=[],bondPositions:number[]=[];
  for(let chain=0;chain<(mobile?11:24);chain++) {
    const x=(rand()-.5)*17, y=(rand()-.5)*16, z=-2-rand()*16;
    let previous:THREE.Vector3|undefined;
    const direction=rand()*TAU;
    for(let i=0;i<55;i++) {
      const t=i/54, p=new THREE.Vector3(x+Math.sin(t*6+direction)*(.65+chain%3*.2)+t*1.5,y+(t-.5)*4+Math.cos(t*9)*.25,z+Math.cos(t*5+chain)*.7);
      atomPositions.push(...p.toArray());
      const intensity=.32+rand()*.8;atomColors.push(.035*intensity,.42*intensity,.25*intensity);atomSizes.push(.025+rand()*.028);
      if(previous)bondPositions.push(...previous.toArray(),...p.toArray());
      previous=p;
    }
  }
  molecules.add(cloud(atomPositions,atomColors,atomSizes,moleculeOpacity));
  const bonds=new THREE.LineSegments(new THREE.BufferGeometry().setAttribute('position',new THREE.Float32BufferAttribute(bondPositions,3)),new THREE.LineBasicMaterial({color:'#137858',transparent:true,opacity:.13,depthWrite:false,blending:THREE.AdditiveBlending}));
  molecules.add(bonds);
  // Sparse foreground molecules supply readable, softly defocused beads and curved links.
  const foreground=new THREE.Group();world.add(foreground);
  for(let k=0;k<(mobile?2:5);k++) {
    const pos:number[]=[],colors:number[]=[],sizes:number[]=[],verts:THREE.Vector3[]=[];
    for(let i=0;i<12;i++){const t=i/11;const p=new THREE.Vector3(Math.sin(t*5+k)*.5,t*2.7-1.3,Math.cos(t*4)*.3);pos.push(...p.toArray());colors.push(.08,.43,.31);sizes.push(i%3===0?.11:.045);verts.push(p);}
    const g=new THREE.Group();g.add(cloud(pos,colors,sizes,moleculeOpacity));
    g.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(verts),new THREE.LineBasicMaterial({color:'#25694e',transparent:true,opacity:.12,depthWrite:false})));
    g.position.set(1.2+k*1.2,-2+k*.6,k%2===0?3.8:-3);g.rotation.z=k*.5-.4;foreground.add(g);
  }

  const particles=new THREE.Group();world.add(particles);
  const haloPos:number[]=[],haloColors:number[]=[],haloSizes:number[]=[];
  for(let i=0;i<(mobile?450:1700);i++){
    const y=(rand()-.5)*18,a=y*.6+rand()*TAU,r=1.7+Math.pow(rand(),2)*2.7;
    haloPos.push(Math.cos(a)*r+.5,y,Math.sin(a)*r-2.5);
    const b=.25+rand()*.75;haloColors.push(.015*b,.46*b,.23*b);haloSizes.push(.018+rand()*.04);
  }
  particles.add(cloud(haloPos,haloColors,haloSizes,{value:1}));
  for(let layer=0;layer<3;layer++) {
    const pos:number[]=[],colors:number[]=[],sizes:number[]=[];
    const count=mobile?[400,240,35][layer]:[2100,1100,90][layer];
    for(let i=0;i<count;i++) {
      const x=(rand()-.5)*(layer===2?14:32),y=(rand()-.5)*24,z=layer===0?-5-rand()*25:layer===1?-8+rand()*13:3+rand()*3;
      pos.push(x,y,z);
      const b=.18+Math.pow(rand(),2)*.8,hue=rand();
      if(hue>.975) colors.push(.5*b,.025*b,.09*b);
      else if(hue>.91)colors.push(.6*b,.43*b,.03*b);
      else colors.push(.035*b,.48*b,.24*b);
      sizes.push(layer===2?.06+rand()*.12:.018+rand()*.045);
    }
    particles.add(cloud(pos,colors,sizes,{value:1},{haze:layer===2}));
  }

  // Vesicles remain distinct from DNA, entering as separate membrane spheres in chapter two.
  const vesicles=new THREE.Group();world.add(vesicles);
  const membraneMaterial=new THREE.ShaderMaterial({
    uniforms:{uTime:time,uOpacity:membraneOpacity},transparent:true,depthWrite:false,side:THREE.FrontSide,
    vertexShader:`uniform float uTime;varying vec3 vNormal,vEye,vPosition;void main(){vec3 p=position*(1.+.014*sin(position.y*5.+uTime*.45)*cos(position.x*4.-uTime*.3));vec4 mv=modelViewMatrix*vec4(p,1.);vNormal=normalize(normalMatrix*normal);vEye=normalize(-mv.xyz);vPosition=p;gl_Position=projectionMatrix*mv;}`,
    fragmentShader:`uniform float uTime,uOpacity;varying vec3 vNormal,vEye,vPosition;void main(){float rim=pow(1.-max(dot(normalize(vNormal),normalize(vEye)),0.),2.7);float texture=sin(vPosition.x*85.)*sin(vPosition.y*75.)*sin(vPosition.z*90.);vec3 c=mix(vec3(.055,.22,.15),vec3(.46,.78,.53),rim);gl_FragColor=vec4(c,(.018+rim*.58+texture*.015)*uOpacity);}`
  });
  for(let k=0;k<4;k++) {
    const g=new THREE.Group(),r=k===0?1.36:.42+k*.11;
    g.add(new THREE.Mesh(new THREE.SphereGeometry(r,mobile?32:64,mobile?24:48),membraneMaterial));
    const pos:number[]=[],cols:number[]=[],sizes:number[]=[];
    const n=mobile?700:1900;
    for(let i=0;i<n;i++){const y=1-2*(i+.5)/n,a=i*2.399963,rad=Math.sqrt(1-y*y);pos.push(Math.cos(a)*rad*r,y*r,Math.sin(a)*rad*r);cols.push(.14,.44,.25);sizes.push(.017+rand()*.016);}
    for(let i=0;i<45;i++){pos.push((rand()-.5)*r*1.4,(rand()-.5)*r*1.4,(rand()-.5)*r*1.4);cols.push(.42,.56,.22);sizes.push(.04+rand()*.035);}
    g.add(cloud(pos,cols,sizes,membraneOpacity));
    g.position.set(k===0?2.7:2.7+Math.sin(k*3)*3,k===0?0:Math.cos(k*3)*2.6,k===0?1:-3-k*.4);
    vesicles.add(g);
  }

  let paused=initialPaused, visible=true, raf=0, last=0, disposed=false, elapsed=0;
  let targetScroll=0, smoothScroll=0;
  const pointer=new THREE.Vector2(),smoothPointer=new THREE.Vector2();
  const story=stage.parentElement!;
  const chapterLinks=Array.from(document.querySelectorAll<HTMLAnchorElement>('[data-science-chapter]'));
  const chapters=Array.from(story.querySelectorAll<HTMLElement>('.science-step'));
  function scrollPosition(){
    const y=scrollY-story.offsetTop;
    for(let i=chapters.length-1;i>=0;i--){
      const top=chapters[i].offsetTop;
      if(y>=top)return Math.min(3,i+(y-top)/Math.max(1,chapters[i].offsetHeight));
    }
    return 0;
  }
  function syncScene(dt:number,instant=false){
    const small=stage.clientWidth<650;
    const damping=instant?1:1-Math.exp(-dt*3.6);
    smoothScroll=THREE.MathUtils.lerp(smoothScroll,targetScroll,damping);
    smoothPointer.lerp(paused?new THREE.Vector2():pointer,instant?1:1-Math.exp(-dt*3.1));
    const p=smoothScroll;
    const closeup=THREE.MathUtils.smoothstep(p,.15,1.1);
    const returnDna=THREE.MathUtils.smoothstep(p,2.15,3);
    dnaOpacity.value=(1-closeup*.97)+returnDna*.32;
    membraneOpacity.value=THREE.MathUtils.smoothstep(p,.45,1.05)*(1-THREE.MathUtils.smoothstep(p,1.65,2.6)*.75);
    moleculeOpacity.value=.75+THREE.MathUtils.smoothstep(p,1.35,2.1)*.25;
    dna.visible=dnaOpacity.value>.015;
    vesicles.visible=membraneOpacity.value>.005;
    dna.position.set(small?.35:.2,small?-1.35:.1,-closeup*4+returnDna*2);
    dna.rotation.set(.035*Math.sin(elapsed*.14),elapsed*.15+.38,-.12+Math.sin(elapsed*.1)*.028+returnDna*.2);
    dna.scale.setScalar(small?.66:1);
    vesicles.position.set(small?-2.2:0,small?-1.65:0,-3+closeup*3.1);
    vesicles.rotation.y=Math.sin(elapsed*.1)*.08;
    molecules.rotation.y=Math.sin(elapsed*.03)*.035;
    molecules.position.x=-p*.25;
    foreground.position.x=-p*.17;
    foreground.rotation.y=Math.sin(elapsed*.06)*.04;
    world.rotation.y=smoothPointer.x*.035;
    world.rotation.x=-smoothPointer.y*.025;
    camera.position.set(smoothPointer.x*.72,smoothPointer.y*.42,11-closeup*.65+returnDna*.55);
    camera.lookAt(smoothPointer.x*.14,small?-.45:0,0);
    pointerUniform.value.copy(smoothPointer);
    time.value=elapsed;
    stage.dataset.chapter=String(Math.round(p));
    for(const [i,link]of chapterLinks.entries())if(i===Math.round(p))link.setAttribute('aria-current','step');else link.removeAttribute('aria-current');
  }
  function render(){if(!disposed)composer.render();}
  function tick(now:number){raf=0;if(disposed||paused||!visible||document.hidden)return;const dt=Math.min((now-last)/1000,.05);last=now;elapsed+=dt;syncScene(dt);render();raf=requestAnimationFrame(tick);}
  function start(){if(!raf&&!paused&&visible&&!document.hidden){last=performance.now();raf=requestAnimationFrame(tick);}}
  function stop(){cancelAnimationFrame(raf);raf=0;}
  function resize(){const w=stage.clientWidth,h=stage.clientHeight;renderer.setSize(w,h,false);composer.setSize(w,h);heightUniform.value=h*renderer.getPixelRatio();camera.aspect=w/h;camera.updateProjectionMatrix();atmosphere.uniforms.uAspect.value=w/h;targetScroll=scrollPosition();syncScene(0,true);render();}
  function onPointer(e:PointerEvent){if(e.pointerType!=='mouse'||paused)return;pointer.set(e.clientX/innerWidth*2-1,1-e.clientY/innerHeight*2);start();}
  function onLeave(){pointer.set(0,0);}
  function onScroll(){targetScroll=scrollPosition();if(paused){syncScene(0,true);render();}else start();}
  function onMotion(e:Event){paused=(e as CustomEvent<boolean>).detail;if(paused){stop();pointer.set(0,0);syncScene(0,true);render();}else start();}
  function onVisibility(){if(document.hidden)stop();else start();}
  const resizeObserver=new ResizeObserver(resize);resizeObserver.observe(stage);
  const observer=new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;if(visible){if(paused)render();else start();}else stop();});observer.observe(stage);
  addEventListener('pointermove',onPointer,{passive:true});document.documentElement.addEventListener('pointerleave',onLeave);
  addEventListener('scroll',onScroll,{passive:true});addEventListener('motion-change',onMotion);document.addEventListener('visibilitychange',onVisibility);
  canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();stop();stage.classList.remove('is-ready');});
  canvas.addEventListener('webglcontextrestored',()=>{resize();stage.classList.add('is-ready');start();});
  const cleanup=()=>{disposed=true;stop();resizeObserver.disconnect();observer.disconnect();removeEventListener('pointermove',onPointer);document.documentElement.removeEventListener('pointerleave',onLeave);removeEventListener('scroll',onScroll);removeEventListener('motion-change',onMotion);document.removeEventListener('visibilitychange',onVisibility);const materials=new Set<THREE.Material>();scene.traverse(o=>{if(o instanceof THREE.Mesh||o instanceof THREE.Points||o instanceof THREE.Line){o.geometry.dispose();(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>materials.add(m));}});materials.forEach(m=>m.dispose());composer.dispose();renderer.dispose();};
  addEventListener('pagehide',(e:PageTransitionEvent)=>{if(e.persisted)stop();else cleanup();});
  addEventListener('pageshow',(e:PageTransitionEvent)=>{if(e.persisted){resize();start();}});
  targetScroll=scrollPosition();resize();stage.classList.add('is-ready');start();
}
