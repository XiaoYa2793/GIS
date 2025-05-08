<template>
  <div class="time-space-view">
    <!-- 主容器 -->
    <div class="universe-container" ref="universeContainer">
      <!-- 视频背景 -->
      <div class="video-container" ref="videoContainer">
        <VideoPlayer
          ref="videoPlayer"
          :src="currentVideo?.url"
          :muted="true"
          :autoplay="isPlaying"
          :loop="false"
          :playbackRate="playbackRate"
          @loaded="handleVideoLoaded"
          @timeupdate="handleTimeUpdate"
          @ended="handleVideoEnded"
          @error="handleVideoError"
        />
      </div>
      
      <!-- 3D场景层 -->
      <div class="scene-layer" v-show="currentMode === '3d'">
      <canvas ref="threeCanvas"></canvas>
      </div>
      
      <!-- 粒子效果层 -->
      <div class="particles-container" ref="particlesContainer"></div>
      
      <!-- 浮动时间指示器 -->
      <div class="time-indicator" :class="{'expanded': showTimeDetails}">
        <div class="time-indicator-inner" @click="toggleTimeDetails">
          <div class="time-year">{{ currentVideo?.year || '未知年份' }}</div>
          <div class="time-period">{{ currentVideo?.period }}</div>
          <div class="time-details" v-if="showTimeDetails">
            <h3>{{ currentVideo?.name }}</h3>
            <p>{{ getDescriptionForPeriod(currentVideo?.period) }}</p>
          </div>
        </div>
        </div>
        
      <!-- 时间轴与控制面板 -->
      <div class="control-panel" :class="{'expanded': isPanelExpanded}">
        <div class="panel-toggle" @click="togglePanel">
          <div class="toggle-icon"></div>
        </div>
        
        <div class="panel-content">
          <div class="panel-header">
            <h2>北京时空光影</h2>
            <div class="view-modes">
              <button 
                v-for="mode in viewModes" 
                :key="mode.id"
                :class="['mode-btn', { active: currentMode === mode.id }]"
                @click="switchMode(mode.id)"
              >
                <i :class="mode.icon"></i>
                {{ mode.name }}
              </button>
            </div>
          </div>
          
          <!-- 时间轴 -->
          <div class="timeline-section">
            <div class="timeline-wrapper">
              <div class="timeline-track">
                <div 
                  v-for="(video, index) in videos" 
                  :key="video.id"
                  class="timeline-point"
                  :class="{ active: selectedVideoIndex === index }"
                  :style="{ left: `${videos.length <= 1 ? 50 : (index / (videos.length - 1)) * 100}%` }"
                  @click="selectVideo(index)"
                >
                  <div class="point-marker"></div>
                  <div class="point-label">{{ video.year }}</div>
                </div>
                
                <div class="time-progress" :style="{ width: `${timelineProgress}%` }"></div>
              </div>
            </div>
            
            <div class="playback-controls">
              <button class="control-btn" @click="prevVideo" :disabled="selectedVideoIndex === 0">
                <i class="el-icon-arrow-left"></i>
              </button>
              <button class="control-btn play-btn" @click="togglePlayMode">
                <i :class="isPlaying ? 'el-icon-video-pause' : 'el-icon-video-play'"></i>
              </button>
              <button class="control-btn" @click="goToNextVideo" :disabled="selectedVideoIndex === videos.length - 1">
                <i class="el-icon-arrow-right"></i>
              </button>
            </div>
          </div>
          
          <!-- 视频信息 -->
          <div class="video-info">
            <h3>{{ currentVideo?.name }}</h3>
            <p class="video-description">{{ getDescriptionForPeriod(currentVideo?.period) }}</p>
            
            <!-- 视频控制选项 -->
            <div class="video-options">
              <div class="option">
                <span>视频速度</span>
                <el-slider 
                  v-model="playbackRate" 
                  :min="0.5" 
                  :max="2" 
                  :step="0.25"
                  :format-tooltip="value => `${value}x`"
                  @change="updatePlaybackRate"
                ></el-slider>
                </div>
              
              <div class="option">
                <span>视频特效</span>
                <div class="effect-toggles">
                  <el-switch
                    v-model="enableBloom"
                    active-text="泛光"
                    inactive-text=""
                    active-color="#42b983"
                  ></el-switch>
                  <el-switch
                    v-model="enableParticles"
                    active-text="粒子"
                    inactive-text=""
                    active-color="#42b983"
                  ></el-switch>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 3D场景控制 -->
          <div class="scene-controls" v-if="currentMode === '3d'">
            <h3>3D场景控制</h3>
            <div class="control-group">
              <button class="scene-btn" @click="resetCamera">
                <i class="el-icon-refresh"></i>
                重置视角
              </button>
              <button class="scene-btn" @click="toggleAutoRotate">
                <i class="el-icon-refresh-right"></i>
                自动旋转
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 全屏按钮 -->
      <button class="fullscreen-btn" @click="toggleFullscreen">
        <i :class="isFullscreen ? 'el-icon-close' : 'el-icon-full-screen'"></i>
      </button>
      
      <!-- 时空传送门 -->
      <div class="portal-effect" v-show="isTransitioning" animation="appear">
        <div class="portal-ring"></div>
        <div class="portal-center"></div>
        </div>
      
      <!-- 加载指示器 -->
      <div class="loading-overlay" v-if="loading">
          <div class="loading-spinner"></div>
        <div class="loading-text">穿越时空中...</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, watch, nextTick } from 'vue';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass';
import axios from 'axios';
import gsap from 'gsap';
import VideoPlayer from '../components/VideoPlayer.vue';

// 状态变量
const isPanelExpanded = ref(false);
const currentMode = ref('video');
const showTimeDetails = ref(false);
const loading = ref(true);
const isTransitioning = ref(false);
const videos = ref([]);
const selectedVideoIndex = ref(0);
const isPlaying = ref(true);
const videoLoaded = ref(false);
const playbackRate = ref(1);
const enableBloom = ref(true);
const enableParticles = ref(true);
const isFullscreen = ref(false);
const timelineProgress = ref(0);
const playInterval = ref(null);
const progressInterval = ref(null);

// DOM引用
const universeContainer = ref(null);
const videoContainer = ref(null);
const videoPlayer = ref(null);
const particlesContainer = ref(null);
const threeCanvas = ref(null);

// Three.js相关变量
const scene = ref(null);
const camera = ref(null);
const renderer = ref(null);
const controls = ref(null);
const composer = ref(null);
const videoTexture = ref(null);
const videoMesh = ref(null);
const portalGroup = ref(null);
const portalParticles = ref([]);
const particleSystem = ref(null);
const clock = new THREE.Clock();

// 视图模式配置
const viewModes = [
  { id: 'video', name: '影像模式', icon: 'el-icon-video-camera' },
  { id: '3d', name: '3D模式', icon: 'el-icon-view' }
];

// 计算属性
const currentVideo = computed(() => {
  if (videos.value.length === 0 || selectedVideoIndex.value < 0) return null;
  return videos.value[selectedVideoIndex.value];
});

const nextVideoComputed = computed(() => {
  if (videos.value.length === 0 || selectedVideoIndex.value >= videos.value.length - 1) return null;
  return videos.value[selectedVideoIndex.value + 1];
});

// 方法定义
const togglePanel = () => {
  isPanelExpanded.value = !isPanelExpanded.value;
};

const toggleTimeDetails = () => {
  showTimeDetails.value = !showTimeDetails.value;
};

const switchMode = (mode) => {
  currentMode.value = mode;
  if (mode === '3d') {
    enable3DMode();
  } else {
    enableVideoMode();
  }
};

const selectVideo = async (index) => {
  if (index === selectedVideoIndex.value) return;
  
  console.log(`选择视频索引: ${index}`);
  
  // 停止当前的播放进度更新
  if (progressInterval.value) {
    clearInterval(progressInterval.value);
    progressInterval.value = null;
  }
  
  // 开始转场动画
  isTransitioning.value = true;
  
  // 等待转场动画完成
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  selectedVideoIndex.value = index;
  videoLoaded.value = false;
  timelineProgress.value = 0;
  
  console.log('当前选择的视频:', videos.value[index]);
  
  // 重置视频
  if (videoPlayer.value) {
    videoPlayer.value.stop();
    console.log('重置视频到开始位置');
    
    // 如果处于播放状态，延迟一点时间再播放新视频
    if (isPlaying.value) {
      setTimeout(() => {
        console.log('尝试播放新视频');
        videoPlayer.value.play();
      }, 100);
    }
  }
  
  // 更新3D场景中的视频纹理
  if (currentMode.value === '3d') {
    console.log('更新3D视频纹理');
    update3DVideoTexture();
  }
  
  // 结束转场动画
  setTimeout(() => {
    isTransitioning.value = false;
    console.log('转场动画结束');
  }, 500);
};

const handleVideoLoaded = () => {
  console.log('视频加载完成');
  videoLoaded.value = true;
  loading.value = false;
  
  // 如果在播放模式，开始更新进度
  if (isPlaying.value) {
    startProgressTracking();
  }
};

const handleTimeUpdate = (data) => {
  // 更新时间轴进度
  timelineProgress.value = data.percentage;
  
  // 如果视频接近结束，自动播放下一个视频
  if (data.percentage > 98) {
    if (selectedVideoIndex.value < videos.value.length - 1) {
      console.log('视频接近结束，跳转到下一个视频');
      goToNextVideo();
    } else {
      console.log('已经是最后一个视频，循环回第一个');
      selectVideo(0);
    }
  }
};

const handleVideoEnded = () => {
  console.log('视频播放结束事件被触发');
  // 由于设置了loop=false，现在会正确触发ended事件
  // 自动播放下一个视频
  if (isPlaying.value) {
    if (selectedVideoIndex.value < videos.value.length - 1) {
      console.log('播放下一个视频');
      goToNextVideo();
    } else {
      console.log('已经是最后一个视频，循环回第一个');
      selectVideo(0);
    }
  }
};

const handleVideoError = (error) => {
  console.error('视频播放错误:', error);
};

const togglePlayMode = () => {
  isPlaying.value = !isPlaying.value;
  
  if (videoPlayer.value) {
    if (isPlaying.value) {
      videoPlayer.value.play();
      startProgressTracking();
    } else {
      videoPlayer.value.pause();
      if (progressInterval.value) {
        clearInterval(progressInterval.value);
        progressInterval.value = null;
      }
    }
  }
};

const startProgressTracking = () => {
  // 清除之前的计时器
  if (progressInterval.value) {
    clearInterval(progressInterval.value);
    progressInterval.value = null;
  }
  
  // 使用VideoPlayer组件的timeupdate事件更新进度，不需要单独的计时器
};

const prevVideo = () => {
  if (selectedVideoIndex.value > 0) {
    selectVideo(selectedVideoIndex.value - 1);
  }
};

const goToNextVideo = () => {
  if (selectedVideoIndex.value < videos.value.length - 1) {
    console.log(`从视频索引 ${selectedVideoIndex.value} 切换到 ${selectedVideoIndex.value + 1}`);
    selectVideo(selectedVideoIndex.value + 1);
  } else {
    console.log('已是最后一个视频，循环回第一个');
    selectVideo(0);
  }
};

const updatePlaybackRate = (rate) => {
  playbackRate.value = rate;
  // VideoPlayer组件会自动响应playbackRate的变化
};

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    universeContainer.value.requestFullscreen().catch(err => {
      console.error(`无法进入全屏: ${err.message}`);
    });
    isFullscreen.value = true;
  } else {
    document.exitFullscreen();
    isFullscreen.value = false;
  }
};

// 根据时期获取描述信息
const getDescriptionForPeriod = (period) => {
  const descriptions = {
    '元代': '元大都是元朝的首都，今北京城的前身。元大都城垣呈方形，城周长约28.6千米，面积约50平方千米，为中国古代城市之最。是13世纪世界上最大最先进的城市之一。',
    '明代': '明代北京城由内城和外城组成，内城又称"内皇城"，为皇帝及宫廷人员居住地，外城又称"外城区"，为平民区。明代北京城形成了目前北京旧城的基本格局，特别是城市中轴线的规划，影响至今。',
    '清代': '清代北京城在明代基础上进一步完善，内城为满族人居住，外城为汉族人居住，城内设有八旗驻防。清代北京城发展到鼎盛时期，城市规模扩大，建筑精美，文化繁荣。',
    '民国': '民国时期的北平（今北京）逐渐从传统城市向现代城市转型，城市功能分区开始出现，但仍保留了大量的历史古迹。民国时期北平城墙拆除部分，建设了一些现代设施，城市开始向现代化转型。',
    '当代': '现代北京城为中华人民共和国首都，是国家的政治、文化中心，已发展成为国际化大都市，但仍保留着丰富的历史文化遗产。现代北京已形成环形+放射状的城市空间格局，既有现代化城区，又保留了历史文化街区。'
  };
  
  return descriptions[period] || '这段时期的北京充满了丰富的历史文化，是中华文明的重要见证。';
};

// Three.js相关方法
const initThreeJS = () => {
  // 创建场景
  scene.value = new THREE.Scene();
  
  // 创建相机
  const aspect = threeCanvas.value.clientWidth / threeCanvas.value.clientHeight;
  camera.value = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000);
  camera.value.position.set(0, 0, 5);
  
  // 创建渲染器
  renderer.value = new THREE.WebGLRenderer({
    canvas: threeCanvas.value,
    antialias: true,
    alpha: true
  });
  renderer.value.setSize(threeCanvas.value.clientWidth, threeCanvas.value.clientHeight);
  renderer.value.setPixelRatio(window.devicePixelRatio);
  renderer.value.toneMapping = THREE.ACESFilmicToneMapping;
  
  // 创建控制器
  controls.value = new OrbitControls(camera.value, renderer.value.domElement);
  controls.value.enableDamping = true;
  controls.value.dampingFactor = 0.05;
  controls.value.autoRotate = false;
  controls.value.rotateSpeed = 0.5;
  
  // 创建后期处理
  setupPostProcessing();
  
  // 添加光源
  setupLights();
  
  // 创建视频纹理平面
  createVideoPlane();
  
  // 创建环境效果
  createEnvironment();
  
  // 启动动画循环
  animate();
};

const setupPostProcessing = () => {
  composer.value = new EffectComposer(renderer.value);
  
  const renderPass = new RenderPass(scene.value, camera.value);
  composer.value.addPass(renderPass);
  
  const bloomPass = new UnrealBloomPass(
    new THREE.Vector2(threeCanvas.value.clientWidth, threeCanvas.value.clientHeight),
    1.5, // 强度
    0.4, // 半径
    0.85 // 阈值
  );
  composer.value.addPass(bloomPass);
};

const setupLights = () => {
  // 环境光
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
  scene.value.add(ambientLight);
  
  // 定向光
  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
  directionalLight.position.set(5, 5, 5);
  scene.value.add(directionalLight);
  
  // 添加点光源
  const pointLight = new THREE.PointLight(0x42b983, 2, 10);
  pointLight.position.set(0, 2, 4);
  scene.value.add(pointLight);
};

const createVideoPlane = () => {
  // 清除之前的视频平面
  if (videoMesh.value) {
    scene.value.remove(videoMesh.value);
  }
  
  // 创建视频纹理 - 使用VideoPlayer组件中的视频元素
  const videoElement = videoPlayer.value?.videoElement?.value;
  
  if (videoElement) {
    videoTexture.value = new THREE.VideoTexture(videoElement);
    videoTexture.value.minFilter = THREE.LinearFilter;
    videoTexture.value.magFilter = THREE.LinearFilter;
    
    // 创建平面几何体
    const geometry = new THREE.PlaneGeometry(16, 9);
    const material = new THREE.MeshBasicMaterial({ 
      map: videoTexture.value,
      side: THREE.DoubleSide,
      toneMapped: false
    });
    
    videoMesh.value = new THREE.Mesh(geometry, material);
    scene.value.add(videoMesh.value);
    
    // 缩放平面以匹配视频比例
    const scale = 0.8;
    videoMesh.value.scale.set(scale, scale, scale);
  }
};

const update3DVideoTexture = () => {
  if (videoTexture.value && videoPlayer.value?.videoElement?.value) {
    videoTexture.value.image = videoPlayer.value.videoElement.value;
    videoTexture.value.needsUpdate = true;
  }
};

const createEnvironment = () => {
  // 创建星空背景
  const starGeometry = new THREE.BufferGeometry();
  const starCount = 1000;
  const starPositions = new Float32Array(starCount * 3);
  
  for (let i = 0; i < starCount * 3; i += 3) {
    starPositions[i] = (Math.random() - 0.5) * 100;
    starPositions[i + 1] = (Math.random() - 0.5) * 100;
    starPositions[i + 2] = (Math.random() - 0.5) * 100;
  }
  
  starGeometry.setAttribute('position', new THREE.BufferAttribute(starPositions, 3));
  
  const starMaterial = new THREE.PointsMaterial({
    color: 0xffffff,
    size: 0.1,
      transparent: true,
    opacity: 0.8,
    blending: THREE.AdditiveBlending
  });
  
  const stars = new THREE.Points(starGeometry, starMaterial);
  scene.value.add(stars);
};

const initParticles = () => {
  if (!particlesContainer.value) return;
  
  // 使用GSAP创建粒子效果
  const particleCount = 100;
  const container = particlesContainer.value;
  
  for (let i = 0; i < particleCount; i++) {
    const particle = document.createElement('div');
    particle.className = 'particle';
    container.appendChild(particle);
    
    // 随机定位粒子
    gsap.set(particle, {
      x: Math.random() * container.offsetWidth,
      y: Math.random() * container.offsetHeight,
      scale: Math.random() * 0.5 + 0.2
    });
    
    animateParticle(particle);
  }
};

const animateParticle = (particle) => {
  // 创建随机动画
  const duration = Math.random() * 10 + 10;
  
  gsap.to(particle, {
    x: Math.random() * particlesContainer.value.offsetWidth,
    y: Math.random() * particlesContainer.value.offsetHeight,
    duration: duration,
    ease: "none",
    opacity: Math.random(),
    scale: Math.random() * 0.5 + 0.2,
    onComplete: () => animateParticle(particle)
  });
};

const enableVideoMode = () => {
  if (threeCanvas.value) {
    threeCanvas.value.style.opacity = 0;
  }
};

const enable3DMode = () => {
  if (threeCanvas.value) {
    threeCanvas.value.style.opacity = 1;
  }
  
  if (camera.value) {
    gsap.to(camera.value.position, {
      x: 0,
      y: 0,
      z: 5,
      duration: 1,
      ease: "power2.inOut"
    });
  }
  
  update3DVideoTexture();
};

const resetCamera = () => {
  if (camera.value) {
    gsap.to(camera.value.position, {
      x: 0,
      y: 0,
      z: 5,
      duration: 1,
      ease: "power2.inOut"
    });
    
    gsap.to(camera.value.rotation, {
      x: 0,
      y: 0,
      z: 0,
      duration: 1,
      ease: "power2.inOut"
    });
  }
};

const toggleAutoRotate = () => {
  if (controls.value) {
    controls.value.autoRotate = !controls.value.autoRotate;
  }
};

const handleResize = () => {
  if (!universeContainer.value || !camera.value || !renderer.value) return;
  
  const width = threeCanvas.value.clientWidth;
  const height = threeCanvas.value.clientHeight;
  
  camera.value.aspect = width / height;
  camera.value.updateProjectionMatrix();
  
  renderer.value.setSize(width, height);
  composer.value?.setSize(width, height);
};

const animate = () => {
  requestAnimationFrame(animate);
  
  const delta = clock.getDelta();
  
  // 更新控制器
  if (controls.value) {
    controls.value.update();
  }
  
  // 更新视频纹理
  if (videoTexture.value && videoPlayer.value?.videoElement?.value) {
    if (videoPlayer.value.videoElement.value.readyState >= videoPlayer.value.videoElement.value.HAVE_CURRENT_DATA) {
      videoTexture.value.needsUpdate = true;
    }
  }
  
  // 使用后期处理渲染
  if (composer.value && enableBloom.value) {
    composer.value.render();
  } else if (renderer.value) {
    renderer.value.render(scene.value, camera.value);
  }
};

const disposeThreeJS = () => {
  if (renderer.value) {
    renderer.value.dispose();
  }
  
  if (scene.value) {
    scene.value.traverse((object) => {
      if (object.geometry) {
        object.geometry.dispose();
      }
      if (object.material) {
        if (Array.isArray(object.material)) {
          object.material.forEach(material => material.dispose());
        } else {
          object.material.dispose();
        }
      }
    });
  }
  
  // 停止动画循环
  if (progressInterval.value) {
    clearInterval(progressInterval.value);
    progressInterval.value = null;
  }
};

// 获取视频数据
const fetchVideos = async () => {
  loading.value = true;
  try {
    console.log('开始获取视频数据...');
    try {
      // 优先尝试从API获取
      const response = await axios.get('/api/videos');
      console.log('获取到的视频数据:', response.data);
      
    if (response.data?.status === 'success') {
        videos.value = response.data.data.map(video => ({
          ...video,
          // 使用相对路径，让代理处理
          url: video.url
        }));
        
        console.log('处理后的视频数据:', videos.value);
      } else {
        throw new Error('API返回数据格式不正确');
    }
  } catch (err) {
      console.error('获取视频数据失败:', err);
      console.log('使用本地测试数据...');
      
      // 创建一些测试数据以防API调用失败 
      videos.value = [
        { 
          id: 1, 
          name: '北京元代影像',
          period: '元代',
          year: '1271', 
          url: '/static/mv展示/beijing1.mp4' 
        },
        { 
          id: 2, 
          name: '北京明代影像',
          period: '明代',
          year: '1420', 
          url: '/static/mv展示/beijing2.mp4' 
        },
        { 
          id: 3, 
          name: '北京清代影像',
          period: '清代',
          year: '1750', 
          url: '/static/mv展示/beijing3.mp4' 
        },
        { 
          id: 4, 
          name: '北京民国影像',
          period: '民国',
          year: '1935', 
          url: '/static/mv展示/beijing4.mp4' 
        },
        { 
          id: 5, 
          name: '北京当代影像',
          period: '当代',
          year: '2010', 
          url: '/static/mv展示/beijing5.mp4' 
        }
      ];
    }
  } finally {
    // 确保至少有一个视频可用
    if (videos.value.length > 0) {
      console.log(`加载了${videos.value.length}个视频`);
      await selectVideo(0);
    } else {
      console.error('没有可用的视频数据');
    }
    loading.value = false;
  }
};

// 生命周期钩子
onMounted(async () => {
  // 确保视频播放状态为true
  isPlaying.value = true;
  
  await fetchVideos();
  
  // 初始化3D场景
  nextTick(() => {
    if (threeCanvas.value) {
      initThreeJS();
    }
    
    // 初始化粒子效果
    if (particlesContainer.value && enableParticles.value) {
      initParticles();
    }
    
    // 强制触发视频播放
    if (videoPlayer.value) {
      setTimeout(() => {
        console.log('初始化后强制播放视频');
        videoPlayer.value.play();
      }, 1000);
    }
    
    // 设置自动切换视频的定时器
    const autoPlayNextVideo = () => {
      if (!isPlaying.value) return;
      
      const currentTime = videoPlayer.value?.getCurrentTime() || 0;
      const duration = videoPlayer.value?.getDuration() || 0;
      
      console.log(`检查视频播放状态: ${currentTime}/${duration}, 索引: ${selectedVideoIndex.value}/${videos.value.length-1}`);
      
      // 如果视频接近结束，切换到下一个视频
      if (duration > 0 && currentTime > 0 && (currentTime / duration) > 0.95) {
        console.log('视频接近结束，准备切换到下一个');
        
        // 添加短暂延迟，以防止在视频刚好切换时重复触发
        setTimeout(() => {
          if (selectedVideoIndex.value < videos.value.length - 1) {
            goToNextVideo();
          } else {
            console.log('循环回第一个视频');
            selectVideo(0);
          }
        }, 500);
      }
    };
    
    // 每6秒检查一次视频状态
    const videoCheckInterval = setInterval(autoPlayNextVideo, 6000);
    
    // 组件卸载时清除定时器
    window.addEventListener('beforeunload', () => {
      clearInterval(videoCheckInterval);
    });
  });
  
  window.addEventListener('resize', handleResize);
  
  // 添加用户交互检测，浏览器可能需要用户交互才能自动播放视频
  const startPlayOnUserInteraction = () => {
    if (videoPlayer.value) {
      console.log('用户交互检测到，尝试播放视频');
      videoPlayer.value.play();
    }
    document.removeEventListener('click', startPlayOnUserInteraction);
    document.removeEventListener('touchstart', startPlayOnUserInteraction);
    document.removeEventListener('keydown', startPlayOnUserInteraction);
  };
  
  document.addEventListener('click', startPlayOnUserInteraction);
  document.addEventListener('touchstart', startPlayOnUserInteraction);
  document.addEventListener('keydown', startPlayOnUserInteraction);
});

onBeforeUnmount(() => {
  // 停止视频播放
  if (videoPlayer.value) {
    videoPlayer.value.stop();
  }
  
  // 清除定时器
  if (progressInterval.value) {
    clearInterval(progressInterval.value);
    progressInterval.value = null;
  }
  
  // 清理Three.js资源
  disposeThreeJS();
  
  window.removeEventListener('resize', handleResize);
});

// 监听器
watch([enableBloom, enableParticles], ([newBloom, newParticles]) => {
  if (newParticles) {
    if (particlesContainer.value) {
      particlesContainer.value.style.opacity = 1;
      if (particlesContainer.value.children.length === 0) {
        initParticles();
      }
    }
  } else {
    if (particlesContainer.value) {
      particlesContainer.value.style.opacity = 0;
    }
  }
});

</script>

<style scoped>
.time-space-view {
  width: 100vw;
  height: 100vh;
  position: relative;
  overflow: hidden;
  margin-left:-250px;
  
}

.universe-container {
  width: 100%;
  height: 100%;
  position: relative;
  background: #000;
  overflow: hidden;
}

/* 视频容器 */
.video-container {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
  overflow: hidden;
  z-index: 1;
}

/* 3D场景层 */
.scene-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 2;
  pointer-events: none;
}

.scene-layer canvas {
  width: 100%;
  height: 100%;
  opacity: 0;
  transition: opacity 1s ease;
}

/* 粒子效果 */
.particles-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 3;
  pointer-events: none;
  opacity: 1;
  transition: opacity 0.5s ease;
}

.particle {
  position: absolute;
  width: 8px;
  height: 8px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 50%;
  pointer-events: none;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.8);
}

/* 时间指示器 */
.time-indicator {
  position: absolute;
  top: 30px;
  left: 30px;
  z-index: 10;
  color: white;
  transition: all 0.5s ease;
}

.time-indicator-inner {
  background: rgba(0, 0, 0, 0.7);
  border-radius: 10px;
  padding: 15px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(66, 185, 131, 0.3);
  box-shadow: 0 0 20px rgba(66, 185, 131, 0.3);
  cursor: pointer;
  transition: all 0.3s ease;
  margin-left: 100px;
}

.time-indicator-inner:hover {
  background: rgba(10, 10, 10, 0.8);
  transform: scale(1.02);
}

.time-year {
  font-size: 2.5rem;
  font-weight: 700;
  color: #42b983;
  margin-bottom: 5px;
  text-shadow: 0 0 10px rgba(66, 185, 131, 0.5);
}

.time-period {
  font-size: 1.2rem;
  opacity: 0.8;
}

.time-details {
  margin-top: 15px;
  max-width: 300px;
  overflow: hidden;
}

.time-details h3 {
  margin: 0 0 10px 0;
  color: #42b983;
}

.time-details p {
  margin: 0;
  line-height: 1.5;
  font-size: 0.9rem;
  opacity: 0.9;
}

.time-indicator.expanded .time-indicator-inner {
  width: 300px;
}

/* 控制面板 */
.control-panel {
  position: absolute;
  bottom: 0;
  right: 0;
  z-index: 10;
  transform: translateY(calc(100% - 50px));
  transition: transform 0.5s cubic-bezier(0.23, 1, 0.32, 1);
  width: 400px;
  max-width: 100%;
}

.control-panel.expanded {
  transform: translateY(0);
}

.panel-toggle {
  height: 50px;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 10px 0 0 0;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  border-bottom: 1px solid rgba(66, 185, 131, 0.3);
}

.toggle-icon {
  width: 30px;
  height: 4px;
  background: #42b983;
  position: relative;
  border-radius: 2px;
}

.toggle-icon:before,
.toggle-icon:after {
  content: '';
  position: absolute;
  width: 50%;
  height: 4px;
  background: #42b983;
  border-radius: 2px;
}

.toggle-icon:before {
  left: 0;
  transform: translateY(-8px);
}

.toggle-icon:after {
  right: 0;
  transform: translateY(8px);
}

.panel-content {
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  color: white;
  padding: 20px;
  border-radius: 10px 0 0 0;
  border-top: 1px solid rgba(66, 185, 131, 0.3);
  border-left: 1px solid rgba(66, 185, 131, 0.3);
  height: calc(100vh - 50px);
  max-height: 600px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.panel-header h2 {
  margin: 0 0 15px 0;
  color: #42b983;
  text-align: center;
  font-size: 1.8rem;
  text-shadow: 0 0 10px rgba(66, 185, 131, 0.5);
}

.view-modes {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.mode-btn {
  flex: 1;
  padding: 10px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.mode-btn:hover {
  background: rgba(66, 185, 131, 0.2);
}

.mode-btn.active {
  background: #42b983;
}

.mode-btn i {
  font-size: 1.2rem;
}

/* 时间轴 */
.timeline-section {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 10px;
  padding: 20px;
  border: 1px solid rgba(66, 185, 131, 0.2);
}

.timeline-wrapper {
  position: relative;
  height: 60px;
  margin-bottom: 15px;
}

.timeline-track {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 2px;
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-50%);
}

.time-progress {
  position: absolute;
  top: 50%;
  left: 0;
  height: 2px;
  background: #42b983;
  transform: translateY(-50%);
  transition: width 0.1s linear;
  z-index: 1;
}

.timeline-point {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  z-index: 2;
  cursor: pointer;
}

.point-marker {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  transition: all 0.3s ease;
}

.timeline-point.active .point-marker {
  background: #42b983;
  transform: scale(1.3);
  box-shadow: 0 0 15px rgba(66, 185, 131, 0.8);
}

.point-label {
  position: absolute;
  bottom: -25px;
  left: 50%;
  transform: translateX(-50%);
  white-space: nowrap;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
}

.timeline-point.active .point-label {
  color: #42b983;
  font-weight: bold;
}

.playback-controls {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 10px;
}

.control-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.control-btn:hover:not(:disabled) {
  background: rgba(66, 185, 131, 0.3);
}

.control-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.control-btn i {
  font-size: 1.2rem;
}

.play-btn {
  width: 50px;
  height: 50px;
  background: #42b983;
}

.play-btn:hover {
  background: #3aa876;
  box-shadow: 0 0 15px rgba(66, 185, 131, 0.5);
}

/* 视频信息 */
.video-info {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 10px;
  padding: 20px;
  border: 1px solid rgba(66, 185, 131, 0.2);
}

.video-info h3 {
  margin: 0 0 10px 0;
  color: #42b983;
}

.video-description {
  margin: 0 0 20px 0;
  line-height: 1.6;
  opacity: 0.9;
  font-size: 0.95rem;
}

.video-options {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 20px;
}

.option {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.option span {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
}

.effect-toggles {
  display: flex;
  gap: 15px;
}

/* 3D场景控制 */
.scene-controls {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 10px;
  padding: 20px;
  border: 1px solid rgba(66, 185, 131, 0.2);
}

.scene-controls h3 {
  margin: 0 0 15px 0;
  color: #42b983;
}

.control-group {
  display: flex;
  gap: 10px;
}

.scene-btn {
  flex: 1;
  padding: 10px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 0.9rem;
}

.scene-btn:hover {
  background: rgba(66, 185, 131, 0.3);
}

.scene-btn i {
  font-size: 1.1rem;
}

/* 全屏按钮 */
.fullscreen-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 10;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.7);
  border: 1px solid rgba(66, 185, 131, 0.3);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.fullscreen-btn:hover {
  background: rgba(0, 0, 0, 0.9);
  transform: scale(1.1);
}

.fullscreen-btn i {
  font-size: 1.2rem;
}

/* 时空传送门效果 */
.portal-effect {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 5;
  pointer-events: none;
  animation: appear 0.5s ease-in-out;
}

.portal-ring {
  width: 300px;
  height: 300px;
  border-radius: 50%;
  border: 4px solid #42b983;
  box-shadow: 0 0 30px rgba(66, 185, 131, 0.8), inset 0 0 30px rgba(66, 185, 131, 0.8);
  animation: pulse 2s ease-in-out infinite, rotate 10s linear infinite;
}

.portal-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 150px;
  height: 150px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(66, 185, 131, 0.8) 0%, rgba(66, 185, 131, 0) 70%);
  animation: glow 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.1); opacity: 1; }
}

@keyframes rotate {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes glow {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

@keyframes appear {
  from { 
    opacity: 0; 
    transform: translate(-50%, -50%) scale(0.5);
  }
  to { 
    opacity: 1; 
    transform: translate(-50%, -50%) scale(1);
  }
}

/* 加载指示器 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 20;
  color: white;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 5px solid rgba(66, 185, 131, 0.3);
  border-top-color: #42b983;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

.loading-text {
  font-size: 1.2rem;
  letter-spacing: 2px;
  animation: fadeInOut 1.5s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes fadeInOut {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .control-panel {
    width: 100%;
    transform: translateY(calc(100% - 40px));
  }
  
  .panel-toggle {
    height: 40px;
  }
  
  .time-indicator {
    top: 10px;
    left: 10px;
  }
  
  .time-year {
    font-size: 2rem;
  }
  
  .fullscreen-btn {
    top: 10px;
    right: 10px;
  }
  
  .panel-content {
    height: calc(100vh - 40px);
    max-height: 70vh;
  }
}
</style> 