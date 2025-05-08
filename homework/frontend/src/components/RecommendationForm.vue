<template>
  <div class="recommendation-form">
    <h2>
      <span class="form-title">创建景点推荐</span>
      <div class="title-underline"></div>
    </h2>
    
    <div class="form-group">
      <label for="title">
        <span class="label-icon">✍️</span>
        推荐标题
      </label>
      <input 
        id="title" 
        v-model="formData.title" 
        type="text" 
        placeholder="给您的推荐起个标题"
        class="form-control"
      />
    </div>
    
    <div class="form-group">
      <label for="description">
        <span class="label-icon">📝</span>
        推荐描述
      </label>
      <textarea 
        id="description" 
        v-model="formData.description" 
        placeholder="为何推荐这些景点？有什么特别之处？"
        class="form-control"
        rows="3"
      ></textarea>
    </div>
    
    <div class="form-group">
      <label>
        <span class="label-icon">🏮</span>
        选择景点
        <span class="selected-count" v-if="selectedAttractions.length > 0">
          已选择 {{ selectedAttractions.length }} 个景点
        </span>
      </label>
      <div class="attractions-list">
        <div 
          v-for="attraction in attractions" 
          :key="attraction.id"
          class="attraction-item"
          :class="{ selected: selectedAttractions.includes(attraction.id) }"
          @click="toggleAttraction(attraction.id)"
        >
          <div class="attraction-image">
            <img :src="getImageUrl(attraction)" :alt="attraction.name" />
            <div class="check-overlay" v-if="selectedAttractions.includes(attraction.id)">
              <span class="check-icon">✓</span>
            </div>
          </div>
          <div class="attraction-info">
            <h4>{{ attraction.name }}</h4>
            <div class="info-divider"></div>
            <p class="category">
              <span class="category-badge">{{ attraction.category || '景点' }}</span>
            </p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="form-actions">
      <button 
        class="submit-button" 
        @click="submitRecommendation"
        :disabled="!isFormValid || isSubmitting"
      >
        <span class="button-icon" v-if="!isSubmitting">✨</span>
        <span class="loading-icon" v-else></span>
        {{ isSubmitting ? '创建中...' : '创建推荐' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const formData = ref({
  title: '',
  description: '',
})

const attractions = ref([])
const selectedAttractions = ref([])
const isSubmitting = ref(false)

const isFormValid = computed(() => {
  return formData.value.title.trim() !== '' && selectedAttractions.value.length > 0
})

const getImageUrl = (attraction) => {
  if (!attraction.image_path) return null
  return `http://localhost:5000${attraction.image_path}`
}

const toggleAttraction = (id) => {
  const index = selectedAttractions.value.indexOf(id)
  if (index === -1) {
    selectedAttractions.value.push(id)
  } else {
    selectedAttractions.value.splice(index, 1)
  }
}

const fetchAttractions = async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/attractions')
    attractions.value = response.data
  } catch (error) {
    console.error('获取景点列表失败:', error)
    ElMessage.error('获取景点列表失败')
  }
}

const submitRecommendation = async () => {
  if (!isFormValid.value) return
  
  isSubmitting.value = true
  
  try {
    const response = await axios.post('http://localhost:5000/api/recommendations', {
      title: formData.value.title,
      description: formData.value.description,
      attractions: selectedAttractions.value
    })
    
    ElMessage.success('景点推荐创建成功！')
    
    // 触发创建成功事件，传递推荐ID
    emit('created', response.data.id)
    
    // 重置表单
    formData.value.title = ''
    formData.value.description = ''
    selectedAttractions.value = []
  } catch (error) {
    console.error('创建推荐失败:', error)
    ElMessage.error('创建推荐失败，请重试')
  } finally {
    isSubmitting.value = false
  }
}

const emit = defineEmits(['created'])

onMounted(() => {
  fetchAttractions()
})
</script>

<style scoped>
.recommendation-form {
  max-width: 800px;
  margin: 0 auto;
  padding: 30px;
  background: rgba(18, 24, 38, 0.8);
  border-radius: 16px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  position: relative;
  overflow: hidden;
}

.recommendation-form::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background: linear-gradient(90deg, #42b983, #67c6ff, #a78bfa);
}

h2 {
  text-align: center;
  margin-bottom: 30px;
  position: relative;
  display: inline-block;
  width: 100%;
}

.form-title {
  font-size: 2rem;
  font-weight: 700;
  background: linear-gradient(120deg, #42b983, #67c6ff);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.title-underline {
  height: 5px;
  width: 100px;
  background: linear-gradient(90deg, #42b983, #67c6ff);
  border-radius: 4px;
  margin: 10px auto 0;
}

.form-group {
  margin-bottom: 25px;
}

label {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  font-weight: 500;
  color: white;
  font-size: 1.1rem;
}

.label-icon {
  margin-right: 8px;
  font-size: 1.2rem;
}

.selected-count {
  margin-left: auto;
  font-size: 0.9rem;
  font-weight: normal;
  color: rgba(255, 255, 255, 0.7);
  background: rgba(66, 185, 131, 0.2);
  padding: 3px 10px;
  border-radius: 20px;
}

.form-control {
  width: 100%;
  padding: 12px 15px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  font-size: 1rem;
  color: white;
  transition: all 0.3s;
}

.form-control:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(66, 185, 131, 0.5);
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.2);
}

.form-control::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.attractions-list {
  max-height: 400px;
  overflow-y: auto;
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.1);
  padding: 5px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 10px;
}

.attraction-item {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.attraction-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
  background: rgba(255, 255, 255, 0.08);
}

.attraction-item.selected {
  background: rgba(66, 185, 131, 0.2);
  border-color: rgba(66, 185, 131, 0.4);
  box-shadow: 0 0 15px rgba(66, 185, 131, 0.3);
}

.attraction-image {
  height: 140px;
  overflow: hidden;
  position: relative;
}

.attraction-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s;
}

.attraction-item:hover .attraction-image img {
  transform: scale(1.05);
}

.check-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(66, 185, 131, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.check-icon {
  font-size: 2rem;
  color: white;
  filter: drop-shadow(0 0 3px rgba(0, 0, 0, 0.3));
}

.attraction-info {
  padding: 15px;
}

.attraction-info h4 {
  margin: 0;
  font-size: 1rem;
  color: white;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.info-divider {
  height: 2px;
  width: 30px;
  background: linear-gradient(90deg, #42b983, #67c6ff);
  margin: 8px 0;
  border-radius: 2px;
}

.category-badge {
  display: inline-block;
  padding: 3px 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  font-size: 0.7rem;
}

.form-actions {
  margin-top: 30px;
  text-align: center;
}

.submit-button {
  padding: 12px 35px;
  background: linear-gradient(135deg, #42b983, #34d399);
  color: white;
  border: none;
  border-radius: 50px;
  font-size: 1.1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow: 0 4px 15px rgba(66, 185, 131, 0.4);
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(66, 185, 131, 0.5);
}

.submit-button:disabled {
  background: rgba(255, 255, 255, 0.1);
  cursor: not-allowed;
  box-shadow: none;
}

.button-icon {
  font-size: 1.2rem;
}

.loading-icon {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 滚动条美化 */
.attractions-list::-webkit-scrollbar {
  width: 6px;
  display: block;
}

.attractions-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.attractions-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.attractions-list::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

@media (max-width: 768px) {
  .attractions-list {
    grid-template-columns: 1fr;
  }
  
  .form-title {
    font-size: 1.6rem;
  }
}
</style> 