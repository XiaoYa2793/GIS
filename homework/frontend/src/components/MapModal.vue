<template>
  <div class="map-modal" v-if="visible" @click.self="close">
    <div class="modal-content">
      <div class="modal-header">
        <h3>{{ attraction?.name }}</h3>
        <button class="close-btn" @click="close">×</button>
      </div>
      <div id="container" class="map-container"></div>
      <div class="location-info">
        <i class="fas fa-map-marker-alt"></i>
        {{ attraction?.location }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue';

const props = defineProps({
  visible: Boolean,
  attraction: Object
});

const emit = defineEmits(['close']);

const close = () => {
  emit('close');
};

const initMap = () => {
  const container = document.getElementById('container');
  if (container && props.attraction) {
    // 使用景点的实际坐标
    const coordinates = props.attraction.coordinates || '116.397428,39.90923'; // 默认北京坐标
    const name = encodeURIComponent(props.attraction.name);
    container.innerHTML = `
      <iframe 
        src="https://uri.amap.com/marker?position=${coordinates}&name=${name}&src=mypage&coordinate=gaode&callnative=0"
        width="100%" 
        height="100%" 
        frameborder="0"
        scrolling="no"
      ></iframe>
    `;
  }
};

watch(() => props.visible, (newVal) => {
  if (newVal) {
    setTimeout(initMap, 100);
  }
});

onUnmounted(() => {
  const container = document.getElementById('container');
  if (container) {
    container.innerHTML = '';
  }
});
</script>

<style scoped>
.map-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: rgba(26, 31, 44, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  width: 90%;
  max-width: 800px;
  padding: 1.5rem;
  color: white;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 2rem;
  cursor: pointer;
  padding: 0.5rem;
  line-height: 1;
}

.close-btn:hover {
  color: #42b983;
}

.map-container {
  width: 100%;
  height: 400px;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 1rem;
  background: #fff;
}

.location-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: rgba(255, 255, 255, 0.8);
  padding: 0.5rem 0;
}

.location-info i {
  color: #42b983;
}
</style> 