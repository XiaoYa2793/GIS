<template>
  <div class="inline-frame-container" v-if="visible">
    <div class="frame-overlay" @click="close"></div>
    <div class="frame-modal">
      <div class="frame-header">
        <div class="site-info">
          <i class="fas fa-globe"></i>
          <span class="site-url">{{ displayUrl }}</span>
        </div>
        <div class="frame-controls">
          <button class="reload-btn" @click="reload" title="刷新">
            <i class="fas fa-sync-alt"></i>
          </button>
          <button class="open-btn" @click="openExternal" title="在新窗口打开">
            <i class="fas fa-external-link-alt"></i>
          </button>
          <button class="close-btn" @click="close" title="关闭">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
      
      <div class="frame-content" :class="{ 'loading': loading }">
        <div class="loading-overlay" v-if="loading">
          <div class="spinner"></div>
          <p>加载中...</p>
        </div>
        <iframe 
          ref="frameRef" 
          :src="url" 
          @load="onFrameLoad"
          frameborder="0"
          allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen
        ></iframe>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  url: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(['close', 'update:visible']);

const frameRef = ref(null);
const loading = ref(true);

const displayUrl = computed(() => {
  try {
    const url = new URL(props.url);
    return url.hostname + url.pathname;
  } catch (e) {
    return props.url;
  }
});

const close = () => {
  emit('update:visible', false);
  emit('close');
};

const reload = () => {
  if (frameRef.value) {
    loading.value = true;
    frameRef.value.src = props.url;
  }
};

const openExternal = () => {
  window.open(props.url, '_blank');
};

const onFrameLoad = () => {
  loading.value = false;
};

watch(() => props.url, () => {
  loading.value = true;
});

watch(() => props.visible, (newValue) => {
  if (newValue && frameRef.value && props.url) {
    // 当显示时重新加载内容
    reload();
  }
});

onMounted(() => {
  // 处理ESC键关闭
  const handleKeyDown = (e) => {
    if (e.key === 'Escape' && props.visible) {
      close();
    }
  };
  
  window.addEventListener('keydown', handleKeyDown);
  
  return () => {
    window.removeEventListener('keydown', handleKeyDown);
  };
});
</script>

<style scoped>
.inline-frame-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.frame-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(3px);
}

.frame-modal {
  position: relative;
  width: 90%;
  height: 90%;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 5px 25px rgba(0, 0, 0, 0.3);
  animation: frame-appear 0.3s ease forwards;
}

.frame-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
  height: 50px;
}

.site-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #333;
  font-size: 0.9rem;
  max-width: 70%;
  overflow: hidden;
}

.site-url {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.frame-controls {
  display: flex;
  gap: 8px;
}

.frame-controls button {
  background: transparent;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.frame-controls button:hover {
  background: rgba(0, 0, 0, 0.1);
}

.reload-btn, .open-btn {
  color: #555;
}

.close-btn {
  color: #ff5252;
}

.frame-content {
  flex: 1;
  position: relative;
  background: #fff;
}

.frame-content iframe {
  width: 100%;
  height: 100%;
  border: none;
  display: block;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  z-index: 10;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #42b983;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes frame-appear {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@media (max-width: 768px) {
  .frame-modal {
    width: 100%;
    height: 100%;
    border-radius: 0;
  }
  
  .site-info {
    font-size: 0.8rem;
  }
}
</style> 