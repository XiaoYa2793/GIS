<template>
  <div class="share-modal" v-if="visible">
    <div class="share-content">
      <h3>分享景点</h3>
      <div class="qrcode-container">
        <qrcode-vue :value="shareUrl" :size="200" level="H" />
      </div>
      <div class="url-section">
        <p class="url-label">链接地址：</p>
        <div class="url-box">
          <span class="url-text">{{ shareUrl }}</span>
          <button class="copy-btn" @click="copyUrl" title="复制链接">📋</button>
        </div>
      </div>
      <p class="share-tip">扫描二维码查看景点详情</p>
      <button class="close-btn" @click="$emit('close')">关闭</button>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import QrcodeVue from 'qrcode.vue'

const props = defineProps({
  visible: Boolean,
  attractionId: String,
  attractionName: String
})

// 修改备用IP地址为实际检测到的IP地址
const localIp = ref('192.168.3.71');  // 使用正确的IP地址

// 获取本机IP地址函数可以保留，但默认值更新为实际IP
const detectLocalIp = async () => {
  try {
    const response = await fetch('https://api.ipify.org?format=json');
    const data = await response.json();
    // 如果获取到公网IP成功，使用公网IP
    if (data && data.ip) {
      localIp.value = data.ip;
      console.log('检测到的公网IP:', localIp.value);
    }
  } catch (error) {
    console.error('获取公网IP地址失败，使用本地IP:', error);
    // 继续使用初始设置的本地IP
  }
};

onMounted(() => {
  detectLocalIp();
});

// 修改shareUrl计算属性
const shareUrl = computed(() => {
  // 优先使用环境变量中配置的公共API URL
  let serverUrl = import.meta.env.VITE_PUBLIC_API_URL;
  
  // 如果没有配置环境变量，使用本地IP
  if (!serverUrl) {
    serverUrl = localIp.value;
  }
  
  // 添加协议
  if (!serverUrl.startsWith('http')) {
    serverUrl = `http://${serverUrl}`;
  }
  
  // 添加端口(后端服务端口)
  if (!serverUrl.includes(':') && !serverUrl.includes('.com')) {
    serverUrl = `${serverUrl}:5000`;
  }
  
  // 添加format=html参数，确保手机扫码后可以直接查看格式化的HTML页面
  const url = `${serverUrl}/attraction/${props.attractionId}?format=html`;
  console.log('生成的二维码URL:', url);
  return url;
})

const copyUrl = () => {
  navigator.clipboard.writeText(shareUrl.value)
    .then(() => {
      alert('链接已复制到剪贴板');
    })
    .catch(err => {
      console.error('复制失败:', err);
    });
}

defineEmits(['close'])
</script>

<style scoped>
.share-modal {
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
}

.share-content {
  background: rgba(18, 24, 38, 0.95);
  padding: 25px;
  border-radius: 15px;
  text-align: center;
  max-width: 350px;
  width: 90%;
  color: white;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
}

.qrcode-container {
  margin: 20px 0;
  background: white;
  padding: 15px;
  border-radius: 12px;
  display: inline-block;
}

.url-section {
  margin: 15px 0;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 10px;
}

.url-label {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 5px;
  text-align: left;
}

.url-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 6px;
  padding: 8px 12px;
}

.url-text {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.9);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  text-align: left;
}

.copy-btn {
  background: none;
  border: none;
  color: #4CAF50;
  cursor: pointer;
  font-size: 1.1rem;
  padding: 5px;
  margin-left: 8px;
  border-radius: 4px;
  transition: all 0.2s;
}

.copy-btn:hover {
  background: rgba(76, 175, 80, 0.2);
}

.share-tip {
  color: rgba(255, 255, 255, 0.8);
  margin: 15px 0;
}

.close-btn {
  padding: 10px 25px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}

.close-btn:hover {
  background: #45a049;
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
}

@media (max-width: 480px) {
  .share-content {
    padding: 20px;
  }
}
</style> 