<template>
  <div class="home">
    <div class="hero-section">
      <h1>探索北京文化之旅</h1>
      <p>发现历史文化名城的独特魅力</p>
      <div class="feature-buttons">
        <router-link to="/attractions" class="feature-btn">热门景点</router-link>
        <router-link to="/historical-maps" class="feature-btn highlight">历史地图</router-link>
      </div>
    </div>
    
    <!-- 新增历史地图特色区域 -->
    <div class="map-feature-section">
      <div class="feature-text">
        <div class="time-travel-title">
          <div class="time-travel-icon">
            <i class="fas fa-clock"></i>
          </div>
          <h2>北京历史地图时空穿越</h2>
        </div>
        <p>探索北京城从元大都、明清北京城到现代化国际都市的演变历程，通过沉浸式3D地图体验千年古都的历史变迁。</p>
        <ul class="feature-list">
          <li class="feature-item"><span class="feature-icon">🗺️</span> 多时期历史地图立体叠加</li>
          <li class="feature-item"><span class="feature-icon">⏱️</span> 时间轴3D动画城市演变</li>
          <li class="feature-item"><span class="feature-icon">📍</span> 地图兴趣点3D展示文化地标</li>
          <li class="feature-item"><span class="feature-icon">🔄</span> 现代地图与历史地图沉浸切换</li>
        </ul>
        <router-link to="/time-space-view" class="explore-btn">
          <span class="btn-text">开始3D时空之旅</span>
          <span class="btn-icon">
            <i class="fas fa-cube"></i>
          </span>
        </router-link>
      </div>
      
      <div class="feature-image">
        <div class="carousel-3d-container">
          <div class="carousel-perspective">
            <div class="carousel-slides" :style="{ transform: getCarouselTransform() }">
              <div v-for="(map, index) in historicalMapImages" :key="index" 
                   class="carousel-slide" 
                   :class="{ 'active': currentSlide === index, 'prev': getPrevIndex() === index, 'next': getNextIndex() === index }"
                   :style="{ transform: getSlideTransform(index) }">
                <img :src="map.url" :alt="map.name" @error="handleFeatureImageError($event, index)">
                <div class="slide-info">
                  <h3>{{ map.name }}</h3>
                  <div class="time-period">{{ getTimePeriod(index) }}</div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="carousel-controls-3d">
            <button class="carousel-btn prev" @click="prevSlide" aria-label="上一张">
              <i class="fas fa-chevron-left"></i>
            </button>
            <div class="time-slider">
              <div class="slider-track">
                <div class="slider-fill" :style="{ width: `${(currentSlide / (historicalMapImages.length - 1)) * 100}%` }"></div>
                <div v-for="(_, index) in historicalMapImages" :key="index" 
                     class="slider-point" 
                     :class="{ 'active': currentSlide >= index }"
                     @click="goToSlide(index)"></div>
              </div>
            </div>
            <button class="carousel-btn next" @click="nextSlide" aria-label="下一张">
              <i class="fas fa-chevron-right"></i>
            </button>
          </div>
          
          <div class="map-overlay-info">
            <div class="period-name">{{ historicalMapImages[currentSlide]?.name || '元代至现代' }}</div>
            <div class="time-arrow">
              <i class="fas fa-arrow-right"></i>
            </div>
            <div class="zoom-controls">
              <button class="zoom-btn" @click="zoomMap">
                <i class="fas fa-search-plus"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="featured-attractions">
      <h2>热门景点推荐</h2>
      <div class="attraction-grid">
        <div v-for="attraction in featuredAttractions" 
             :key="attraction.id" 
             class="attraction-card"
             @click="handleAttractionClick(attraction)">
          <img 
            :src="getImageUrl(attraction)" 
            :alt="attraction.name"
            @error="handleImageError($event, attraction)"
            :class="{ 'image-error': imageErrors[attraction.id] }"
          >
          <div class="card-content">
            <h3>{{ attraction.name }}</h3>
            <p>{{ attraction.description }}</p>
          </div>
        </div>
      </div>
      <div class="view-all-container">
        <router-link to="/attractions" class="view-all-btn">查看全部景点</router-link>
      </div>
    </div>
  </div>
  
  <!-- 内嵌浏览器组件 -->
  <InlineFrameViewer
    v-model:visible="inlineFrameVisible"
    :url="inlineFrameUrl"
  />
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import axios from 'axios'
import InlineFrameViewer from '../components/InlineFrameViewer.vue'

const featuredAttractions = ref([])
const imageErrors = ref({})
const inlineFrameVisible = ref(false)
const inlineFrameUrl = ref('')

// 添加轮播图数据和逻辑
const currentSlide = ref(0)
const autoSlideInterval = ref(null)
const historicalMapImages = ref([
  { name: '元大都', url: 'http://localhost:5000/images/maps/yuan_dadu.jpg' },
  { name: '明代北京', url: 'http://localhost:5000/images/maps/ming_beijing.jpg' },
  { name: '清代北京', url: 'http://localhost:5000/images/maps/qing_beijing.jpg' },
  { name: '民国北平', url: 'http://localhost:5000/images/maps/minguo_beiping.jpg' },
  { name: '现代北京', url: 'http://localhost:5000/images/maps/modern_beijing.jpg' }
])

const nextSlide = () => {
  currentSlide.value = (currentSlide.value + 1) % historicalMapImages.value.length
}

const prevSlide = () => {
  currentSlide.value = (currentSlide.value - 1 + historicalMapImages.value.length) % historicalMapImages.value.length
}

const goToSlide = (index) => {
  currentSlide.value = index
}

const startAutoSlide = () => {
  stopAutoSlide()
  autoSlideInterval.value = setInterval(() => {
    nextSlide()
  }, 4000)
}

const stopAutoSlide = () => {
  if (autoSlideInterval.value) {
    clearInterval(autoSlideInterval.value)
  }
}

// 3D轮播效果相关方法
const getCarouselTransform = () => {
  // 基本的平移效果，不添加太多3D变换以避免过度复杂的动画
  return `translateX(-${currentSlide * 25}%) translateZ(0)`;
}

const getSlideTransform = (index) => {
  const diff = index - currentSlide;
  
  if (diff === 0) {
    // 当前选中的幻灯片
    return 'translateZ(50px) rotateY(0deg) scale(1.1)';
  } else if (diff === 1 || diff === -1 * (historicalMapImages.value.length - 1)) {
    // 右侧下一张或循环后的第一张
    return 'translateZ(-50px) translateX(105%) rotateY(-20deg) scale(0.9)';
  } else if (diff === -1 || diff === (historicalMapImages.value.length - 1)) {
    // 左侧上一张或循环前的最后一张
    return 'translateZ(-50px) translateX(-105%) rotateY(20deg) scale(0.9)';
  } else {
    // 其他不可见的幻灯片
    return 'translateZ(-100px) scale(0.8) rotateY(0deg)';
  }
}

const getPrevIndex = () => {
  return (currentSlide - 1 + historicalMapImages.value.length) % historicalMapImages.value.length;
}

const getNextIndex = () => {
  return (currentSlide + 1) % historicalMapImages.value.length;
}

const getTimePeriod = (index) => {
  const timePeriods = [
    '1271-1368',  // 元大都
    '1368-1644',  // 明代北京
    '1644-1912',  // 清代北京
    '1912-1949',  // 民国北平
    '1949-至今'   // 现代北京
  ];
  
  return timePeriods[index] || '';
}

const zoomMap = () => {
  // 此处可以实现地图放大功能，例如打开一个模态框显示大图
  const mapUrl = historicalMapImages.value[currentSlide]?.url;
  if (mapUrl) {
    // 创建一个临时链接并打开模态框或新窗口
    window.open(mapUrl, '_blank');
  }
}

const getImageUrl = (attraction) => {
  const imagePath = attraction.image_path || attraction.image_url
  if (!imagePath) {
    console.error(`景点 ${attraction.name} 缺少图片路径`);
    return `https://via.placeholder.com/400x300/0a192f/ffffff?text=${encodeURIComponent(attraction.name)}`;
  }
  
  // 如果是以 http:// 或 https:// 开头的完整URL
  if (imagePath.match(/^https?:\/\//)) {
    return imagePath;
  }
  
  // 移除开头的斜杠并获取文件名
  const filename = imagePath.split('/').pop();
  const fullUrl = `http://localhost:5000/images/${filename}`;
  return fullUrl;
}

const handleImageError = (event, attraction) => {
  console.error(`图片加载失败:`, {
    景点名称: attraction.name,
    原始路径: attraction.image_path || attraction.image_url,
    尝试加载的URL: event.target.src
  });
  
  imageErrors.value[attraction.id] = true;
  const placeholderText = encodeURIComponent(attraction.name);
  const placeholderUrl = `https://via.placeholder.com/400x300/0a192f/ffffff?text=${placeholderText}`;
  console.log(`使用占位图片: ${placeholderUrl}`);
  event.target.src = placeholderUrl;
}

const handleFeatureImageError = (event, index) => {
  console.error(`特色图片加载失败:`, {
    图片索引: index
  });
  
  imageErrors.value[index] = true;
  const placeholderText = encodeURIComponent(historicalMapImages.value[index]?.name || '元代至现代');
  const placeholderUrl = `https://via.placeholder.com/400x300/0a192f/ffffff?text=${placeholderText}`;
  console.log(`使用占位图片: ${placeholderUrl}`);
  event.target.src = placeholderUrl;
}

// 处理景点点击
const handleAttractionClick = (attraction) => {
  if (attraction.name === '故宫博物院') {
    openGugongPanorama();
  } else if (attraction.name === '颐和园') {
    openYiheyuanPanorama();
  } else if (attraction.name === '天坛') {
    openTiantanPanorama();
  } else if (attraction.name === '八达岭长城' || attraction.name === '长城' || attraction.name.includes('长城')) {
    openChangchengPanorama();
  }
};

// 故宫全景网站URL
const gugongPanoramaUrl = 'https://pano.dpm.org.cn/#/';

// 颐和园全景网站URL
const yiheyuanPanoramaUrl = 'https://www.720yun.com/vr/b542cabuaba';

// 天坛全景网站URL
const tiantanPanoramaUrl = 'https://www.720yun.com/t/12vkuyies7q?scene_id=39471371';

// 长城全景网站URL
const changchengPanoramaUrl = 'https://www.720yun.com/t/ce0jtswwsm2?scene_id=14052175';

// 打开故宫全景网站
const openGugongPanorama = async () => {
  try {
    console.log('首页准备打开故宫全景网站');
    
    // 先从后端获取重定向链接
    const response = await axios.get('http://localhost:5000/api/redirect/gugong-panorama');
    
    if (response.data && response.data.status === 'success') {
      const redirectUrl = response.data.redirect_url || gugongPanoramaUrl;
      console.log('获取到重定向URL:', redirectUrl);
      
      // 使用内嵌浏览器显示
      inlineFrameUrl.value = redirectUrl;
      inlineFrameVisible.value = true;
    } else {
      console.error('获取重定向链接失败:', response.data);
      // 使用默认URL作为备选
      inlineFrameUrl.value = gugongPanoramaUrl;
      inlineFrameVisible.value = true;
    }
  } catch (error) {
    console.error('跳转过程中出错:', error);
    // 出错时仍使用默认URL
    inlineFrameUrl.value = gugongPanoramaUrl;
    inlineFrameVisible.value = true;
  }
};

// 打开颐和园全景网站
const openYiheyuanPanorama = async () => {
  try {
    console.log('首页准备打开颐和园全景网站');
    
    // 先从后端获取重定向链接
    const response = await axios.get('http://localhost:5000/api/redirect/yiheyuan-panorama');
    
    if (response.data && response.data.status === 'success') {
      const redirectUrl = response.data.redirect_url || yiheyuanPanoramaUrl;
      console.log('获取到重定向URL:', redirectUrl);
      
      // 使用内嵌浏览器显示
      inlineFrameUrl.value = redirectUrl;
      inlineFrameVisible.value = true;
    } else {
      console.error('获取重定向链接失败:', response.data);
      // 使用默认URL作为备选
      inlineFrameUrl.value = yiheyuanPanoramaUrl;
      inlineFrameVisible.value = true;
    }
  } catch (error) {
    console.error('跳转过程中出错:', error);
    // 出错时仍使用默认URL
    inlineFrameUrl.value = yiheyuanPanoramaUrl;
    inlineFrameVisible.value = true;
  }
};

// 打开天坛全景网站
const openTiantanPanorama = async () => {
  try {
    console.log('首页准备打开天坛全景网站');
    
    // 先从后端获取重定向链接
    const response = await axios.get('http://localhost:5000/api/redirect/tiantan-panorama');
    
    if (response.data && response.data.status === 'success') {
      const redirectUrl = response.data.redirect_url || tiantanPanoramaUrl;
      console.log('获取到重定向URL:', redirectUrl);
      
      // 使用内嵌浏览器显示
      inlineFrameUrl.value = redirectUrl;
      inlineFrameVisible.value = true;
    } else {
      console.error('获取重定向链接失败:', response.data);
      // 使用默认URL作为备选
      inlineFrameUrl.value = tiantanPanoramaUrl;
      inlineFrameVisible.value = true;
    }
  } catch (error) {
    console.error('跳转过程中出错:', error);
    // 出错时仍使用默认URL
    inlineFrameUrl.value = tiantanPanoramaUrl;
    inlineFrameVisible.value = true;
  }
};

// 打开长城全景网站
const openChangchengPanorama = async () => {
  try {
    console.log('首页准备打开长城全景网站');
    
    // 先从后端获取重定向链接
    const response = await axios.get('http://localhost:5000/api/redirect/changcheng-panorama');
    
    if (response.data && response.data.status === 'success') {
      const redirectUrl = response.data.redirect_url || changchengPanoramaUrl;
      console.log('获取到重定向URL:', redirectUrl);
      
      // 使用内嵌浏览器显示
      inlineFrameUrl.value = redirectUrl;
      inlineFrameVisible.value = true;
    } else {
      console.error('获取重定向链接失败:', response.data);
      // 使用默认URL作为备选
      inlineFrameUrl.value = changchengPanoramaUrl;
      inlineFrameVisible.value = true;
    }
  } catch (error) {
    console.error('跳转过程中出错:', error);
    // 出错时仍使用默认URL
    inlineFrameUrl.value = changchengPanoramaUrl;
    inlineFrameVisible.value = true;
  }
};

onMounted(async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/attractions')
    featuredAttractions.value = response.data.slice(0, 4) // 只显示前4个景点
    // 初始化图片错误状态
    featuredAttractions.value.forEach(attraction => {
      imageErrors.value[attraction.id] = false
    })
    
    // 启动自动轮播
    startAutoSlide()
  } catch (error) {
    console.error('获取景点数据失败:', error)
  }
})

// 组件卸载前清除轮播定时器
onBeforeUnmount(() => {
  stopAutoSlide()
})
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
  color: #2c3e50;
}

.hero-section {
  text-align: center;
  padding: 4rem 2rem;
  background: linear-gradient(rgba(255,255,255,0.9), rgba(255,255,255,0.9)),
              url('http://localhost:5000/images/placeholder.jpg');
  background-size: cover;
  border-radius: 8px;
  margin-bottom: 3rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.hero-section h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 1rem;
}

.hero-section p {
  font-size: 1.2rem;
  color: #666;
  margin-bottom: 2rem;
}

.feature-buttons {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.feature-btn {
  display: inline-block;
  padding: 0.8rem 1.8rem;
  background-color: #f5f5f5;
  color: #333;
  text-decoration: none;
  border-radius: 30px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.feature-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.feature-btn.highlight {
  background-color: #42b983;
  color: white;
}

.feature-btn.highlight:hover {
  background-color: #3aa876;
}

/* 3D历史地图特色区域 */
.time-travel-title {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
}

.time-travel-icon {
  background: linear-gradient(135deg, #42b983, #3b82f6);
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  color: white;
  font-size: 1.5rem;
  box-shadow: 0 10px 20px rgba(66, 185, 131, 0.3);
}

.map-feature-section {
  display: flex;
  gap: 2rem;
  align-items: center;
  margin-bottom: 4rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
}

.map-feature-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #42b983, transparent);
  animation: gradient-move 8s infinite linear;
}

@keyframes gradient-move {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.feature-text {
  flex: 1;
  padding-right: 1rem;
}

.feature-text h2 {
  font-size: 2.2rem;
  margin-bottom: 1rem;
  color: #2c3e50;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  font-weight: 700;
}

.feature-text p {
  margin-bottom: 1.5rem;
  line-height: 1.7;
  color: #505a66;
  font-size: 1.1rem;
}

.feature-list {
  list-style: none;
  padding: 0;
  margin-bottom: 2rem;
}

.feature-item {
  margin-bottom: 1rem;
  padding: 0.8rem 1rem;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  display: flex;
  align-items: center;
  transform: translateZ(0);
  transition: all 0.3s ease;
  border-left: 3px solid #42b983;
}

.feature-item:hover {
  transform: translateX(5px) translateZ(0);
  background: rgba(255, 255, 255, 0.12);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
}

.feature-icon {
  margin-right: 1rem;
  font-size: 1.5rem;
  background: linear-gradient(135deg, #42b983, #3b82f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.explore-btn {
  display: inline-flex;
  align-items: center;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #42b983, #3aa876);
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1.1rem;
  transition: all 0.3s ease;
  box-shadow: 0 10px 20px rgba(66, 185, 131, 0.3);
  position: relative;
  overflow: hidden;
  z-index: 1;
}

.explore-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #3aa876, #42b983);
  opacity: 0;
  z-index: -1;
  transition: opacity 0.3s ease;
}

.explore-btn:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(66, 185, 131, 0.4);
}

.explore-btn:hover::before {
  opacity: 1;
}

.btn-text {
  margin-right: 10px;
}

.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  transition: transform 0.3s ease;
}

.explore-btn:hover .btn-icon {
  transform: rotate(45deg);
}

.feature-image {
  flex: 1.2;
  position: relative;
}

.carousel-3d-container {
  position: relative;
  width: 100%;
  height: 450px;
  perspective: 1000px;
  overflow: visible;
}

.carousel-perspective {
  width: 100%;
  height: 100%;
  transform-style: preserve-3d;
  perspective: 1000px;
}

.carousel-slides {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.8s cubic-bezier(0.215, 0.61, 0.355, 1);
  transform-style: preserve-3d;
}

.carousel-slide {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0.7;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
  transition: all 0.8s cubic-bezier(0.215, 0.61, 0.355, 1);
  transform-style: preserve-3d;
  backface-visibility: hidden;
}

.carousel-slide img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: all 0.8s ease;
  border-radius: 16px;
}

.carousel-slide.active {
  opacity: 1;
  z-index: 10;
}

.carousel-slide.active img {
  filter: brightness(1.1) contrast(1.1);
}

.slide-info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 1.5rem;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
  color: white;
  transform: translateZ(20px);
}

.slide-info h3 {
  margin: 0 0 5px 0;
  font-size: 1.8rem;
  font-weight: 700;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
}

.time-period {
  font-size: 1rem;
  opacity: 0.9;
  display: inline-block;
  background: rgba(66, 185, 131, 0.7);
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  margin-top: 5px;
}

.carousel-controls-3d {
  position: absolute;
  bottom: -30px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 15px;
  z-index: 20;
  background: rgba(255, 255, 255, 0.1);
  padding: 10px 20px;
  border-radius: 30px;
  backdrop-filter: blur(10px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.carousel-btn {
  background-color: rgba(255, 255, 255, 0.1);
  color: #42b983;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.carousel-btn:hover {
  background-color: #42b983;
  color: white;
  transform: scale(1.1);
}

.time-slider {
  width: 200px;
  position: relative;
}

.slider-track {
  height: 4px;
  background: rgba(255, 255, 255, 0.2);
  position: relative;
  border-radius: 4px;
}

.slider-fill {
  position: absolute;
  height: 100%;
  background: linear-gradient(90deg, #4eacf3, #42b983);
  left: 0;
  top: 0;
  border-radius: 4px;
  transition: width 0.8s cubic-bezier(0.215, 0.61, 0.355, 1);
}

.slider-point {
  position: absolute;
  width: 12px;
  height: 12px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  cursor: pointer;
  z-index: 2;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.slider-point.active {
  background: #42b983;
  transform: translate(-50%, -50%) scale(1.2);
  box-shadow: 0 0 10px rgba(66, 185, 131, 0.5);
  border-color: white;
}

/* 设置每个点的位置 */
.slider-point:nth-child(1) { left: 0%; }
.slider-point:nth-child(2) { left: 25%; }
.slider-point:nth-child(3) { left: 50%; }
.slider-point:nth-child(4) { left: 75%; }
.slider-point:nth-child(5) { left: 100%; }

.map-overlay-info {
  position: absolute;
  top: 20px;
  left: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(0, 0, 0, 0.7);
  padding: 10px 15px;
  border-radius: 30px;
  backdrop-filter: blur(5px);
  color: white;
  z-index: 20;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.period-name {
  font-weight: 600;
  font-size: 1.1rem;
}

.time-arrow {
  color: #42b983;
}

.zoom-controls {
  margin-left: 5px;
}

.zoom-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 5px;
}

.zoom-btn:hover {
  color: #42b983;
}

.featured-attractions {
  padding: 2rem 0;
}

.featured-attractions h2 {
  text-align: center;
  margin-bottom: 2rem;
}

.attraction-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  padding: 0 1rem;
}

.attraction-card {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.3s ease;
  background: white;
  cursor: pointer;
}

.attraction-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.15);
}

.attraction-card img {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.card-content {
  padding: 1.5rem;
}

.card-content h3 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
}

.card-content p {
  color: #666;
  font-size: 0.9rem;
  line-height: 1.5;
}

.image-error {
  opacity: 0.7;
  filter: grayscale(50%);
}

.view-all-container {
  text-align: center;
  margin-top: 3rem;
}

.view-all-btn {
  display: inline-block;
  padding: 0.8rem 2rem;
  background-color: transparent;
  border: 2px solid #42b983;
  color: #42b983;
  text-decoration: none;
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.view-all-btn:hover {
  background-color: #42b983;
  color: white;
}

.panorama-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
  color: #42b983;
  font-weight: 500;
}

.panorama-link i {
  font-size: 1.1rem;
}

.attraction-card:hover .panorama-link {
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .map-feature-section {
    flex-direction: column;
  }
  
  .feature-image {
    width: 100%;
  }
  
  .carousel-container,
  .carousel-slides img {
    height: 300px;
  }
}
</style> 