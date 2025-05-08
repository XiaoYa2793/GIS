<template>
  <div class="recommendation-view">
    <div class="page-header">
      <div class="header-content">
        <h1>
          <span class="text-gradient">北京景点推荐</span>
          <div class="underline"></div>
        </h1>
        <p class="subtitle">选择您喜爱的景点，与朋友分享您的专属推荐路线</p>
      </div>
    </div>
    
    <div class="tabs-container">
      <div class="tabs">
        <div 
          class="tab" 
          :class="{ active: activeTab === 'create' }"
          @click="setActiveTab('create')"
        >
          <i class="tab-icon">✏️</i>
          <span>创建推荐</span>
        </div>
        <div 
          class="tab" 
          :class="{ active: activeTab === 'view' }"
          @click="setActiveTab('view')"
          v-if="recommendationId"
        >
          <i class="tab-icon">👁️</i>
          <span>查看推荐</span>
        </div>
      </div>
    </div>
    
    <div class="tab-content">
      <transition name="fade" mode="out-in">
        <div v-if="activeTab === 'create'" key="create">
          <RecommendationForm @created="handleRecommendationCreated" />
        </div>
        
        <div v-else-if="activeTab === 'view'" key="view" class="recommendation-details">
          <div v-if="recommendation" class="recommendation-container">
            <div class="recommendation-header">
              <div class="recommendation-title">
                <h2>{{ recommendation.title }}</h2>
                <div class="title-decoration"></div>
              </div>
              <p v-if="recommendation.description" class="recommendation-description">
                {{ recommendation.description }}
              </p>
              <p class="created-date">
                <i class="date-icon">🕒</i>
                创建于: {{ formatDate(recommendation.created_at) }}
              </p>
            </div>
            
            <div class="attractions-count">
              <span class="count-badge">{{ recommendation.attractions.length }}</span>
              个推荐景点
            </div>
            
            <div class="attractions-grid">
              <div 
                v-for="(attraction, index) in recommendation.attractions" 
                :key="attraction.id"
                class="attraction-card"
                :style="{ animationDelay: `${index * 0.1}s` }"
              >
                <div class="attraction-number">{{ index + 1 }}</div>
                <div class="attraction-image">
                  <img :src="getImageUrl(attraction)" :alt="attraction.name" />
                  <div class="attraction-overlay">
                    <span class="overlay-icon">📍</span>
                  </div>
                </div>
                <div class="attraction-info">
                  <h3>{{ attraction.name }}</h3>
                  <div class="info-divider"></div>
                  <p class="category">
                    <span class="category-badge">{{ attraction.category || '景点' }}</span>
                  </p>
                  <p class="description">{{ truncateText(attraction.description, 100) }}</p>
                  <button class="route-button" @click="showRoute(attraction)">
                    <i class="route-icon">🗺️</i>
                    查看路线
                  </button>
                </div>
              </div>
            </div>
            
            <div class="action-buttons">
              <button class="share-button" @click="showQrCode = true">
                <i class="button-icon">🔗</i>
                分享推荐
              </button>
              <button class="back-button" @click="setActiveTab('create')">
                <i class="button-icon">↩️</i>
                返回创建
              </button>
            </div>
          </div>
          
          <div v-else class="loading">
            <div class="loading-spinner"></div>
            <p>正在加载精彩推荐...</p>
          </div>
        </div>
      </transition>
    </div>
    
    <RecommendationQRCode
      v-if="showQrCode && recommendation"
      :visible="showQrCode"
      :recommendationId="recommendationId"
      :title="recommendation.title"
      :description="recommendation.description"
      @close="showQrCode = false"
    />

    <RouteModal
      v-if="showRouteModal"
      :visible="showRouteModal"
      :currentLocation="currentLocation"
      :destination="selectedDestination"
      @close="showRouteModal = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import RecommendationForm from '../components/RecommendationForm.vue'
import RecommendationQRCode from '../components/RecommendationQRCode.vue'
import RouteModal from '../components/RouteModal.vue'

const route = useRoute()
const activeTab = ref('create')
const recommendation = ref(null)
const recommendationId = ref(null)
const showQrCode = ref(false)
const showRouteModal = ref(false)
const selectedDestination = ref(null)
const currentLocation = ref(null)

// 如果URL中有推荐ID，则自动切换到查看标签
onMounted(() => {
  if (route.params.id) {
    recommendationId.value = route.params.id
    fetchRecommendation(recommendationId.value)
    setActiveTab('view')
  }
  
  // 获取当前位置
  getCurrentLocation()
})

// 监听推荐ID变化，获取推荐详情
watch(recommendationId, (newId) => {
  if (newId) {
    fetchRecommendation(newId)
  }
})

const setActiveTab = (tab) => {
  activeTab.value = tab
}

const fetchRecommendation = async (id) => {
  try {
    const response = await axios.get(`http://localhost:5000/api/recommendations/${id}`)
    recommendation.value = response.data
  } catch (error) {
    console.error('获取推荐详情失败:', error)
  }
}

const handleRecommendationCreated = (id) => {
  recommendationId.value = id
  fetchRecommendation(id)
  setActiveTab('view')
}

const getImageUrl = (attraction) => {
  if (!attraction.image_path) return null
  return `http://localhost:5000${attraction.image_path}`
}

const truncateText = (text, length) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取当前位置
const getCurrentLocation = () => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      position => {
        currentLocation.value = {
          lat: position.coords.latitude,
          lng: position.coords.longitude
        }
      },
      error => {
        console.error('获取位置失败:', error)
        // 失败时使用默认位置（从后端获取）
        fetchDefaultLocation()
      }
    )
  } else {
    console.error('浏览器不支持地理定位')
    fetchDefaultLocation()
  }
}

// 获取默认位置（天安门）
const fetchDefaultLocation = async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/current-location')
    if (response.data.status === 0) {
      currentLocation.value = response.data.location
    }
  } catch (error) {
    console.error('获取默认位置失败:', error)
    // 使用硬编码默认位置
    currentLocation.value = {
      lat: 39.9087,
      lng: 116.3976
    }
  }
}

// 显示路线模态框
const showRoute = (attraction) => {
  if (!attraction.coordinates) {
    console.error('景点缺少坐标信息')
    return
  }
  
  const [lng, lat] = attraction.coordinates.split(',').map(coord => parseFloat(coord.trim()))
  selectedDestination.value = {
    name: attraction.name,
    location: attraction.location,
    coordinates: {
      lat: lat,
      lng: lng
    }
  }
  
  showRouteModal.value = true
}
</script>

<style scoped>
.recommendation-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  color: #fff;
}

/* 页面标题样式 */
.page-header {
  text-align: center;
  margin-bottom: 40px;
  position: relative;
}

.header-content {
  position: relative;
  padding: 30px 0;
}

h1 {
  margin: 0;
  font-size: 3rem;
  font-weight: 800;
  letter-spacing: 2px;
  display: inline-block;
  position: relative;
}

.text-gradient {
  background: linear-gradient(120deg, #42b983, #67c6ff, #a78bfa);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  position: relative;
}

.underline {
  height: 8px;
  width: 100px;
  background: linear-gradient(90deg, #42b983, #67c6ff);
  border-radius: 4px;
  margin: 10px auto 0;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.8;
  }
}

.subtitle {
  color: rgba(255, 255, 255, 0.8);
  margin-top: 15px;
  font-size: 1.1rem;
  font-weight: 300;
}

/* 标签页样式 */
.tabs-container {
  margin-bottom: 30px;
}

.tabs {
  display: flex;
  gap: 20px;
  background: rgba(255, 255, 255, 0.1);
  padding: 5px;
  border-radius: 10px;
  margin: 0 auto;
  width: fit-content;
  position: relative;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.tab {
  padding: 10px 20px;
  cursor: pointer;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  display: flex;
  align-items: center;
  gap: 8px;
}

.tab-icon {
  font-size: 1.2rem;
}

.tab:hover {
  background: rgba(66, 185, 131, 0.2);
}

.tab.active {
  background: linear-gradient(135deg, #42b983, #67c6ff);
  color: white;
  box-shadow: 0 4px 15px rgba(66, 185, 131, 0.3);
  transform: translateY(-2px);
}

/* 内容区域样式 */
.tab-content {
  position: relative;
  min-height: 300px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* 推荐容器样式 */
.recommendation-container {
  background: rgba(18, 24, 38, 0.8);
  border-radius: 16px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
  padding: 30px;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.recommendation-container::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background: linear-gradient(90deg, #42b983, #67c6ff, #a78bfa);
}

.recommendation-header {
  margin-bottom: 30px;
  text-align: center;
  position: relative;
}

.recommendation-title {
  position: relative;
  display: inline-block;
  margin-bottom: 15px;
}

.recommendation-title h2 {
  margin: 0;
  font-size: 2.2rem;
  font-weight: 700;
  color: #fff;
  position: relative;
  z-index: 1;
}

.title-decoration {
  width: 50%;
  height: 10px;
  background: rgba(66, 185, 131, 0.3);
  position: absolute;
  bottom: 5px;
  left: 25%;
  z-index: 0;
  border-radius: 4px;
}

.recommendation-description {
  color: rgba(255, 255, 255, 0.8);
  max-width: 700px;
  margin: 0 auto 15px;
  line-height: 1.6;
  font-style: italic;
}

.created-date {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

.date-icon {
  margin-right: 5px;
}

.attractions-count {
  text-align: center;
  margin-bottom: 30px;
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.8);
}

.count-badge {
  display: inline-block;
  background: linear-gradient(135deg, #42b983, #67c6ff);
  color: white;
  font-weight: bold;
  padding: 3px 10px;
  border-radius: 20px;
  margin-right: 5px;
}

.attractions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 25px;
  margin-top: 30px;
}

/* 卡片样式 */
.attraction-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  position: relative;
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  animation: fadeInUp 0.5s ease forwards;
  opacity: 0;
  transform: translateY(20px);
}

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.attraction-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
  background: rgba(255, 255, 255, 0.08);
}

.attraction-number {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(66, 185, 131, 0.9);
  color: white;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  z-index: 2;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.attraction-image {
  height: 200px;
  overflow: hidden;
  position: relative;
}

.attraction-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s;
}

.attraction-card:hover .attraction-image img {
  transform: scale(1.05);
}

.attraction-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 50%;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
  opacity: 0;
  transition: opacity 0.3s;
  display: flex;
  align-items: flex-end;
  justify-content: flex-end;
  padding: 15px;
}

.attraction-card:hover .attraction-overlay {
  opacity: 1;
}

.overlay-icon {
  font-size: 24px;
}

.attraction-info {
  padding: 20px;
  position: relative;
}

.attraction-info h3 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
  color: white;
  margin-bottom: 10px;
}

.info-divider {
  height: 3px;
  width: 40px;
  background: linear-gradient(90deg, #42b983, #67c6ff);
  margin-bottom: 10px;
  border-radius: 2px;
}

.category-badge {
  display: inline-block;
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  font-size: 0.8rem;
  margin-bottom: 10px;
}

.description {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.5;
  margin: 10px 0 0;
}

/* 按钮样式 */
.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 40px;
}

.share-button, .back-button {
  padding: 12px 25px;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.button-icon {
  font-size: 1.2rem;
}

.share-button {
  background: linear-gradient(135deg, #42b983, #34d399);
  color: white;
  box-shadow: 0 4px 15px rgba(66, 185, 131, 0.4);
}

.back-button {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.share-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(66, 185, 131, 0.5);
}

.back-button:hover {
  transform: translateY(-3px);
  background: rgba(255, 255, 255, 0.15);
}

/* 加载样式 */
.loading {
  text-align: center;
  padding: 60px;
  color: rgba(255, 255, 255, 0.7);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #42b983;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .attractions-grid {
    grid-template-columns: 1fr;
  }
  
  h1 {
    font-size: 2rem;
  }
  
  .recommendation-title h2 {
    font-size: 1.8rem;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 15px;
  }
  
  .share-button, .back-button {
    width: 100%;
    justify-content: center;
  }
}

.route-button {
  margin-top: 10px;
  padding: 6px 12px;
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.3s;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.route-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

.route-icon {
  font-size: 1rem;
}
</style> 