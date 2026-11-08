import { useEffect, useRef, useState } from 'react';
import type * as Three from 'three';
interface Props { src:string; poster?:string; label:string }
export default function ModelViewer({src,poster,label}:Props) {
  const host=useRef<HTMLDivElement>(null);
  const [status,setStatus]=useState('Загрузка модели…');
  useEffect(()=>{
    let cancelled=false;let dispose=()=>{};
    (async()=>{
      const [T,{GLTFLoader},{OrbitControls}]=await Promise.all([import('three'),import('three/addons/loaders/GLTFLoader.js'),import('three/addons/controls/OrbitControls.js')]);
      if(cancelled||!host.current)return;
      const container=host.current;
      const renderer=new T.WebGLRenderer({antialias:true,alpha:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));container.appendChild(renderer.domElement);
      renderer.domElement.setAttribute('aria-label',label);renderer.domElement.setAttribute('role','img');
      const scene=new T.Scene();const camera=new T.PerspectiveCamera(40,1,.01,1000);camera.position.set(0,1,4);
      scene.add(new T.HemisphereLight(0xffffff,0x333333,3));const light=new T.DirectionalLight(0xffffff,3);light.position.set(4,6,5);scene.add(light);
      const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=false;
      let model:Three.Object3D|undefined;
      const draw=()=>renderer.render(scene,camera);controls.addEventListener('change',draw);
      const resize=()=>{const width=container.clientWidth,height=container.clientHeight;renderer.setSize(width,height);camera.aspect=width/Math.max(height,1);camera.updateProjectionMatrix();draw();};
      const observer=new ResizeObserver(resize);observer.observe(container);resize();
      dispose=()=>{observer.disconnect();controls.dispose();model?.traverse(o=>{const mesh=o as Three.Mesh;if(mesh.geometry)mesh.geometry.dispose();if(mesh.material)for(const m of Array.isArray(mesh.material)?mesh.material:[mesh.material]){for(const v of Object.values(m))if(v instanceof T.Texture)v.dispose();m.dispose();}});renderer.dispose();renderer.domElement.remove();};
      try{
        const result=await new GLTFLoader().loadAsync(src);
        if(cancelled){result.scene.traverse(o=>{const mesh=o as Three.Mesh;mesh.geometry?.dispose();});return;}
        model=result.scene;const box=new T.Box3().setFromObject(model);const size=box.getSize(new T.Vector3());const center=box.getCenter(new T.Vector3());model.position.sub(center);scene.add(model);
        const distance=Math.max(size.x,size.y,size.z,1)*2.4;camera.position.set(distance*.35,distance*.25,distance);controls.target.set(0,0,0);controls.update();draw();setStatus('Модель загружена');
      }catch{if(!cancelled)setStatus('Не удалось загрузить модель.');}
    })().catch(()=>{if(!cancelled)setStatus('Просмотр 3D недоступен в этом браузере.');});
    return()=>{cancelled=true;dispose();};
  },[src,label]);
  return <figure data-component="model-viewer" style={{margin:'48px auto',maxWidth:1120,color:'#e9dfcf'}}>
    <div ref={host} style={{height:'min(65vh,560px)',minHeight:280,background:poster?`#161414 url("${poster}") center/contain no-repeat`:'#161414'}} />
    <figcaption><strong>{label}</strong><p role="status">{status}</p><span>Повернуть — перетащите мышью или пальцем. Масштаб — колёсико или жест двумя пальцами.</span></figcaption>
  </figure>;
}
