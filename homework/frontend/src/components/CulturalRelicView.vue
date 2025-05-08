<template>
  <div class="cultural-relic-view">
    <div v-if="isLoading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在加载文物信息...</p>
    </div>
    
    <div v-else-if="error" class="error-container">
      <p>{{ error }}</p>
      <button @click="loadRelics">重试</button>
    </div>
    
    <div v-else>
      <!-- 过滤器 -->
      <div class="filters">
        <div class="filter-group">
          <label>时期筛选:</label>
          <select v-model="selectedPeriod" @change="filterRelics">
            <option value="">全部时期</option>
            <option v-for="period in periods" :key="period" :value="period">
              {{ period }}
            </option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>分类筛选:</label>
          <select v-model="selectedCategory" @change="filterRelics">
            <option value="">全部分类</option>
            <option v-for="category in categories" :key="category" :value="category">
              {{ category }}
            </option>
          </select>
        </div>
      </div>
      
      <!-- 文物网格 -->
      <div class="relics-grid">
        <div 
          v-for="relic in filteredRelics" 
          :key="relic.id"
          class="relic-card"
          @click="selectRelic(relic)"
        >
          <div class="relic-image">
            <img 
              :src="getImageUrl(relic.image_path)" 
              :alt="relic.name"
              @error="handleImageError($event, relic)"
            >
          </div>
          <div class="relic-content">
            <h3>{{ relic.name }}</h3>
            <p class="relic-period">{{ relic.period }} (约 {{ relic.year }} 年)</p>
            <p class="relic-location">
              <i class="fas fa-map-marker-alt"></i> {{ relic.location }}
            </p>
            <div class="relic-category">{{ relic.category }}</div>
          </div>
        </div>
      </div>
      
      <!-- 文物详情弹窗 -->
      <div v-if="selectedRelic && showDetailModal" class="detail-modal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>{{ selectedRelic.name }}</h2>
            <button class="close-btn" @click="closeDetailModal">×</button>
          </div>
          <div class="modal-body">
            <div class="relic-detail-image">
              <img 
                :src="getImageUrl(selectedRelic.image_path)" 
                :alt="selectedRelic.name"
                @error="handleImageError($event, selectedRelic)"
              >
            </div>
            <div class="relic-detail-info">
              <div class="info-row">
                <span class="info-label">时期:</span>
                <span class="info-value">{{ selectedRelic.period }} (约 {{ selectedRelic.year }} 年)</span>
              </div>
              <div class="info-row">
                <span class="info-label">分类:</span>
                <span class="info-value">{{ selectedRelic.category }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">位置:</span>
                <span class="info-value">{{ selectedRelic.location }}</span>
              </div>
              <div class="info-row description">
                <span class="info-label">描述:</span>
                <p class="info-value">{{ selectedRelic.description }}</p>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="map-btn" @click="showRelicMap">
              <i class="fas fa-map-marker-alt"></i> 在地图上查看
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';

// 状态变量
const relics = ref([]);
const periods = ref([]);
const categories = ref([]);
const selectedPeriod = ref('');
const selectedCategory = ref('');
const selectedRelic = ref(null);
const showDetailModal = ref(false);
const isLoading = ref(true);
const error = ref(null);

// 计算属性：过滤后的文物
const filteredRelics = computed(() => {
  return relics.value.filter(relic => {
    const matchesPeriod = !selectedPeriod.value || relic.period === selectedPeriod.value;
    const matchesCategory = !selectedCategory.value || relic.category === selectedCategory.value;
    return matchesPeriod && matchesCategory;
  });
});

// 处理图片URL
const getImageUrl = (imagePath) => {
  if (!imagePath) return null;
  
  if (imagePath.match(/^https?:\/\//)) {
    return imagePath;
  }
  
  return `http://localhost:5000${imagePath}`;
};

// 图片加载错误处理
const handleImageError = (event, item) => {
  console.error(`图片加载失败:`, {
    名称: item.name,
    路径: item.image_path
  });
  event.target.src = 'http://localhost:5000/images/placeholder.jpg';
};

// 筛选文物
const filterRelics = () => {
  console.log(`应用筛选: 时期=${selectedPeriod.value}, 分类=${selectedCategory.value}`);
};

// 选择文物
const selectRelic = (relic) => {
  selectedRelic.value = relic;
  showDetailModal.value = true;
};

// 关闭详情弹窗
const closeDetailModal = () => {
  showDetailModal.value = false;
};

// 在地图上查看文物
const showRelicMap = () => {
  // 实现地图定位功能
  alert(`在地图上查看: ${selectedRelic.value.name} (坐标: ${selectedRelic.value.coordinates})`);
};

// 初始化文化数据
const initCulturalData = async () => {
  try {
    await axios.get('http://localhost:5000/api/init-cultural-data');
    console.log('文化数据初始化完成');
  } catch (err) {
    console.error('初始化文化数据失败:', err);
  }
};

// 加载文物数据
const loadRelics = async () => {
  isLoading.value = true;
  error.value = null;
  
  try {
    // 初始化文化数据
    await initCulturalData();
    
    // 获取文物数据
    const response = await axios.get('http://localhost:5000/api/cultural-relics');
    relics.value = response.data;
    
    // 提取所有分类和时期
    const allCategories = new Set(relics.value.map(relic => relic.category));
    categories.value = Array.from(allCategories);
    
    const allPeriods = new Set(relics.value.map(relic => relic.period));
    periods.value = Array.from(allPeriods);
    
    isLoading.value = false;
  } catch (err) {
    console.error('加载文物数据失败:', err);
    error.value = '加载文物数据失败，请稍后重试';
    isLoading.value = false;
  }
};

// 组件挂载时加载数据
onMounted(() => {
  loadRelics();
});
</script>

<style scoped>
.cultural-relic-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.loading-container, .error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 3px solid #42b983;
  border-top: 3px solid transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-container button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: #42b983;
  border: none;
  border-radius: 4px;
  color: white;
  cursor: pointer;
}

/* 过滤器样式 */
.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 2rem;
  background: #f5f5f5;
  padding: 1rem;
  border-radius: 8px;
}

.filter-group {
  display: flex;
  align-items: center;
}

.filter-group label {
  margin-right: 0.5rem;
  font-weight: bold;
  color: #555;
}

.filter-group select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
}

/* 文物网格样式 */
.relics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.relic-card {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  background: white;
  transition: transform 0.3s ease;
  cursor: pointer;
}

.relic-card:hover {
  transform: translateY(-5px);
}

.relic-image {
  height: 200px;
  overflow: hidden;
}

.relic-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.relic-card:hover .relic-image img {
  transform: scale(1.05);
}

.relic-content {
  padding: 1.5rem;
}

.relic-content h3 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
}

.relic-period {
  color: #666;
  font-style: italic;
  margin-bottom: 0.5rem;
}

.relic-location {
  color: #42b983;
  margin-bottom: 0.5rem;
}

.relic-category {
  display: inline-block;
  padding: 0.3rem 0.8rem;
  background: #f0f0f0;
  border-radius: 20px;
  font-size: 0.9rem;
  color: #666;
}

/* 详情弹窗样式 */
.detail-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  margin: 0;
  color: #2c3e50;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #666;
  cursor: pointer;
}

.modal-body {
  padding: 1.5rem;
  display: flex;
  flex-wrap: wrap;
}

.relic-detail-image {
  flex: 0 0 40%;
  margin-right: 2rem;
  margin-bottom: 1rem;
}

.relic-detail-image img {
  width: 100%;
  height: auto;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.relic-detail-info {
  flex: 1;
  min-width: 250px;
}

.info-row {
  margin-bottom: 1rem;
}

.info-label {
  font-weight: bold;
  color: #666;
  margin-right: 0.5rem;
}

.info-value {
  color: #2c3e50;
}

.info-row.description {
  margin-top: 1.5rem;
}

.info-row.description p {
  line-height: 1.6;
  margin-top: 0.5rem;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #eee;
  text-align: right;
}

.map-btn {
  padding: 0.7rem 1.2rem;
  background: #42b983;
  border: none;
  border-radius: 4px;
  color: white;
  cursor: pointer;
  transition: background 0.3s ease;
}

.map-btn:hover {
  background: #36a271;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .filters {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .modal-body {
    flex-direction: column;
  }
  
  .relic-detail-image {
    flex: 0 0 100%;
    margin-right: 0;
  }
}
</style> 