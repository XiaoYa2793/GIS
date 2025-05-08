<template>
  <div class="cultural-relics">
    <h1>北京文化遗产</h1>
    
    <div class="loading" v-if="loading">加载中...</div>
    <div class="error" v-if="error">{{ error }}</div>
    
    <div class="relics-container" v-if="!loading && !error">
      <div class="relic-card" v-for="relic in relics" :key="relic.id">
        <div class="relic-image">
          <img :src="getImageUrl(relic)" @error="handleImageError($event, relic)" :alt="relic.name">
        </div>
        <div class="relic-info">
          <h2>{{ relic.name }}</h2>
          <div class="relic-period">时期：{{ relic.period }}</div>
          <div class="relic-year" v-if="relic.year_range">年代：{{ relic.year_range }}</div>
          <div class="relic-location" v-if="relic.latitude && relic.longitude">
            位置：{{ relic.latitude.toFixed(4) }}, {{ relic.longitude.toFixed(4) }}
          </div>
          <div class="relic-description">{{ relic.description }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CulturalRelics',
  data() {
    return {
      relics: [],
      loading: true,
      error: null
    }
  },
  mounted() {
    this.fetchCulturalRelics()
  },
  methods: {
    async fetchCulturalRelics() {
      this.loading = true
      this.error = null
      
      try {
        console.log('开始获取文化遗产数据')
        const response = await fetch('http://localhost:5000/api/cultural-relics')
        const data = await response.json()
        
        if (data.status === 'success' && Array.isArray(data.data)) {
          this.relics = data.data
          console.log(`成功获取到${this.relics.length}个文化遗产数据`)
        } else {
          throw new Error(data.message || '获取文化遗产数据失败')
        }
      } catch (err) {
        console.error('获取文化遗产数据出错:', err)
        this.error = `获取文化遗产数据失败: ${err.message}`
      } finally {
        this.loading = false
      }
    },
    getImageUrl(relic) {
      if (!relic.image_path) {
        console.error(`文物 ${relic.name} 没有图片路径`)
        return 'https://via.placeholder.com/600x400?text=无图片'
      }
      
      if (relic.image_path.startsWith('http')) {
        return relic.image_path
      }
      
      return `http://localhost:5000${relic.image_path}`
    },
    handleImageError(event, relic) {
      console.error(`文物 ${relic.name} 图片加载失败: ${relic.image_path}`)
      event.target.src = `https://via.placeholder.com/600x400?text=${encodeURIComponent(relic.name)}`
    }
  }
}
</script>

<style scoped>
.cultural-relics {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
  font-size: 28px;
}

.loading, .error {
  text-align: center;
  padding: 20px;
  font-size: 18px;
}

.error {
  color: #e74c3c;
  background-color: #fef0f0;
  border-radius: 4px;
  padding: 15px;
}

.relics-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 30px;
}

.relic-card {
  background-color: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.relic-card:hover {
  transform: translateY(-5px);
}

.relic-image {
  width: 100%;
  height: 250px;
  overflow: hidden;
}

.relic-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.relic-card:hover .relic-image img {
  transform: scale(1.05);
}

.relic-info {
  padding: 20px;
}

.relic-info h2 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #333;
  font-size: 20px;
}

.relic-period, .relic-year, .relic-location {
  color: #666;
  font-size: 14px;
  margin-bottom: 8px;
}

.relic-description {
  color: #555;
  font-size: 16px;
  line-height: 1.5;
  margin-top: 10px;
}
</style> 