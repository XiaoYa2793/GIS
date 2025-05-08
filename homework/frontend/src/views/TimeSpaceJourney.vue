<template>
  <div class="time-space-journey">
    <div class="journey-container" ref="journeyContainer">
      <!-- 3D场景容器 - 现在占据更多空间 -->
      <div class="scene-container" ref="sceneContainer">
        <div class="loading-overlay" v-if="loading">
          <div class="loading-spinner"></div>
          <div class="loading-text">加载中...</div>
        </div>
      </div>
      
      <!-- 紧凑型侧边控制面板 -->
      <div class="side-control-panel" :class="{ hidden: !isPanelVisible }">
        <div class="panel-header">
          <h3>时空导航</h3>
          <button class="close-panel-btn" @click="togglePanel">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="panel-scroll-content">
          <div class="side-panel-section">
            <div class="time-navigation">
              <button class="nav-btn" @click="() => selectMap(Math.max(currentMapIndex - 1, 0))">
                <i class="fas fa-chevron-left"></i>
              </button>
              <div class="current-time">
                <div class="time-name">{{ currentMap?.name || '' }}</div>
                <div class="time-year">{{ currentMap?.year_range || '' }}</div>
              </div>
              <button class="nav-btn" @click="() => selectMap(Math.min(currentMapIndex + 1, maps.length - 1))">
                <i class="fas fa-chevron-right"></i>
              </button>
            </div>
          </div>
          
          <div class="side-panel-section">
            <h3>视图模式</h3>
            <div class="view-buttons">
              <button class="view-btn" :class="{ active: viewMode === '3d' }" @click="setViewMode('3d')">
                <i class="fas fa-cube"></i> 3D
              </button>
              <button class="view-btn" :class="{ active: viewMode === '2d' }" @click="setViewMode('2d')">
                <i class="fas fa-map"></i> 2D
              </button>
              <button class="view-btn" :class="{ active: viewMode === 'compare' }" @click="setViewMode('compare')">
                <i class="fas fa-clone"></i> 对比
              </button>
            </div>
          </div>
          
          <div class="side-panel-section">
            <h3>地图控制</h3>
            <div class="control-grid">
              <button class="ctrl-btn" @click="rotateLeft">
                <i class="fas fa-undo"></i> 左转
              </button>
              <button class="ctrl-btn" @click="zoomIn">
                <i class="fas fa-search-plus"></i> 放大
              </button>
              <button class="ctrl-btn" @click="rotateRight">
                <i class="fas fa-redo"></i> 右转
              </button>
              <button class="ctrl-btn" @click="zoomOut">
                <i class="fas fa-search-minus"></i> 缩小
              </button>
            </div>
          </div>
          
          <div class="map-info">
            <h3>地图信息</h3>
            <p>{{ currentMap?.description || '' }}</p>
          </div>
        </div>
      </div>
      
      <!-- 时间线浮动指示器 -->
      <div class="floating-timeline">
        <div 
          v-for="(map, index) in maps" 
          :key="map.id"
          class="timeline-dot"
          :class="{ active: currentMapIndex === index }"
          @click="selectMap(index)"
        >
          <div class="dot-tooltip">{{ map.name }}</div>
        </div>
        <div class="timeline-progress" :style="{ width: `${timelineProgress}%` }"></div>
      </div>
      
      <!-- 返回按钮 -->
      <div class="back-button" @click="goBack">
        <i class="fas fa-arrow-left"></i> 返回
      </div>
      
      <div class="toggle-panel-btn" @click="togglePanel" v-if="!isPanelVisible">
        <i class="fas fa-chevron-left"></i>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

const router = useRouter();
const loading = ref(true);
const maps = ref([]);
const currentMapIndex = ref(0);
const viewMode = ref('3d');
const isPanelVisible = ref(true);

const journeyContainer = ref(null);
const sceneContainer = ref(null);

// Three.js 变量
let scene, camera, renderer, controls;
let mapTextures = [];
let currentMapMesh;
let compareMesh;

// 计算当前地图
const currentMap = computed(() => {
  return maps.value[currentMapIndex.value] || null;
});

// 计算时间线进度
const timelineProgress = computed(() => {
  if (maps.value.length <= 1) return 100;
  return (currentMapIndex.value / (maps.value.length - 1)) * 100;
});

// 初始化3D场景
const initScene = () => {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0a192f);
  
  camera = new THREE.PerspectiveCamera(
    60, 
    sceneContainer.value.clientWidth / sceneContainer.value.clientHeight, 
    0.1, 
    1000
  );
  camera.position.z = 5;
  
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(sceneContainer.value.clientWidth, sceneContainer.value.clientHeight);
  renderer.setPixelRatio(window.devicePixelRatio);
  sceneContainer.value.appendChild(renderer.domElement);
  
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.rotateSpeed = 0.5;
  
  // 添加环境光
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
  scene.add(ambientLight);
  
  // 添加方向光
  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
  directionalLight.position.set(1, 1, 1);
  scene.add(directionalLight);
  
  // 响应窗口大小变化
  window.addEventListener('resize', onWindowResize);
  
  animate();
};

// 加载地图纹理
const loadMapTextures = async () => {
  loading.value = true;
  
  try {
    for (const map of maps.value) {
      const textureLoader = new THREE.TextureLoader();
      const texture = await new Promise((resolve, reject) => {
        textureLoader.load(
          map.image_path.startsWith('http') ? map.image_path : `http://localhost:5000${map.image_path}`,
          (texture) => resolve(texture),
          undefined,
          (error) => reject(error)
        );
      });
      
      mapTextures.push(texture);
    }
    
    createMapMesh();
    loading.value = false;
  } catch (error) {
    console.error('加载地图纹理失败:', error);
    loading.value = false;
  }
};

// 创建地图网格
const createMapMesh = () => {
  if (mapTextures.length === 0 || currentMapIndex.value >= mapTextures.length) return;
  
  if (currentMapMesh) {
    scene.remove(currentMapMesh);
  }
  
  const geometry = new THREE.PlaneGeometry(10, 7);
  const material = new THREE.MeshStandardMaterial({
    map: mapTextures[currentMapIndex.value],
    side: THREE.DoubleSide
  });
  
  currentMapMesh = new THREE.Mesh(geometry, material);
  scene.add(currentMapMesh);
  
  if (viewMode.value === '3d') {
    // 添加些微弯曲效果，增强3D感
    currentMapMesh.geometry = new THREE.BoxGeometry(10, 7, 0.2);
    currentMapMesh.material = [
      new THREE.MeshStandardMaterial({ color: 0x777777 }), // 右
      new THREE.MeshStandardMaterial({ color: 0x777777 }), // 左
      new THREE.MeshStandardMaterial({ color: 0x777777 }), // 上
      new THREE.MeshStandardMaterial({ color: 0x777777 }), // 下
      new THREE.MeshStandardMaterial({ map: mapTextures[currentMapIndex.value] }), // 前
      new THREE.MeshStandardMaterial({ color: 0x555555 }) // 后
    ];
    
    // 添加初始旋转
    currentMapMesh.rotation.x = -0.1;
    currentMapMesh.rotation.y = 0.1;
  }
  
  // 确保地图居中
  currentMapMesh.position.set(0, 0, 0);
  
  // 调整地图大小以适应屏幕
  const aspectRatio = sceneContainer.value.clientWidth / sceneContainer.value.clientHeight;
  if (aspectRatio > 10/7) { // 如果屏幕更宽
    currentMapMesh.scale.set(aspectRatio/(10/7), 1, 1);
  } else { // 如果屏幕更高
    currentMapMesh.scale.set(1, (10/7)/aspectRatio, 1);
  }
  
  updateViewMode();
};

// 更新视图模式
const updateViewMode = () => {
  if (!currentMapMesh) return;
  
  if (viewMode.value === '2d') {
    // 2D模式
    camera.position.set(0, 0, 5);
    controls.enableRotate = false;
    currentMapMesh.rotation.set(0, 0, 0);
  } else if (viewMode.value === '3d') {
    // 3D模式
    camera.position.set(0, 0, 5);
    controls.enableRotate = true;
    currentMapMesh.rotation.x = -0.1;
    currentMapMesh.rotation.y = 0.1;
  } else if (viewMode.value === 'compare') {
    // 对比模式
    setupCompareMode();
  }
  
  controls.update();
};

// 设置对比模式
const setupCompareMode = () => {
  if (compareMesh) {
    scene.remove(compareMesh);
    compareMesh = null;
  }
  
  // 如果只有一张地图，无法比较
  if (maps.value.length <= 1) return;
  
  // 找到下一张地图进行对比
  const nextIndex = (currentMapIndex.value + 1) % maps.value.length;
  
  const geometry = new THREE.PlaneGeometry(10, 7);
  const material = new THREE.MeshStandardMaterial({
    map: mapTextures[nextIndex],
    side: THREE.DoubleSide,
    transparent: true,
    opacity: 0.5
  });
  
  compareMesh = new THREE.Mesh(geometry, material);
  compareMesh.position.z = 0.1; // 略微在当前地图上方
  scene.add(compareMesh);
  
  // 调整相机位置以便更好地观察对比
  camera.position.set(0, 0, 6);
  controls.update();
};

// 动画循环
const animate = () => {
  requestAnimationFrame(animate);
  
  if (controls) {
    controls.update();
  }
  
  if (renderer && scene && camera) {
    renderer.render(scene, camera);
  }
};

// 窗口大小变化处理
const onWindowResize = () => {
  if (!camera || !renderer || !sceneContainer.value) return;
  
  // 获取容器的实际尺寸
  const width = sceneContainer.value.clientWidth;
  const height = sceneContainer.value.clientHeight;
  
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);
};

// 选择地图
const selectMap = (index) => {
  if (index < 0 || index >= maps.value.length) return;
  
  currentMapIndex.value = index;
  createMapMesh();
};

// 旋转控制
const rotateLeft = () => {
  if (!currentMapMesh) return;
  currentMapMesh.rotation.y -= 0.1;
};

const rotateRight = () => {
  if (!currentMapMesh) return;
  currentMapMesh.rotation.y += 0.1;
};

// 缩放控制
const zoomIn = () => {
  if (!camera) return;
  camera.position.z = Math.max(camera.position.z - 0.5, 2);
};

const zoomOut = () => {
  if (!camera) return;
  camera.position.z = Math.min(camera.position.z + 0.5, 10);
};

// 设置视图模式
const setViewMode = (mode) => {
  viewMode.value = mode;
  updateViewMode();
};

// 返回上一页
const goBack = () => {
  router.push('/');
};

// 从服务器获取历史地图数据
const fetchMaps = async () => {
  try {
    loading.value = true;
    const response = await axios.get('http://localhost:5000/api/historical-maps');
    
    if (response.data && response.data.status === 'success') {
      maps.value = response.data.data;
      loading.value = false;
      
      // 地图数据加载完成后，加载纹理
      await loadMapTextures();
    } else {
      console.error('获取历史地图数据失败:', response.data);
      loading.value = false;
    }
  } catch (error) {
    console.error('获取历史地图数据时出错:', error);
    loading.value = false;
  }
};

const togglePanel = () => {
  isPanelVisible.value = !isPanelVisible.value;
};

onMounted(async () => {
  await fetchMaps();
  initScene();
  
  // 确保初始尺寸正确
  setTimeout(() => {
    if (renderer && sceneContainer.value) {
      renderer.setSize(sceneContainer.value.clientWidth, sceneContainer.value.clientHeight);
      camera.aspect = sceneContainer.value.clientWidth / sceneContainer.value.clientHeight;
      camera.updateProjectionMatrix();
    }
  }, 100);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', onWindowResize);
  
  // 清理Three.js资源
  if (renderer) {
    renderer.dispose();
    sceneContainer.value.removeChild(renderer.domElement);
  }
  
  if (controls) {
    controls.dispose();
  }
  
  // 清理几何体和材质
  if (currentMapMesh) {
    currentMapMesh.geometry.dispose();
    if (Array.isArray(currentMapMesh.material)) {
      currentMapMesh.material.forEach(material => material.dispose());
    } else {
      currentMapMesh.material.dispose();
    }
  }
  
  if (compareMesh) {
    compareMesh.geometry.dispose();
    compareMesh.material.dispose();
  }
  
  mapTextures.forEach(texture => texture.dispose());
});
</script>

<style scoped>
.time-space-journey {
  width: 700px;
  height: 100vh;
  overflow: hidden;
  background: linear-gradient(135deg, #0f172a, #1e293b);
  color: white;
  position: relative;
  font-family: 'Roboto', 'Microsoft YaHei', sans-serif;
}

.journey-container {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
}

.scene-container {
  flex: 1;
  height: 100%;
  position: relative;
  width: calc(100% - 300px); /* 地图区域更宽 */
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(15, 23, 42, 0.9);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 100;
  backdrop-filter: blur(10px);
}

.loading-spinner {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: 4px solid rgba(99, 102, 241, 0.1);
  border-left-color: #6366f1;
  border-top-color: #8b5cf6;
  animation: spin 1.2s cubic-bezier(0.34, 0.69, 0.1, 1) infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  margin-top: 24px;
  font-size: 18px;
  font-weight: 500;
  color: white;
  background: linear-gradient(90deg, #6366f1, #8b5cf6);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  letter-spacing: 0.5px;
}

/* 新的紧凑型侧边面板 */
.side-control-panel {
  width: 300px;
  height: 100%;
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  background: rgba(15, 23, 42, 0.9);
  box-shadow: -5px 0 15px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease;
  border-left: 1px solid rgba(99, 102, 241, 0.2);
}

.side-control-panel.hidden {
  transform: translateX(100%);
}

.panel-header {
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(99, 102, 241, 0.2);
}

.panel-header h3 {
  margin: 0;
  font-size: 1.3rem;
  color: white;
  background: linear-gradient(90deg, #6366f1, #8b5cf6);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.close-panel-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.close-panel-btn:hover {
  color: white;
  transform: scale(1.1);
}

.panel-scroll-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.side-panel-section {
  padding: 16px;
  background: rgba(30, 41, 59, 0.6);
  border-radius: 12px;
  margin-bottom: 16px;
  border: 1px solid rgba(99, 102, 241, 0.2);
  transition: all 0.3s ease;
}

.side-panel-section h3 {
  color: white;
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 1.1rem;
  font-weight: 600;
  text-align: center;
}

.time-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.current-time {
  flex: 1;
  text-align: center;
  padding: 12px;
  background: rgba(30, 41, 59, 0.8);
  border-radius: 10px;
  border: 1px solid rgba(99, 102, 241, 0.2);
}

.time-name {
  font-size: 1.1rem;
  font-weight: bold;
  color: white;
  margin-bottom: 4px;
}

.time-year {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
}

.nav-btn {
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(99, 102, 241, 0.3);
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.nav-btn:hover {
  background: rgba(99, 102, 241, 0.3);
  transform: scale(1.05);
}

.view-buttons {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.view-btn {
  padding: 10px;
  border-radius: 8px;
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(99, 102, 241, 0.2);
  color: white;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.view-btn:hover {
  background: rgba(99, 102, 241, 0.2);
}

.view-btn.active {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-color: transparent;
}

.control-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.ctrl-btn {
  padding: 10px;
  border-radius: 8px;
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(99, 102, 241, 0.2);
  color: white;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.ctrl-btn:hover {
  background: rgba(99, 102, 241, 0.2);
}

.map-info {
  padding: 12px;
  background: rgba(30, 41, 59, 0.6);
  border-radius: 10px;
  border: 1px solid rgba(99, 102, 241, 0.2);
}

.map-info h3 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 1.1rem;
}

.map-info p {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.8);
}

/* 时间线样式 */
.floating-timeline {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(15, 23, 42, 0.9);
  border-radius: 20px;
  padding: 12px 20px;
  display: flex;
  gap: 20px;
  z-index: 10;
  backdrop-filter: blur(10px);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
}

.timeline-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  cursor: pointer;
  position: relative;
  transition: all 0.2s ease;
}

.timeline-dot:hover {
  transform: scale(1.2);
  background: rgba(99, 102, 241, 0.5);
}

.timeline-dot.active {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  transform: scale(1.2);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.3);
}

.dot-tooltip {
  position: absolute;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(15, 23, 42, 0.95);
  padding: 6px 12px;
  border-radius: 6px;
  white-space: nowrap;
  font-size: 0.8rem;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s ease;
}

.timeline-dot:hover .dot-tooltip {
  opacity: 1;
  visibility: visible;
  bottom: 25px;
}

.timeline-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 2px;
  background: linear-gradient(90deg, #6366f1, #8b5cf6);
  transition: width 0.4s ease;
}

/* 返回按钮 */
.back-button {
  position: absolute;
  top: 20px;
  left: 20px;
  background: rgba(15, 23, 42, 0.9);
  color: white;
  padding: 10px 16px;
  border-radius: 20px;
  cursor: pointer;
  z-index: 15;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  backdrop-filter: blur(5px);
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.back-button:hover {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  transform: translateY(-2px);
}

/* 面板切换按钮 */
.toggle-panel-btn {
  position: absolute;
  top: 50%;
  right: 0;
  transform: translateY(-50%);
  width: 30px;
  height: 60px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 15px 0 0 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 5;
  box-shadow: -2px 0 10px rgba(0, 0, 0, 0.2);
  transition: all 0.2s ease;
}

.toggle-panel-btn:hover {
  width: 35px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .scene-container {
    width: 100%;
  }
  
  .side-control-panel {
    position: absolute;
    right: 0;
    width: 280px;
    height: 100%;
    transform: translateX(100%);
  }
  
  .side-control-panel.hidden {
    transform: translateX(100%);
  }
  
  .toggle-panel-btn {
    display: flex;
  }
  
  .floating-timeline {
    bottom: 15px;
    padding: 10px 15px;
    gap: 15px;
  }
  
  .timeline-dot {
    width: 14px;
    height: 14px;
  }
}
</style>