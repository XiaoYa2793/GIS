<template>
  <div class="panorama-modal" v-if="visible" @click.self="close">
    <div class="modal-content">
      <div class="modal-header">
        <h3>故宫全景游览</h3>
        <button class="close-btn" @click="close">×</button>
      </div>
      <div class="panorama-container">
        <div v-if="loading" class="loading">
          <div class="spinner"></div>
          <p>正在准备跳转至故宫全景网站...</p>
        </div>
        <div v-else-if="error" class="error">
          <p>{{ error }}</p>
          <button class="retry-btn" @click="redirectToPanoramaSite">重试</button>
        </div>
        <div v-else class="panorama-content">
          <div class="redirect-message">
            <h2>即将前往故宫博物院全景网站</h2>
            <p>故宫博物院提供精美的3D全景浏览体验，让您在家也能游览故宫的壮丽建筑。</p>
            <div class="button-group">
              <button class="redirect-btn primary" @click="redirectToPanoramaSite">
                <i class="fas fa-external-link-alt"></i> 立即前往
              </button>
              <button class="redirect-btn secondary" @click="close">
                稍后再说
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import axios from 'axios';

const props = defineProps({
  visible: Boolean
});

const emit = defineEmits(['close']);
const loading = ref(true);
const error = ref(null);

// 故宫全景网站URL
const panoramaUrl = 'https://pano.dpm.org.cn/#/';

// 自动跳转功能
const redirectToPanoramaSite = async () => {
  try {
    console.log('准备跳转至故宫全景网站');
    
    // 先从后端获取重定向链接
    const response = await axios.get('http://localhost:5000/api/redirect/gugong-panorama');
    
    if (response.data && response.data.status === 'success') {
      const redirectUrl = response.data.redirect_url || panoramaUrl;
      console.log('获取到重定向URL:', redirectUrl);
      
      // 在新窗口打开链接
      window.open(redirectUrl, '_blank');
      
      // 延迟关闭模态框，使用户体验更好
      setTimeout(() => {
        close();
      }, 500);
    } else {
      console.error('获取重定向链接失败:', response.data);
      // 使用默认URL作为备选
      window.open(panoramaUrl, '_blank');
      setTimeout(() => {
        close();
      }, 500);
    }
  } catch (e) {
    console.error('跳转失败:', e);
    error.value = '跳转失败，请检查网络连接或浏览器设置';
    
    // 仍然尝试使用默认URL
    try {
      window.open(panoramaUrl, '_blank');
      setTimeout(() => {
        close();
      }, 500);
    } catch (innerError) {
      console.error('使用默认URL也失败:', innerError);
      error.value = '跳转失败，请检查浏览器是否阻止了弹出窗口';
    }
  }
};

// 初始化函数
const init = () => {
  loading.value = true;
  error.value = null;
  
  console.log('准备跳转至故宫全景网站...');
  
  // 模拟延迟，让加载状态显示一会儿
  setTimeout(() => {
    loading.value = false;
  }, 800);
};

// 关闭全景图
const close = () => {
  emit('close');
};

// 监听可见性变化
watch(() => props.visible, (newVal) => {
  if (newVal) {
    init();
  }
});
</script>

<style scoped>
.panorama-modal {
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
  background: rgba(26, 31, 44, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  width: 95%;
  max-width: 700px;
  min-height: 300px;
  padding: 1.5rem;
  color: white;
  display: flex;
  flex-direction: column;
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

.panorama-container {
  flex: 1;
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.panorama-content {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.redirect-message {
  text-align: center;
}

.redirect-message h2 {
  margin-bottom: 1rem;
  color: #42b983;
}

.redirect-message p {
  margin-bottom: 2rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.9);
}

.button-group {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

.redirect-btn {
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.3s ease;
  border: none;
}

.redirect-btn.primary {
  background-color: #42b983;
  color: white;
}

.redirect-btn.primary:hover {
  background-color: #3aa876;
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(66, 185, 131, 0.3);
}

.redirect-btn.secondary {
  background-color: transparent;
  border: 1px solid rgba(255, 255, 255, 0.5);
  color: white;
}

.redirect-btn.secondary:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.loading, .error {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: rgba(0, 0, 0, 0.8);
  color: white;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 3px solid #42b983;
  border-top: 3px solid transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.retry-btn {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: #42b983;
  border: none;
  border-radius: 4px;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s;
}

.retry-btn:hover {
  background: #3aa876;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style> 