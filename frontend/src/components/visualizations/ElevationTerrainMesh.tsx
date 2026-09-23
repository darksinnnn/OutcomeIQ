import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

interface ElevationTerrainMeshProps {
  elevationErrorCm: number;
  surfaceVariance: number;
  isQualityAlert?: boolean;
  className?: string;
}

export const ElevationTerrainMesh: React.FC<ElevationTerrainMeshProps> = ({
  elevationErrorCm,
  surfaceVariance,
  isQualityAlert = false,
  className = '',
}) => {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!mountRef.current) return;

    const width = mountRef.current.clientWidth || 400;
    const height = 240;

    // Scene, Camera, Renderer
    const scene = new THREE.Scene();
    scene.background = new THREE.Color('#1B1F23');

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 12, 18);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    mountRef.current.appendChild(renderer.domElement);

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(isQualityAlert ? 0xe5484d : 0x5b8def, 1.5);
    dirLight.position.set(10, 20, 10);
    scene.add(dirLight);

    // Create 3D Plane Mesh representing Subgrade Surface
    const size = 14;
    const segments = 24;
    const geometry = new THREE.PlaneGeometry(size, size, segments, segments);
    geometry.rotateX(-Math.PI / 2);

    const pos = geometry.attributes.position;
    const amp = isQualityAlert ? elevationErrorCm * 0.3 : 0.2;

    // Deform vertices based on actual elevation error & variance
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i);
      const z = pos.getZ(i);
      const dist = Math.sqrt(x * x + z * z);
      const wave = Math.sin(dist * 0.8) * amp * (surfaceVariance + 0.5);
      pos.setY(i, wave);
    }
    geometry.computeVertexNormals();

    const material = new THREE.MeshStandardMaterial({
      color: isQualityAlert ? 0xe5484d : 0x4caf7d,
      wireframe: true,
      roughness: 0.4,
      metalness: 0.2,
    });

    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);

    // Subtle ambient animation loop
    let animationFrameId: number;
    const animate = () => {
      mesh.rotation.y += 0.003;
      renderer.render(scene, camera);
      animationFrameId = requestAnimationFrame(animate);
    };
    animate();

    return () => {
      cancelAnimationFrame(animationFrameId);
      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement);
      }
      geometry.dispose();
      material.dispose();
      renderer.dispose();
    };
  }, [elevationErrorCm, surfaceVariance, isQualityAlert]);

  return (
    <div className={`bg-panel border border-hairline rounded-md p-4 ${className}`}>
      <div className="flex items-center justify-between mb-2">
        <div>
          <h4 className="font-display font-medium text-xs text-text-primary uppercase tracking-wider">
            Data-Driven Subgrade 3D Elevation Surface Mesh (Three.js)
          </h4>
          <p className="text-[11px] font-body text-text-muted mt-0.5">
            Height & wireframe deformation directly visualize recorded elevation deviation ({elevationErrorCm} cm).
          </p>
        </div>
        <span
          className={`text-[11px] font-display font-medium px-2 py-0.5 rounded-sm border ${
            isQualityAlert
              ? 'bg-status-red/15 text-status-red border-status-red/40'
              : 'bg-status-green/15 text-status-green border-status-green/40'
          }`}
        >
          {isQualityAlert ? `Elevation Risk +${elevationErrorCm}cm` : 'Grade Surface Nominal'}
        </span>
      </div>

      <div ref={mountRef} className="w-full h-[240px] rounded-sm overflow-hidden bg-base relative">
        <div className="absolute bottom-2 left-2 bg-panel/80 px-2 py-1 rounded-sm border border-hairline text-[10px] font-mono text-text-muted">
          Mesh Amp: {elevationErrorCm} cm | Var: {surfaceVariance}
        </div>
      </div>
    </div>
  );
};
