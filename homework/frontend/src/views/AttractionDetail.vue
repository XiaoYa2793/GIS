<template>
  <div class="attraction-detail" v-if="attraction">
    <div class="detail-container">
      <div class="image-section">
        <img 
          :src="getImageUrl(attraction)" 
          :alt="attraction.name"
          @error="handleImageError"
          class="attraction-image"
        />
      </div>
      
      <div class="info-section">
        <h1>{{ attraction.name }}</h1>
        <div class="meta-info">
          <span class="category">{{ attraction.category }}</span>
          <span class="address">{{ attraction.address }}</span>
        </div>
        
        <div class="description">
          {{ attraction.description }}
        </div>

        <div class="additional-info">
          <h3>开放时间</h3>
          <p>{{ attraction.opening_hours || '暂无开放时间信息' }}</p>
          
          <h3>门票信息</h3>
          <p>{{ attraction.ticket_info || '暂无门票信息' }}</p>
        </div>

        <div class="actions">
          <button class="share-btn" @click="showShare = true">
            分享景点
          </button>
          <button class="navigate-btn" @click="navigateToMap">
            在地图中查看
          </button>
        </div>
      </div>
    </div>

    <ShareQRCode
      v-if="showShare"
      :visible="showShare"
      :attraction-id="attraction.id"
      :attraction-name="attraction.name"
      @close="showShare = false"
    />
  </div>
  <div v-else class="loading">
    <p>加载中...</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import ShareQRCode from '../components/ShareQRCode.vue'

const route = useRoute()
const router = useRouter()
const attraction = ref(null)
const showShare = ref(false)

const getImageUrl = (attraction) => {
  if (!attraction.image_path) return null
  return `http://localhost:5000${attraction.image_path}`
}

const handleImageError = (e) => {
  e.target.src = `https://via.placeholder.com/400x300?text=${encodeURIComponent(attraction.value.name)}`
}

const navigateToMap = () => {
  router.push({
    name: 'SimpleMap',
    query: { 
      lat: attraction.value.latitude,
      lng: attraction.value.longitude,
      name: attraction.value.name
    }
  })
}

const fetchAttractionDetail = async () => {
  try {
    const response = await axios.get(`http://localhost:5000/api/attractions/${route.params.id}`)
    attraction.value = response.data
  } catch (error) {
    console.error('获取景点详情失败:', error)
  }
}

onMounted(() => {
  fetchAttractionDetail()
})
</script>

<style scoped>
.attraction-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.detail-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.image-section {
  width: 100%;
}

.attraction-image {
  width: 100%;
  height: 400px;
  object-fit: cover;
  border-radius: 8px;
}

.info-section {
  padding: 20px;
}

h1 {
  margin: 0 0 20px 0;
  color: #333;
}

.meta-info {
  margin-bottom: 20px;
}

.category, .address {
  display: inline-block;
  margin-right: 15px;
  color: #666;
}

.description {
  line-height: 1.6;
  color: #444;
  margin-bottom: 30px;
}

.additional-info {
  margin-bottom: 30px;
}

.additional-info h3 {
  color: #333;
  margin: 15px 0 5px 0;
}

.additional-info p {
  color: #666;
  margin: 0;
}

.actions {
  display: flex;
  gap: 15px;
}

.share-btn, .navigate-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.share-btn {
  background: #4CAF50;
  color: white;
}

.navigate-btn {
  background: #2196F3;
  color: white;
}

.share-btn:hover {
  background: #45a049;
}

.navigate-btn:hover {
  background: #1976D2;
}

.loading {
  text-align: center;
  padding: 50px;
  color: #666;
}

@media (max-width: 768px) {
  .detail-container {
    grid-template-columns: 1fr;
  }
}
</style> 