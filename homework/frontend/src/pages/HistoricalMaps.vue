<template>
  <div class="historical-maps">
    <h1>北京历史地图</h1>
    
    <div class="loading" v-if="loading">加载中...</div>
    <div class="error" v-if="error">{{ error }}</div>
    
    <div class="maps-container" v-if="!loading && !error">
      <div class="map-card" v-for="map in maps" :key="map.id">
        <div class="map-image">
          <img :src="getImageUrl(map)" @error="handleImageError($event, map)" :alt="map.name">
        </div>
        <div class="map-info">
          <h2>{{ map.name }}</h2>
          <div class="map-period">时期：{{ map.period }} ({{ map.year_range }})</div>
          <div class="map-description">{{ map.description }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HistoricalMaps',
  data() {
    return {
      maps: [],
      loading: true,
      error: null
    }
  },
  mounted() {
    this.fetchHistoricalMaps()
  },
  methods: {
    async fetchHistoricalMaps() {
      this.loading = true
      this.error = null
      
      try {
        console.log('开始获取历史地图数据')
        const response = await fetch('http://localhost:5000/api/historical-maps')
        const data = await response.json()
        
        if (data.status === 'success' && Array.isArray(data.data)) {
          this.maps = data.data
          console.log(`成功获取到${this.maps.length}个历史地图数据`)
        } else {
          throw new Error(data.message || '获取历史地图数据失败')
        }
      } catch (err) {
        console.error('获取历史地图数据出错:', err)
        this.error = `获取历史地图数据失败: ${err.message}`
      } finally {
        this.loading = false
      }
    },
    getImageUrl(map) {
      if (!map.image_path) {
        console.error(`地图 ${map.name} 没有图片路径`)
        return 'https://via.placeholder.com/600x400?text=无图片'
      }
      
      if (map.image_path.startsWith('http')) {
        return map.image_path
      }
      
      return `http://localhost:5000${map.image_path}`
    },
    handleImageError(event, map) {
      console.error(`地图 ${map.name} 图片加载失败: ${map.image_path}`)
      event.target.src = `https://via.placeholder.com/600x400?text=${encodeURIComponent(map.name)}`
    }
  }
}
</script>

<style scoped>
.historical-maps {
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

.maps-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 30px;
}

.map-card {
  background-color: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.map-card:hover {
  transform: translateY(-5px);
}

.map-image {
  width: 100%;
  height: 250px;
  overflow: hidden;
}

.map-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.map-card:hover .map-image img {
  transform: scale(1.05);
}

.map-info {
  padding: 20px;
}

.map-info h2 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #333;
  font-size: 20px;
}

.map-period {
  color: #666;
  font-size: 14px;
  margin-bottom: 10px;
}

.map-description {
  color: #555;
  font-size: 16px;
  line-height: 1.5;
}
</style> 