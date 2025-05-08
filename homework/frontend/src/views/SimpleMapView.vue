<template>
  <div class="simple-map-view">
    <h1>简化版历史地图</h1>
    <p>这是一个简化版的北京历史地图展示，点击下方按钮查看高级版本</p>
    
    <button class="advanced-btn" @click="goToAdvancedView">
      <i class="fas fa-map-marked-alt"></i> 查看高级版本
    </button>
    
    <div v-if="loading" class="loading">
      <p>加载中...</p>
    </div>
    
    <div v-else-if="error" class="error">
      <h2>加载失败</h2>
      <p>{{ error }}</p>
      <button @click="fetchData" class="retry-btn">重试</button>
    </div>
    
    <div v-else class="timeline-container">
      <h2>历史地图时间轴</h2>
      
      <div v-if="maps.length === 0" class="no-data">没有找到历史地图数据</div>
      
      <div v-else class="timeline-view">
        <!-- 时间轴导航 -->
        <div class="timeline-nav">
          <div class="timeline-ruler">
            <div class="timeline-line"></div>
            <div 
              v-for="(map, index) in maps" 
              :key="map.id"
              class="timeline-marker"
              :class="{ active: selectedMapIndex === index }"
              @click="selectMap(index)"
              :style="{ left: `${(index / (maps.length - 1)) * 100}%` }"
            >
              <div class="marker-dot"></div>
              <div class="marker-label">{{ map.year || '未知年份' }}</div>
              <div class="marker-dynasty">{{ map.period }}</div>
            </div>
          </div>
          
          <div class="timeline-controls">
            <button 
              class="nav-btn prev" 
              @click="prevMap" 
              :disabled="selectedMapIndex === 0"
            >
              &#9664; 上一个
            </button>
            
            <button 
              class="play-btn" 
              @click="togglePlayMode"
            >
              {{ isPlaying ? '暂停' : '播放' }}
            </button>
            
            <button 
              class="nav-btn next" 
              @click="nextMap" 
              :disabled="selectedMapIndex === maps.length - 1"
            >
              下一个 &#9654;
            </button>
          </div>
        </div>
        
        <!-- 3D地图展示区域 -->
        <div class="map-display">
          <!-- Three.js 3D画布容器 -->
          <div id="three-container" ref="threeContainer" class="three-container"></div>
          
          <transition name="fade" mode="out-in">
            <div class="map-content" :key="selectedMapIndex">
              <div class="map-header">
                <h3>{{ currentMap?.name }}</h3>
                <p class="map-period">{{ currentMap?.period }} ({{ currentMap?.year_range }})</p>
              </div>
              
              <div class="map-image-container">
                <canvas v-if="showThreeJS" class="three-overlay"></canvas>
                <img 
                  :src="getImageUrl(currentMap?.image_path)" 
                  :alt="currentMap?.name"
                  @error="handleImageError($event, currentMap)"
                  ref="mapImage"
                  @load="handleImageLoad"
                >
                <!-- 3D控制按钮 -->
                <div class="three-controls">
                  <button class="three-btn" @click="toggle3DMode">
                    {{ showThreeJS ? '2D模式' : '3D模式' }}
                  </button>
                  <div v-if="showThreeJS" class="effect-controls">
                    <button @click="rotateModel('left')" class="effect-btn">↶ 左旋转</button>
                    <button @click="rotateModel('reset')" class="effect-btn">重置</button>
                    <button @click="rotateModel('right')" class="effect-btn">右旋转 ↷</button>
                  </div>
                </div>
                
                <!-- 3D效果指示器 -->
                <div v-if="showThreeJS" class="three-indicator">
                  <div class="indicator-dot"></div>
                  3D效果已启用
                </div>
              </div>
              
              <div class="map-description">
                <p>{{ currentMap?.description }}</p>
              </div>
            </div>
          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onBeforeUnmount, watch, nextTick } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import gsap from 'gsap';

const router = useRouter();
const maps = ref([]);
const loading = ref(true);
const error = ref(null);
const selectedMapIndex = ref(0);
const isPlaying = ref(false);
const playInterval = ref(null);

// Three.js相关变量
const threeContainer = ref(null);
const mapImage = ref(null);
const showThreeJS = ref(false);
let camera = null;
let scene = null;
let renderer = null;
let controls = null;
let mapMesh = null;
const mapTexture = ref(null);
let animationFrameId = null;

// 获取当前选中的地图数据
const currentMap = computed(() => {
  if (maps.value.length === 0 || selectedMapIndex.value < 0) return null;
  return maps.value[selectedMapIndex.value] || null;
});

// 跳转到高级版本地图
const goToAdvancedView = () => {
  router.push('/historical-maps');
};

// 选择地图
const selectMap = (index) => {
  selectedMapIndex.value = index;
  if (isPlaying.value) {
    stopPlayMode();
    startPlayMode();
  }
  
  if (showThreeJS.value) {
    nextTick(() => {
      if (mapImage.value) {
        setTimeout(() => {
          updateMapTexture();
        }, 300);
      }
    });
  }
};

// 上一个地图
const prevMap = () => {
  if (selectedMapIndex.value > 0) {
    selectedMapIndex.value--;
  }
};

// 下一个地图
const nextMap = () => {
  if (selectedMapIndex.value < maps.value.length - 1) {
    selectedMapIndex.value++;
  } else if (isPlaying.value) {
    stopPlayMode();
  }
};

// 切换播放模式
const togglePlayMode = () => {
  if (isPlaying.value) {
    stopPlayMode();
  } else {
    startPlayMode();
  }
};

// 开始自动播放
const startPlayMode = () => {
  if (playInterval.value) clearInterval(playInterval.value);
  isPlaying.value = true;
  playInterval.value = setInterval(() => {
    if (selectedMapIndex.value < maps.value.length - 1) {
      selectedMapIndex.value++;
    } else {
      selectedMapIndex.value = 0;
    }
  }, 3000);
};

// 停止自动播放
const stopPlayMode = () => {
  isPlaying.value = false;
  if (playInterval.value) {
    clearInterval(playInterval.value);
    playInterval.value = null;
  }
};

const getImageUrl = (imagePath) => {
  if (!imagePath) return null;
  
  if (imagePath.match(/^https?:\/\//)) {
    return imagePath;
  }
  
  return `http://localhost:5000${imagePath}`;
};

const handleImageError = (event, map) => {
  if (!map) return;
  event.target.src = `https://via.placeholder.com/800x600?text=${encodeURIComponent(map.name)}`;
};

const handleImageLoad = () => {
  if (showThreeJS.value) {
    updateMapTexture();
  }
};

// 切换3D模式
const toggle3DMode = () => {
  showThreeJS.value = !showThreeJS.value;
  
  if (showThreeJS.value) {
    nextTick(() => {
      if (!scene) {
        initThreeJS();
      } else {
        updateMapTexture();
        
        // 确保容器可见并启用交互
        if (threeContainer.value) {
          threeContainer.value.style.opacity = '1';
          threeContainer.value.style.pointerEvents = 'auto';
        }
      }
    });
  } else {
    // 禁用3D容器的交互
    if (threeContainer.value) {
      threeContainer.value.style.opacity = '0';
      threeContainer.value.style.pointerEvents = 'none';
    }
  }
};

// 旋转模型
const rotateModel = (direction) => {
  console.log(`正在执行 ${direction} 旋转...`, mapMesh);
  
  if (!mapMesh || !scene) {
    console.error("地图模型未加载，无法旋转");
    return;
  }
  
  if (direction === 'left') {
    gsap.to(mapMesh.rotation, {
      y: mapMesh.rotation.y + Math.PI / 4,
      duration: 0.5,
      ease: "power2.out",
      onStart: () => console.log("开始左旋转"),
      onComplete: () => console.log("完成左旋转", mapMesh.rotation.y)
    });
  } else if (direction === 'right') {
    gsap.to(mapMesh.rotation, {
      y: mapMesh.rotation.y - Math.PI / 4,
      duration: 0.5,
      ease: "power2.out",
      onStart: () => console.log("开始右旋转"),
      onComplete: () => console.log("完成右旋转", mapMesh.rotation.y)
    });
  } else if (direction === 'reset') {
    // 重置旋转状态
    gsap.to(mapMesh.rotation, {
      x: -Math.PI / 15,
      y: 0,
      z: 0,
      duration: 0.7,
      ease: "elastic.out(1, 0.5)",
      onStart: () => console.log("开始重置旋转"),
      onComplete: () => console.log("完成重置旋转")
    });
    
    // 重置相机位置
    if (controls && camera) {
      gsap.to(camera.position, {
        x: 0,
        y: 0.5,
        z: 3,
        duration: 0.7,
        onUpdate: () => {
          if (controls) controls.update();
        },
        onComplete: () => {
          if (controls) {
            controls.target.set(0, 0, 0);
            controls.update();
          }
        }
      });
    }
  }
};

// 创建地图平面
const createMapPlane = () => {
  if (!scene || !currentMap.value) {
    console.error("场景或当前地图数据不存在，无法创建地图平面");
    return;
  }

  console.log("开始创建地图平面...");

  // 清理之前的地图网格
  if (mapMesh) {
    console.log("清理旧地图网格...");
    scene.remove(mapMesh);
    if (mapMesh.material) {
      if (Array.isArray(mapMesh.material)) {
        mapMesh.material.forEach(mat => mat.dispose());
      } else {
        mapMesh.material.dispose();
      }
    }
    if (mapMesh.geometry) mapMesh.geometry.dispose();
  }

  const textureLoader = new THREE.TextureLoader();
  const imagePath = getImageUrl(currentMap.value.image_path);
  console.log("加载地图纹理:", imagePath);

  textureLoader.load(imagePath, (texture) => {
    console.log("纹理加载成功");
    texture.anisotropy = renderer.capabilities.getMaxAnisotropy();
    texture.encoding = THREE.sRGBEncoding;
    texture.needsUpdate = true;

    const frontMaterial = new THREE.MeshStandardMaterial({
      map: texture,
      roughness: 0.7,
      metalness: 0.1,
      color: 0xfffaf0,
      side: THREE.FrontSide
    });

    const edgeMaterial = new THREE.MeshStandardMaterial({
      color: 0xe2d9c5,
      roughness: 0.9,
      metalness: 0.0,
      side: THREE.FrontSide
    });

    const backMaterial = new THREE.MeshStandardMaterial({
      color: 0xd9c7a9,
      roughness: 0.85,
      metalness: 0.05,
      side: THREE.BackSide
    });

    const mapAspect = texture.image.width / texture.image.height;
    const mapWidth = 2.0;
    const mapHeight = mapWidth / mapAspect;
    const mapDepth = 0.05;

    const geometry = new THREE.BoxGeometry(mapWidth, mapHeight, mapDepth, 100, 100, 1);

    const positionAttribute = geometry.getAttribute('position');
    const vertex = new THREE.Vector3();

    for (let i = 0; i < positionAttribute.count; i++) {
      vertex.fromBufferAttribute(positionAttribute, i);

      // 只对前后贴图面进行变形（Z 接近正负 mapDepth/2）
      if (Math.abs(vertex.z) >= mapDepth / 2 * 0.99) {
        const centerDist = Math.sqrt(vertex.x ** 2 + vertex.y ** 2);

        // 中心鼓起 + 噪声扰动
        const bulge = Math.exp(-(centerDist ** 2) / 0.5) * 0.02;
        const noise = (Math.sin(vertex.x * 20) + Math.sin(vertex.y * 20)) * 0.005;
        vertex.z += vertex.z > 0 ? bulge + noise : -(bulge + noise); // 区分前后面方向
      }

      positionAttribute.setXYZ(i, vertex.x, vertex.y, vertex.z);
    }

    geometry.computeVertexNormals();

    mapMesh = new THREE.Mesh(geometry, [
      edgeMaterial, edgeMaterial,
      edgeMaterial, edgeMaterial,
      frontMaterial, backMaterial
    ]);

    scene.add(mapMesh);
    mapMesh.rotation.x = -Math.PI / 15;

    // 动画
    gsap.from(mapMesh.position, {
      y: -0.5,
      duration: 1,
      ease: "back.out(1.7)"
    });

    gsap.from(mapMesh.rotation, {
      x: -Math.PI / 2,
      duration: 1.2,
      ease: "power2.out"
    });

    gsap.from(mapMesh.scale, {
      x: 0.8,
      y: 0.8,
      z: 0.8,
      duration: 1,
      ease: "elastic.out(1, 0.3)"
    });

    if (controls) controls.update();
  },
  (progress) => {
    console.log(`纹理加载进度: ${Math.round(progress.loaded / progress.total * 100)}%`);
  },
  (error) => {
    console.error("加载地图纹理错误:", error);
    createDefaultMap();
  });
};


// 创建默认地图（纹理加载失败时使用）
const createDefaultMap = () => {
  if (!scene) return;
  
  console.log("创建默认地图...");
  
  const defaultMaterial = new THREE.MeshStandardMaterial({
    color: 0xcccccc,
    roughness: 0.8,
    metalness: 0.1,
    side: THREE.DoubleSide
  });
  
  const geometry = new THREE.PlaneGeometry(2, 1.5, 20, 20);
  mapMesh = new THREE.Mesh(geometry, defaultMaterial);
  scene.add(mapMesh);
  mapMesh.rotation.x = -Math.PI / 15;
  
  if (controls) controls.update();
};

// 初始化Three.js场景
const initThreeJS = () => {
  console.log("初始化Three.js场景...");

  // 创建场景
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x101820);

  // 创建相机
  camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.set(0, 0.5, 3);

  // 创建渲染器
  renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true,
    powerPreference: 'high-performance'
  });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.outputEncoding = THREE.sRGBEncoding;

  const container = threeContainer.value;
  if (!container) {
    console.error("未找到Three.js容器元素");
    return;
  }

  container.innerHTML = ''; // 清除容器
  container.appendChild(renderer.domElement);

  // 创建控制器
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.1;
  controls.rotateSpeed = 0.8;
  controls.zoomSpeed = 0.8;
  controls.minDistance = 1.5;
  controls.maxDistance = 6;
  controls.minPolarAngle = Math.PI / 6;
  controls.maxPolarAngle = Math.PI * 0.6;

  // 添加光源
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
  scene.add(ambientLight);

  const mainLight = new THREE.DirectionalLight(0xfdfbd3, 0.9);
  mainLight.position.set(2, 3, 3);
  mainLight.castShadow = true;
  scene.add(mainLight);

  const fillLight = new THREE.PointLight(0xcceeff, 0.6);
  fillLight.position.set(-3, 1, 2);
  scene.add(fillLight);

  const bottomLight = new THREE.PointLight(0xe1c699, 0.4);
  bottomLight.position.set(0, -2, 1);
  scene.add(bottomLight);

  // 添加地面
  const groundGeometry = new THREE.PlaneGeometry(12, 12);
  const groundMaterial = new THREE.MeshStandardMaterial({
    color: 0x333333,
    roughness: 0.8,
    metalness: 0.2,
    transparent: true,
    opacity: 0.6
  });
  const ground = new THREE.Mesh(groundGeometry, groundMaterial);
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -1.2;
  ground.receiveShadow = true;
  scene.add(ground);

  // 添加环境效果
  scene.fog = new THREE.FogExp2(0x101820, 0.08);

  // 确保容器可见
  threeContainer.value.style.opacity = '1';
  threeContainer.value.style.pointerEvents = 'auto';

  resizeHandler();
  window.addEventListener('resize', resizeHandler);

  createMapPlane();
  startAnimation (); // Starts the animation loop

  console.log("Three.js场景初始化完成");
};

// 动画循环
const startAnimation = () => {
  animationFrameId = requestAnimationFrame(startAnimation);

  const cam = camera;
  const scn = scene;
  const rdr = renderer;
  const ctrls = controls;

  if (!rdr || !scn || !cam) return;

  if (ctrls) ctrls.update();

  rdr.render(scn, cam);
};


// 窗口大小调整
function resizeHandler() {
  const width = window.innerWidth;
  const height = window.innerHeight;

  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);
}


// 更新尺寸
const updateSizes = () => {
  if (!camera|| !renderer || !threeContainer.value) return;
  
  camera.aspect = threeContainer.value.clientWidth / threeContainer.value.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(threeContainer.value.clientWidth, threeContainer.value.clientHeight);
};

// 更新地图纹理
const updateMapTexture = () => {
  if (!mapImage || !scene || !mapMesh) {
    console.warn("更新纹理失败: 缺少必要元素", {
      mapImage: !!mapImage,
      scene: !!scene,
      mapMesh: !!mapMesh
    });
    return;
  }
  
  try {
    console.log("更新地图纹理...");
    
    const texture = new THREE.Texture(mapImage);
    texture.needsUpdate = true;
    
    if (Array.isArray(mapMesh.material)) {
      console.log("更新材质数组的纹理");
      mapMesh.material[4].map = texture;
      mapMesh.material[4].needsUpdate = true;
    } else {
      console.log("更新单个材质的纹理");
      mapMesh.material.map = texture;
      mapMesh.material.needsUpdate = true;
    }
    
    console.log("纹理更新完成");
  } catch (err) {
    console.error('更新3D地图纹理出错:', err);
  }
};

// 动画循环
const animate = () => {
  animationFrameId = requestAnimationFrame(animate);

  const mesh = mapMesh;
  const cam = camera;
  const scn = scene;
  const rdr = renderer;
  const ctrls = controls;

  if (mesh) {
    const time = Date.now() * 0.001;
    mesh.position.y = Math.sin(time) * 0.03;
  }

  if (ctrls) ctrls.update();
  if (rdr && scn && cam) rdr.render(scn, cam);
};

const fetchData = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    await axios.get('http://localhost:5000/api/init-historical-maps');
    const response = await axios.get('http://localhost:5000/api/historical-maps');
    
    if (response.data && response.data.status === 'success') {
      maps.value = response.data.data || [];
      maps.value.sort((a, b) => {
        const yearA = parseInt(a.year) || 0;
        const yearB = parseInt(b.year) || 0;
        return yearA - yearB;
      });
      selectedMapIndex.value = 0;
    } else {
      throw new Error('获取数据失败: ' + JSON.stringify(response.data));
    }
  } catch (err) {
    console.error('获取历史地图数据出错:', err);
    error.value = `获取数据失败: ${err.message}`;
  } finally {
    loading.value = false;
  }
};

watch(selectedMapIndex, () => {
  if (showThreeJS.value) {
    nextTick(() => {
      if (mapImage.value) {
        setTimeout(() => {
          updateMapTexture();
        }, 300);
      }
    });
  }
});

onBeforeUnmount(() => {
  stopPlayMode();
  
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
  }
  
  if (renderer) {
    renderer.dispose();
  }

  if (controls) {
    controls.dispose();
  }
  
  window.removeEventListener('resize', updateSizes);
});

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
/* 样式部分保持不变 */
.simple-map-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  color: white;
}

h1 {
  text-align: center;
  margin-bottom: 1rem;
  color: #42b983;
}

.advanced-btn {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  margin: 20px auto;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s ease;
  display: block;
}

.advanced-btn:hover {
  background-color: #3aa876;
  box-shadow: 0 0 10px rgba(66, 185, 131, 0.5);
}

.advanced-btn i {
  margin-right: 8px;
}

.loading, .error {
  text-align: center;
  padding: 3rem;
  background: rgba(26, 31, 44, 0.7);
  border-radius: 10px;
}

.error h2 {
  color: #f56c6c;
}

.retry-btn {
  margin-top: 1rem;
  padding: 0.6rem 1.5rem;
  background: #f56c6c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.retry-btn:hover {
  background: #e64242;
}

.timeline-container {
  margin-top: 2rem;
}

.timeline-container h2 {
  margin-bottom: 1.5rem;
  text-align: center;
}

.no-data {
  text-align: center;
  padding: 2rem;
  background: rgba(26, 31, 44, 0.7);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.7);
}

.timeline-view {
  background: rgba(26, 31, 44, 0.7);
  border-radius: 10px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.timeline-nav {
  margin-bottom: 2rem;
}

.timeline-ruler {
  position: relative;
  height: 80px;
  margin: 0 40px 20px;
}

.timeline-line {
  position: absolute;
  top: 30px;
  left: 0;
  right: 0;
  height: 4px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

.timeline-marker {
  position: absolute;
  top: 0;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.marker-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  margin-top: 22px;
  transition: all 0.3s ease;
}

.marker-label {
  padding: 4px 8px;
  margin-top: 8px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
}

.marker-dynasty {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 4px;
}

.timeline-marker:hover .marker-dot {
  background: #42b983;
  transform: scale(1.2);
}

.timeline-marker.active .marker-dot {
  background: #42b983;
  transform: scale(1.5);
  box-shadow: 0 0 10px rgba(66, 185, 131, 0.8);
}

.timeline-marker.active .marker-label {
  background: rgba(66, 185, 131, 0.3);
  color: #42b983;
  font-weight: bold;
}

.timeline-controls {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
}

.nav-btn, .play-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.nav-btn {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
}

.nav-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
}

.nav-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.play-btn {
  background: rgba(66, 185, 131, 0.2);
  color: #42b983;
  padding: 8px 24px;
  font-weight: bold;
}

.play-btn:hover {
  background: rgba(66, 185, 131, 0.4);
}

.map-display {
  min-height: 500px;
  position: relative;
}

.map-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.map-header {
  text-align: center;
  margin-bottom: 1.5rem;
}

.map-header h3 {
  color: #42b983;
  margin: 0 0 0.5rem;
  font-size: 1.8rem;
}

.map-period {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1rem;
}

.map-image-container {
  width: 100%;
  height: 500px;
  overflow: hidden;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  margin-bottom: 1.5rem;
  position: relative;
}

.map-image-container img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: rgba(0, 0, 0, 0.3);
}

.map-description {
  max-width: 800px;
  margin: 0 auto;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.1rem;
  padding: 1rem;
}

.three-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 10;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.5s ease;
}

.three-container canvas {
  width: 100% !important;
  height: 100% !important;
  display: block;
}

.three-controls {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 20;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  background: rgba(0, 0, 0, 0.5);
  padding: 15px;
  border-radius: 15px;
  backdrop-filter: blur(8px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3), 0 0 10px rgba(66, 185, 131, 0.3);
  border: 1px solid rgba(66, 185, 131, 0.3);
}

.three-btn {
  background: rgba(66, 185, 131, 0.8);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 25px;
  cursor: pointer;
  font-weight: bold;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
  min-width: 120px;
  letter-spacing: 1px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.three-btn:hover {
  background: #42b983;
  transform: translateY(-3px);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.3), 0 0 15px rgba(66, 185, 131, 0.5);
}

.three-btn:active {
  transform: translateY(-1px);
}

.effect-controls {
  display: flex;
  gap: 12px;
  width: 100%;
  justify-content: center;
}

.effect-btn {
  background: rgba(20, 30, 40, 0.7);
  color: white;
  border: 1px solid rgba(66, 185, 131, 0.3);
  padding: 8px 15px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  flex: 1;
  text-align: center;
  min-width: 85px;
}

.effect-btn::before {
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: all 0.4s ease;
}

.effect-btn:hover {
  background: rgba(66, 185, 131, 0.5);
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
}

.effect-btn:hover::before {
  left: 100%;
}

.effect-btn:active {
  transform: scale(0.95);
  background: rgba(66, 185, 131, 0.7);
}

.three-indicator {
  position: absolute;
  top: 20px;
  right: 20px;
  background: rgba(20, 30, 40, 0.7);
  padding: 10px 15px;
  border-radius: 25px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(66, 185, 131, 0.3);
  backdrop-filter: blur(5px);
  color: rgba(255, 255, 255, 0.9);
  animation: fadeIn 0.5s ease;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.indicator-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #42b983;
  animation: pulse 1.5s infinite;
}

.three-container:has(+ .map-image-container canvas.three-overlay) {
  opacity: 1;
  pointer-events: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s, transform 0.5s;
}

.fade-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(66, 185, 131, 0.7);
  }
  70% {
    box-shadow: 0 0 0 6px rgba(66, 185, 131, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(66, 185, 131, 0);
  }
}

@keyframes fadeIn {
  0% {
    opacity: 0;
  }
  100% {
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .map-image-container {
    height: 300px;
  }
  
  .timeline-ruler {
    height: 100px;
  }
  
  .marker-label {
    transform: rotate(-45deg);
    transform-origin: top left;
    margin-top: 16px;
  }
  
  .effect-controls {
    flex-direction: column;
    gap: 5px;
  }
}
</style>