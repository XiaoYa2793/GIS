<template>
  <div class="attractions-container">
    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在加载景点信息...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-container">
      <p>{{ error }}</p>
      <button @click="fetchAttractions">重试</button>
    </div>

    <!-- 主要内容 -->
    <template v-else>
      <!-- 搜索区域 -->
      <div class="search-section">
        <div class="search-box">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="搜索景点..."
            @input="filterAttractions"
          >
          <button class="category-btn" :class="{ active: selectedCategory === '' }" @click="selectCategory('')">
            全部
          </button>
          <button 
            v-for="category in categories" 
            :key="category"
            class="category-btn"
            :class="{ active: selectedCategory === category }"
            @click="selectCategory(category)"
          >
            {{ category }}
          </button>
        </div>
      </div>

      <!-- 景点列表 -->
      <div class="attractions-grid">
        <div 
          v-for="attraction in filteredAttractions" 
          :key="attraction.id" 
          class="attraction-card"
          @click="handleAttractionClick(attraction)"
        >
          <div class="card-image">
            <img 
              :src="getImageUrl(attraction)"
              :alt="attraction.name"
              loading="lazy"
              @error="handleImageError($event, attraction)"
              :class="{ 'image-error': imageErrors[attraction.id] }"
            >
            <div class="category-tag">{{ attraction.category }}</div>
          </div>
          <div class="card-content">
            <h3>{{ attraction.name }}</h3>
            <p class="description">{{ attraction.description }}</p>
            <div class="card-actions">
              <button class="action-btn map-btn" @click.stop="showMap(attraction)">
                <i class="fas fa-map-marker-alt"></i> 查看地图
              </button>
              <button v-if="attraction.name === '故宫博物院'" 
                      class="action-btn panorama-btn" 
                      @click.stop="openGugongPanorama()">
                <i class="fas fa-external-link-alt"></i> 全景浏览
              </button>
              <button v-if="attraction.name === '颐和园'" 
                      class="action-btn panorama-btn" 
                      @click.stop="openYiheyuanPanorama()">
                <i class="fas fa-external-link-alt"></i> 全景浏览
              </button>
              <button v-if="attraction.name === '天坛'" 
                      class="action-btn panorama-btn" 
                      @click.stop="openTiantanPanorama()">
                <i class="fas fa-external-link-alt"></i> 全景浏览
              </button>
              <button v-if="attraction.name === '八达岭长城' || attraction.name === '长城' || attraction.name.includes('长城')" 
                      class="action-btn panorama-btn" 
                      @click.stop="openChangchengPanorama()">
                <i class="fas fa-external-link-alt"></i> 全景浏览
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 地图模态框 -->
      <MapModal 
        :visible="mapVisible"
        :attraction="selectedAttraction"
        @close="closeMap"
      />
      <PanoramaViewer
        v-if="panoramaVisible"
        :visible="panoramaVisible"
        @close="closePanorama"
      />
      
      <!-- 内嵌浏览器组件 -->
      <InlineFrameViewer
        v-model:visible="inlineFrameVisible"
        :url="inlineFrameUrl"
      />
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import MapModal from './MapModal.vue'
import AMapLoader from '@amap/amap-jsapi-loader'
import PanoramaViewer from './PanoramaViewer.vue'
import InlineFrameViewer from './InlineFrameViewer.vue'

const attractions = ref([])
const searchQuery = ref('')
const selectedCategory = ref('')
const mapVisible = ref(false)
const selectedAttraction = ref(null)
const imageErrors = ref({})
const isLoading = ref(true)
const error = ref(null)
const panoramaVisible = ref(false)
const inlineFrameVisible = ref(false)
const inlineFrameUrl = ref('')

// 获取所有分类
const categories = computed(() => {
  const uniqueCategories = new Set(attractions.value.map(a => a.category))
  return Array.from(uniqueCategories)
})

// 过滤景点
const filteredAttractions = computed(() => {
  return attractions.value.filter(attraction => {
    const matchesSearch = 
      attraction.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      attraction.description.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesCategory = !selectedCategory.value || attraction.category === selectedCategory.value
    return matchesSearch && matchesCategory
  })
})

const selectCategory = (category) => {
  selectedCategory.value = category
}

const showMap = (attraction) => {
  selectedAttraction.value = attraction
  mapVisible.value = true
}

const closeMap = () => {
  mapVisible.value = false
  selectedAttraction.value = null
}

const handleAttractionClick = (attraction) => {
  if (attraction.name === '故宫博物院') {
    openGugongPanorama();
  } else if (attraction.name === '颐和园') {
    openYiheyuanPanorama();
  } else if (attraction.name === '天坛') {
    openTiantanPanorama();
  } else if (attraction.name === '八达岭长城' || attraction.name === '长城' || attraction.name.includes('长城')) {
    openChangchengPanorama();
  } else {
    showDetails(attraction);
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
    console.log('准备打开故宫全景网站');
    
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
    console.log('准备打开颐和园全景网站');
    
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

const openTiantanPanorama = async () => {
  try {
    console.log('准备打开天坛全景网站');
    
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

const openChangchengPanorama = async () => {
  try {
    console.log('准备打开长城全景网站');
    
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

const getImageUrl = (attraction) => {
  const imagePath = attraction.image_path;
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
    原始路径: attraction.image_path,
    尝试加载的URL: event.target.src
  });
  
  imageErrors.value[attraction.id] = true;
  const placeholderText = encodeURIComponent(attraction.name);
  const placeholderUrl = `https://via.placeholder.com/400x300/0a192f/ffffff?text=${placeholderText}`;
  console.log(`使用占位图片: ${placeholderUrl}`);
  event.target.src = placeholderUrl;
}

const fetchAttractions = async () => {
  try {
    isLoading.value = true
    error.value = null
    
    // 先初始化数据
    console.log('正在初始化数据...')
    try {
      const initResponse = await axios.get('http://localhost:5000/api/init-data')
      console.log('数据初始化响应:', initResponse.data)
    } catch (initError) {
      console.error('数据初始化失败:', initError.response?.data || initError.message)
    }
    
    // 获取景点列表
    console.log('正在获取景点数据...')
    const response = await axios.get('http://localhost:5000/api/attractions')
    console.log('获取到的景点数据:', response.data)
    
    if (!response.data) {
      throw new Error('返回的数据为空')
    }
    
    if (!Array.isArray(response.data)) {
      console.error('返回的数据格式:', typeof response.data, response.data)
      throw new Error('返回的数据格式不正确，期望数组类型')
    }
    
    if (response.data.length === 0) {
      console.warn('获取到的景点列表为空')
    }
    
    attractions.value = response.data
    
    // 初始化图片错误状态
    attractions.value.forEach(attraction => {
      imageErrors.value[attraction.id] = false
    })
  } catch (err) {
    console.error('获取景点数据失败:', {
      message: err.message,
      response: err.response?.data,
      status: err.response?.status
    })
    error.value = `获取景点数据失败: ${err.message || '请稍后重试'}`
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  await fetchAttractions()
  
  // 初始化高德地图
  try {
    window._AMapSecurityConfig = {
      securityJsCode: 'd31826355e4f996d3fc73ca592cb67bb'
    }

    await AMapLoader.load({
      key: '4b9c8387b9b0faeba3184f356a07afb5',
      version: '2.0',
      plugins: ['AMap.Geocoder']
    })
  } catch (err) {
    console.error('地图初始化失败:', err)
  }
})
</script>

<style scoped>
.attractions-container {
  padding: 2rem;
}

.search-section {
  margin-bottom: 2rem;
  background: rgba(255, 255, 255, 0.1);
  padding: 1rem;
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.search-box {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.search-box input {
  flex: 1;
  min-width: 200px;
  padding: 0.8rem 1rem;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.search-box input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.category-btn {
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.category-btn:hover {
  background: rgba(66, 185, 131, 0.2);
}

.category-btn.active {
  background: #42b983;
}

.attractions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
}

.attraction-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
  transition: transform 0.3s ease;
  backdrop-filter: blur(10px);
}

.attraction-card:hover {
  transform: translateY(-5px);
}

.card-image {
  position: relative;
  height: 200px;
  background: rgba(0, 0, 0, 0.1);
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: all 0.3s ease;
}

.card-image img.image-error {
  object-fit: contain;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.05);
}

.category-tag {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: rgba(66, 185, 131, 0.9);
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  font-size: 0.8rem;
  color: white;
}

.card-content {
  padding: 1.5rem;
}

.card-content h3 {
  margin: 0 0 1rem 0;
  color: white;
}

.description {
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 1rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.action-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
}

.map-btn {
  background: rgba(66, 185, 131, 0.1);
  color: #42b983;
}

.map-btn:hover {
  background: #42b983;
  color: white;
}

.panorama-btn {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.panorama-btn:hover {
  background: #3b82f6;
  color: white;
}

.image-error {
  opacity: 0.7;
  filter: grayscale(50%);
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  color: #42b983;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 3px solid rgba(66, 185, 131, 0.1);
  border-radius: 50%;
  border-top-color: #42b983;
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-container {
  text-align: center;
  padding: 2rem;
  color: #ff6b6b;
}

.error-container button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: #42b983;
  border: none;
  border-radius: 4px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.error-container button:hover {
  background: #3aa876;
}

.panorama-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(66, 185, 131, 0.9);
  color: white;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 5px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.panorama-badge i {
  font-size: 1rem;
}

.action-btn.panorama-btn {
  background-color: #42b983;
  color: white;
}

.action-btn.panorama-btn:hover {
  background-color: #3aa876;
}

.panorama-link {
  background: none;
  border: none;
  padding: 0;
  font: inherit;
  cursor: pointer;
  outline: inherit;
  color: #3b82f6;
  text-decoration: underline;
}
</style> 