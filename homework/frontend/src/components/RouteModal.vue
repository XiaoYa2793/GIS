<template>
  <div class="route-modal" v-if="visible">
    <div class="route-content">
      <div class="route-header">
        <div class="header-decoration"></div>
        <h3>到达路线</h3>
        <p v-if="destination">{{ destination.name }}</p>
        
        <div class="location-selector">
          <div class="location-display">
            <span class="location-label">出发地:</span>
            <span v-if="isCustomLocation" class="location-value custom">{{ customLocationName }}</span>
            <span v-else class="location-value">当前位置</span>
            <button class="location-edit" @click="toggleLocationInput">
              {{ isCustomLocation ? '使用当前位置' : '修改' }}
            </button>
          </div>
          
          <div v-if="showLocationInput" class="location-input-container">
            <input 
              v-model="customLocationName" 
              class="location-input" 
              placeholder="输入出发地点名称"
              @keyup.enter="setCustomLocation"
            />
            <button class="location-confirm" @click="setCustomLocation">确定</button>
          </div>
          
          <div v-if="showLocationInput" class="quick-locations">
            <span class="quick-label">热门城市:</span>
            <div class="quick-buttons">
              <button 
                v-for="city in commonCities" 
                :key="city.name"
                class="quick-city-btn"
                @click="quickSelectLocation(city)"
              >
                {{ city.name }}
              </button>
            </div>
          </div>
        </div>
        
        <div class="travel-mode-tabs">
          <div 
            v-for="(mode, index) in travelModes" 
            :key="index"
            class="mode-tab"
            :class="{ active: selectedMode === mode.value }"
            @click="changeMode(mode.value)"
          >
            <span class="mode-icon">{{ mode.icon }}</span>
            <span>{{ mode.name }}</span>
          </div>
        </div>
      </div>
      
      <div class="route-container">
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>正在规划路线...</p>
        </div>
        <div v-else-if="error" class="error-container">
          <span class="error-icon">⚠️</span>
          <p>{{ error }}</p>
        </div>
        <div v-else-if="route" class="route-details">
          <div class="route-summary">
            <div class="summary-item">
              <span class="summary-label">总距离</span>
              <span class="summary-value">{{ formatDistance(route.distance) }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">预计时间</span>
              <span class="summary-value">{{ formatDuration(route.duration) }}</span>
            </div>
          </div>
          
          <div class="route-steps">
            <h4>导航指示</h4>
            <div class="steps-container">
              <div 
                v-for="(step, index) in route.navigation_steps" 
                :key="index"
                class="step-item"
              >
                <div class="step-number">{{ index + 1 }}</div>
                <div class="step-content">
                  <div class="step-instruction" v-html="step.instruction"></div>
                  <div class="step-details">
                    <span>{{ formatDistance(step.distance) }}</span>
                    <span class="dot-separator">•</span>
                    <span>{{ formatDuration(step.duration) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div v-if="mapUrl" class="map-preview">
            <div class="map-title">路线地图预览</div>
            <div class="map-info">
              <div class="map-point">
                <span class="point-icon start">A</span>
                <span class="point-name">{{ isCustomLocation ? customLocationName : '当前位置' }}</span>
              </div>
              <div class="route-arrow">→</div>
              <div class="map-point">
                <span class="point-icon end">B</span>
                <span class="point-name">{{ destination.name }}</span>
              </div>
            </div>
            <img :src="mapUrl" alt="路线地图预览" class="map-image" />
            <a :href="mapDeepLink" target="_blank" class="open-map-btn">
              <span class="btn-icon">🗺️</span>
              在地图中查看
            </a>
          </div>
        </div>
      </div>
      
      <div class="route-footer">
        <button class="close-btn" @click="$emit('close')">
          <span class="btn-icon">✖️</span>
          关闭
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({
  visible: Boolean,
  currentLocation: Object,
  destination: Object
})

const travelModes = [
  { name: '步行', value: 'walking', icon: '🚶' },
  { name: '骑行', value: 'riding', icon: '🚲' },
  { name: '驾车', value: 'driving', icon: '🚗' }
]

const selectedMode = ref('walking')
const loading = ref(false)
const error = ref(null)
const route = ref(null)
const isCustomLocation = ref(false)
const customLocationName = ref('')
const customLocationCoord = ref(null)
const showLocationInput = ref(false)

const commonCities = [
  { name: '北京', lat: 39.9087, lng: 116.3976 },
  { name: '上海', lat: 31.2304, lng: 121.4737 },
  { name: '广州', lat: 23.1291, lng: 113.2644 },
  { name: '深圳', lat: 22.5431, lng: 114.0579 },
  { name: '南京', lat: 32.0603, lng: 118.7969 },
  { name: '燕郊', lat: 39.9374, lng: 116.8245 }
]

// 监听目的地和当前位置变化，获取路线
watch(
  [() => props.destination, () => props.currentLocation, selectedMode, isCustomLocation, customLocationCoord],
  async ([newDest, newLoc, newMode, isCustom, customCoord]) => {
    if (props.visible && newDest && (newLoc || (isCustom && customCoord))) {
      await fetchRoute()
    }
  },
  { immediate: true }
)

// 当模态框显示时获取路线
watch(() => props.visible, async (newVisible) => {
  if (newVisible && props.destination && (props.currentLocation || (isCustomLocation.value && customLocationCoord.value))) {
    await fetchRoute()
  }
})

const changeMode = (mode) => {
  selectedMode.value = mode
}

const toggleLocationInput = () => {
  if (isCustomLocation.value) {
    // 返回使用当前位置
    isCustomLocation.value = false
    customLocationName.value = ''
    customLocationCoord.value = null
    showLocationInput.value = false
    fetchRoute()
  } else {
    // 显示输入框
    showLocationInput.value = true
  }
}

const setCustomLocation = async () => {
  if (!customLocationName.value.trim()) {
    return
  }
  
  loading.value = true
  
  try {
    // 通过地点名称获取坐标
    const response = await axios.get('/api/geocode', {
      params: {
        address: customLocationName.value
      }
    })
    
    if (response.data.status === 0 && response.data.location) {
      customLocationCoord.value = {
        lat: response.data.location.lat,
        lng: response.data.location.lng
      }
      isCustomLocation.value = true
      showLocationInput.value = false
      fetchRoute()
    } else {
      error.value = '无法获取该地点的坐标，请重试或选择其他地点'
    }
  } catch (err) {
    console.error('获取地点坐标出错:', err)
    error.value = '获取地点坐标失败，请重试'
  } finally {
    loading.value = false
  }
}

const getEffectiveLocation = () => {
  if (isCustomLocation.value && customLocationCoord.value) {
    return customLocationCoord.value
  }
  return props.currentLocation
}

const fetchRoute = async () => {
  const effectiveLocation = getEffectiveLocation()
  if (!effectiveLocation || !props.destination) return
  
  loading.value = true
  error.value = null
  route.value = null
  
  try {
    // 发送国外坐标标志，防止自动替换坐标
    const params = {
      current_lat: effectiveLocation.lat,
      current_lng: effectiveLocation.lng,
      destination: props.destination.name,
      mode: selectedMode.value,
      allow_foreign: true // 添加标志允许国外坐标
    }
    
    // 如果是自定义位置，添加起点名称
    if (isCustomLocation.value) {
      params.start_name = customLocationName.value
    }
    
    // 使用相对路径，避免硬编码URL
    const response = await axios.get('/api/real-navigation', {
      params,
      timeout: 30000
    })
    
    if (response.data.status === 0 && response.data.route) {
      route.value = response.data.route
    } else {
      error.value = response.data.message || '获取路线失败'
      
      // 如果没有路线数据但有起点和终点，创建一个简单的直线路线
      if (!route.value && effectiveLocation && props.destination) {
        createSimpleRoute(effectiveLocation)
      }
    }
  } catch (err) {
    console.error('获取路线出错:', err)
    error.value = '获取路线时发生错误，正在使用简化路线'
    
    // 出错时也创建一个简单路线作为备选
    createSimpleRoute(effectiveLocation)
  } finally {
    loading.value = false
  }
}

// 创建一个简单的直线路线作为备选
const createSimpleRoute = (effectiveLocation) => {
  const sourceLabel = isCustomLocation.value ? customLocationName.value : '当前位置'
  
  route.value = {
    points: [
      [effectiveLocation.lat, effectiveLocation.lng],
      [props.destination.coordinates.lat, props.destination.coordinates.lng]
    ],
    distance: calculateDistance(
      effectiveLocation.lat, 
      effectiveLocation.lng, 
      props.destination.coordinates.lat, 
      props.destination.coordinates.lng
    ),
    duration: 1800, // 默认30分钟
    navigation_steps: [
      {
        instruction: `从${sourceLabel}出发，前往${props.destination.name}`,
        distance: calculateDistance(
          effectiveLocation.lat, 
          effectiveLocation.lng, 
          props.destination.coordinates.lat, 
          props.destination.coordinates.lng
        ),
        duration: 1800,
        path: `${effectiveLocation.lng},${effectiveLocation.lat};${props.destination.coordinates.lng},${props.destination.coordinates.lat}`
      }
    ],
    current_location: [effectiveLocation.lat, effectiveLocation.lng],
    destination: [props.destination.coordinates.lat, props.destination.coordinates.lng]
  }
}

// 计算两点之间的距离
const calculateDistance = (lat1, lng1, lat2, lng2) => {
  const R = 6371000 // 地球半径（米）
  const lat1Rad = (lat1 * Math.PI) / 180
  const lat2Rad = (lat2 * Math.PI) / 180
  const latDiff = ((lat2 - lat1) * Math.PI) / 180
  const lngDiff = ((lng2 - lng1) * Math.PI) / 180

  const a =
    Math.sin(latDiff / 2) * Math.sin(latDiff / 2) +
    Math.cos(lat1Rad) * Math.cos(lat2Rad) * Math.sin(lngDiff / 2) * Math.sin(lngDiff / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return Math.round(R * c) // 返回米数
}

const formatDistance = (distance) => {
  if (!distance) return '未知距离'
  if (distance < 1000) {
    return `${distance}米`
  }
  return `${(distance / 1000).toFixed(1)}公里`
}

const formatDuration = (seconds) => {
  if (!seconds) return '未知时间'
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  
  if (hours > 0) {
    return `${hours}小时${minutes}分钟`
  }
  return `${minutes}分钟`
}

// 生成百度地图URL
const mapUrl = computed(() => {
  if (!route.value || !props.destination) return null
  
  const effectiveLocation = getEffectiveLocation();
  if (!effectiveLocation) return null;
  
  // 根据不同交通方式设置不同的路线颜色
  let pathStyle = '0xff0000,5,1'; // 默认红色路线
  if (selectedMode.value === 'walking') {
    pathStyle = '0x4caf50,5,1'; // 步行绿色
  } else if (selectedMode.value === 'riding') {
    pathStyle = '0x2196f3,5,1'; // 骑行蓝色
  } else if (selectedMode.value === 'driving') {
    pathStyle = '0xff9800,5,1'; // 驾车橙色
  }
  
  // 这里简单地返回一个静态地图URL，实际应用中可能需要更复杂的处理
  const points = route.value.points.slice(0, 10).map(point => `${point[1]},${point[0]}`).join(';')
  return `https://api.map.baidu.com/staticimage/v2?ak=mvULQ1iMcjGZLjpEOSPKfRUdMRuvIwV1&width=400&height=300&paths=${points}&path_style=${pathStyle}&markers=${effectiveLocation.lng},${effectiveLocation.lat}|${props.destination.coordinates.lng},${props.destination.coordinates.lat}&markerStyles=l,A|l,B`
})

// 生成百度地图深度链接
const mapDeepLink = computed(() => {
  if (!props.destination) return '#'
  
  const effectiveLocation = getEffectiveLocation();
  if (!effectiveLocation) return '#';
  
  const locationLabel = isCustomLocation.value ? encodeURIComponent(customLocationName.value) : '当前位置';
  
  // 生成百度地图导航链接
  return `https://map.baidu.com/dir/?origin=latlng:${effectiveLocation.lat},${effectiveLocation.lng}|name:${locationLabel}&destination=latlng:${props.destination.coordinates.lat},${props.destination.coordinates.lng}|name:${encodeURIComponent(props.destination.name)}&mode=${selectedMode.value}`
})

const quickSelectLocation = (city) => {
  customLocationName.value = city.name
  customLocationCoord.value = {
    lat: city.lat,
    lng: city.lng
  }
  isCustomLocation.value = true
  showLocationInput.value = false
  fetchRoute()
}

defineEmits(['close'])
</script>

<style scoped>
.route-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(5px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.route-content {
  background: rgba(18, 24, 38, 0.95);
  padding: 30px;
  border-radius: 16px;
  max-width: 550px;
  width: 90%;
  color: white;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  animation: slideUp 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

@keyframes slideUp {
  from {
    transform: translateY(50px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.route-header {
  margin-bottom: 20px;
  position: relative;
  padding-bottom: 15px;
  text-align: center;
}

.header-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, #42b983, #67c6ff, #a78bfa);
  border-radius: 2px;
}

.route-header h3 {
  margin: 15px 0 10px;
  color: white;
  font-size: 1.8rem;
  font-weight: 600;
  background: linear-gradient(120deg, #42b983, #67c6ff);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  display: inline-block;
}

.route-header p {
  margin: 0 0 20px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.2rem;
}

.travel-mode-tabs {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 15px;
}

.mode-tab {
  padding: 8px 15px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  gap: 5px;
}

.mode-tab:hover {
  background: rgba(255, 255, 255, 0.2);
}

.mode-tab.active {
  background: linear-gradient(135deg, #42b983, #67c6ff);
  box-shadow: 0 3px 10px rgba(66, 185, 131, 0.3);
}

.mode-icon {
  font-size: 1.2rem;
}

.route-container {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 20px;
}

.loading-container, .error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
  color: rgba(255, 255, 255, 0.7);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #42b983;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-icon {
  font-size: 2rem;
  margin-bottom: 15px;
}

.route-summary {
  display: flex;
  justify-content: space-around;
  margin-bottom: 25px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.summary-label {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 5px;
}

.summary-value {
  font-size: 1.3rem;
  font-weight: 600;
  color: #fff;
}

.route-steps {
  margin-bottom: 25px;
}

.route-steps h4 {
  margin: 0 0 15px;
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.9);
}

.steps-container {
  max-height: 200px;
  overflow-y: auto;
  padding-right: 10px;
}

.step-item {
  display: flex;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.step-number {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: rgba(66, 185, 131, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-right: 15px;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-instruction {
  margin-bottom: 5px;
  line-height: 1.5;
}

.step-details {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.6);
  display: flex;
  align-items: center;
}

.dot-separator {
  margin: 0 8px;
}

.map-preview {
  margin-top: 20px;
  text-align: center;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 12px;
  padding: 15px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.map-title {
  font-size: 1.1rem;
  margin-bottom: 10px;
  color: rgba(255, 255, 255, 0.9);
}

.map-info {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 10px;
}

.map-point {
  display: flex;
  align-items: center;
  gap: 8px;
  max-width: 150px;
}

.point-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  flex-shrink: 0;
}

.point-icon.start {
  background-color: #42b983;
}

.point-icon.end {
  background-color: #e74c3c;
}

.point-name {
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.route-arrow {
  margin: 0 10px;
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.6);
}

.map-image {
  width: 100%;
  border-radius: 8px;
  margin-bottom: 15px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.open-map-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
  text-decoration: none;
  border-radius: 50px;
  font-weight: 500;
  transition: all 0.3s;
}

.open-map-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(41, 128, 185, 0.4);
}

.route-footer {
  display: flex;
  justify-content: center;
}

.close-btn {
  padding: 10px 25px;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.btn-icon {
  font-size: 1.1rem;
}

/* 自定义滚动条 */
.steps-container::-webkit-scrollbar, .route-container::-webkit-scrollbar {
  width: 8px;
}

.steps-container::-webkit-scrollbar-track, .route-container::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}

.steps-container::-webkit-scrollbar-thumb, .route-container::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
}

.steps-container::-webkit-scrollbar-thumb:hover, .route-container::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .route-content {
    width: 95%;
    padding: 20px;
    max-height: 90vh;
  }
  
  .travel-mode-tabs {
    flex-wrap: wrap;
  }
  
  .route-summary {
    flex-direction: column;
    gap: 15px;
  }
  
  .steps-container {
    max-height: 150px;
  }
}

.location-selector {
  margin: 15px auto;
  width: 100%;
  max-width: 400px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  padding: 10px;
  text-align: left;
}

.location-display {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.location-label {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  margin-right: 8px;
}

.location-value {
  font-weight: 500;
  flex: 1;
}

.location-value.custom {
  color: #42b983;
}

.location-edit {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  padding: 3px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s;
}

.location-edit:hover {
  background: rgba(255, 255, 255, 0.2);
}

.location-input-container {
  margin-top: 10px;
  display: flex;
  gap: 8px;
}

.location-input {
  flex: 1;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.9rem;
}

.location-input:focus {
  outline: none;
  border-color: rgba(66, 185, 131, 0.5);
}

.location-confirm {
  background: #42b983;
  border: none;
  color: white;
  padding: 0 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.location-confirm:hover {
  background: #3aa876;
  transform: translateY(-1px);
}

.quick-locations {
  margin-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 10px;
}

.quick-label {
  display: block;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 8px;
}

.quick-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-city-btn {
  background: rgba(66, 185, 131, 0.2);
  border: 1px solid rgba(66, 185, 131, 0.3);
  color: rgba(255, 255, 255, 0.9);
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-city-btn:hover {
  background: rgba(66, 185, 131, 0.3);
  transform: translateY(-1px);
}
</style> 