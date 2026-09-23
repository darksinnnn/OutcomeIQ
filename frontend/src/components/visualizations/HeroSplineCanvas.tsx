import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

export const HeroSplineCanvas: React.FC<{ className?: string }> = ({ className = '' }) => {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!mountRef.current) return;

    const width = mountRef.current.clientWidth || 600;
    const height = 280;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color('#14171A');

    const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 1000);
    camera.position.set(15, 18, 25);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    mountRef.current.appendChild(renderer.domElement);

    // Ambient & Directional Lighting with Cat Amber hue
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const amberLight = new THREE.PointLight(0xf2a93b, 2.5, 50);
    amberLight.position.set(10, 15, 10);
    scene.add(amberLight);

    // Jobsite Terrain Surface Grid
    const gridHelper = new THREE.GridHelper(40, 20, 0xf2a93b, 0x2c3238);
    scene.add(gridHelper);

    // Stylized Excavator / Heavy Machine Geometry Blocks
    const cabGroup = new THREE.Group();

    // Machine Base Chassis
    const chassisGeo = new THREE.BoxGeometry(6, 1.5, 4);
    const chassisMat = new THREE.MeshStandardMaterial({ color: 0x1b1f23, roughness: 0.5 });
    const chassis = new THREE.Mesh(chassisGeo, chassisMat);
    chassis.position.y = 1;
    cabGroup.add(chassis);

    // Machine Cab (Cat Amber Accent)
    const cabGeo = new THREE.BoxGeometry(3, 2.5, 3);
    const cabMat = new THREE.MeshStandardMaterial({ color: 0xf2a93b, roughness: 0.3, metalness: 0.4 });
    const cab = new THREE.Mesh(cabGeo, cabMat);
    cab.position.set(-1, 3, 0);
    cabGroup.add(cab);

    // Boom Arm Representation
    const armGeo = new THREE.BoxGeometry(8, 0.8, 0.8);
    const armMat = new THREE.MeshStandardMaterial({ color: 0x22272c });
    const arm = new THREE.Mesh(armGeo, armMat);
    arm.position.set(4, 3.5, 0);
    arm.rotation.z = -Math.PI / 6;
    cabGroup.add(arm);

    scene.add(cabGroup);

    let animationFrameId: number;
    const animate = () => {
      cabGroup.rotation.y += 0.002;
      renderer.render(scene, camera);
      animationFrameId = requestAnimationFrame(animate);
    };
    animate();

    return () => {
      cancelAnimationFrame(animationFrameId);
      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement);
      }
      chassisGeo.dispose();
      chassisMat.dispose();
      cabGeo.dispose();
      cabMat.dispose();
      armGeo.dispose();
      armMat.dispose();
      renderer.dispose();
    };
  }, []);

  return (
    <div className={`relative rounded-md overflow-hidden border border-hairline bg-panel ${className}`}>
      <div ref={mountRef} className="w-full h-[280px]" />
      <div className="absolute top-4 left-4 pointer-events-none">
        <span className="text-[10px] font-display uppercase tracking-widest px-2 py-0.5 rounded-sm bg-accent/20 text-accent border border-accent/40">
          Jobsite Command Center
        </span>
        <h3 className="font-display text-xl font-bold text-text-primary mt-1">
          Connected Fleet Operational Baseline
        </h3>
      </div>
    </div>
  );
};
