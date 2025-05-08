<template>
  <div class="qrcode-modal" v-if="visible">
    <div class="qrcode-content">
      <div class="qrcode-header">
        <div class="header-decoration"></div>
        <h3>{{ title }}</h3>
        <p v-if="description">{{ description }}</p>
      </div>
      
      <div class="qrcode-container">
        <div class="qrcode-frame">
          <qrcode-vue :value="shareUrl" :size="200" level="H" />
          <div class="corner top-left"></div>
          <div class="corner top-right"></div>
          <div class="corner bottom-left"></div>
          <div class="corner bottom-right"></div>
        </div>
      </div>
      
      <div class="qrcode-url">
        <p class="url-label">链接地址：</p>
        <div class="url-box">
          <span class="url-text">{{ shareUrl }}</span>
          <button class="copy-btn" @click="copyUrl" title="复制链接">
            <span class="copy-icon">📋</span>
          </button>
        </div>
      </div>
      
      <div class="qrcode-footer">
        <p class="qrcode-tip">
          <span class="tip-icon">📱</span>
          扫描二维码查看推荐景点
        </p>
        <div class="qrcode-actions">
          <button class="download-btn" @click="downloadQRCode">
            <span class="btn-icon">💾</span>
            保存二维码
          </button>
          <button class="close-btn" @click="$emit('close')">
            <span class="btn-icon">✖️</span>
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import QrcodeVue from 'qrcode.vue'

const props = defineProps({
  visible: Boolean,
  recommendationId: [Number, String],
  title: String,
  description: String
})

// 修改备用IP地址为实际检测到的IP地址
const localIp = ref('192.168.3.71');  // 使用正确的IP地址

// 获取本机IP地址
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
  
  // 使用format=html参数，确保手机扫码后可以直接查看格式化的HTML页面
  const url = `${serverUrl}/recommendation/${props.recommendationId}?format=html`;
  console.log('生成的二维码URL:', url);
  return url;
})

const downloadQRCode = () => {
  const canvas = document.querySelector('.qrcode-container canvas')
  if (canvas) {
    const link = document.createElement('a')
    link.download = `${props.title || '景点推荐'}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
  }
}

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
.qrcode-modal {
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

.qrcode-content {
  background: rgba(18, 24, 38, 0.95);
  padding: 30px;
  border-radius: 16px;
  text-align: center;
  max-width: 450px;
  width: 90%;
  color: white;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  animation: slideUp 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
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

.qrcode-header {
  margin-bottom: 25px;
  position: relative;
  padding-bottom: 15px;
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

.qrcode-header h3 {
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

.qrcode-header p {
  margin: 0;
  color: rgba(255, 255, 255, 0.7);
  font-size: 1rem;
  max-width: 350px;
  margin: 0 auto;
}

.qrcode-container {
  margin: 25px 0;
  display: flex;
  justify-content: center;
}

.qrcode-frame {
  background: white;
  padding: 20px;
  border-radius: 12px;
  position: relative;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.qrcode-url {
  margin: 15px 0;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 10px 15px;
}

.url-label {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
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
  color: #42b983;
  cursor: pointer;
  padding: 5px;
  margin-left: 8px;
  border-radius: 4px;
  transition: all 0.2s;
}

.copy-btn:hover {
  background: rgba(66, 185, 131, 0.2);
}

.copy-icon {
  font-size: 1.1rem;
}

.corner {
  position: absolute;
  width: 20px;
  height: 20px;
  border-color: #42b983;
  border-style: solid;
  border-width: 0;
}

.top-left {
  top: 5px;
  left: 5px;
  border-top-width: 2px;
  border-left-width: 2px;
  border-top-left-radius: 5px;
}

.top-right {
  top: 5px;
  right: 5px;
  border-top-width: 2px;
  border-right-width: 2px;
  border-top-right-radius: 5px;
}

.bottom-left {
  bottom: 5px;
  left: 5px;
  border-bottom-width: 2px;
  border-left-width: 2px;
  border-bottom-left-radius: 5px;
}

.bottom-right {
  bottom: 5px;
  right: 5px;
  border-bottom-width: 2px;
  border-right-width: 2px;
  border-bottom-right-radius: 5px;
}

.qrcode-footer {
  margin-top: 20px;
}

.qrcode-tip {
  color: rgba(255, 255, 255, 0.8);
  margin: 15px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.tip-icon {
  font-size: 1.2rem;
}

.qrcode-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 20px;
}

.download-btn, .close-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 500;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-icon {
  font-size: 1.1rem;
}

.download-btn {
  background: linear-gradient(135deg, #42b983, #34d399);
  color: white;
  box-shadow: 0 4px 15px rgba(66, 185, 131, 0.4);
}

.close-btn {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.download-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(66, 185, 131, 0.5);
}

.close-btn:hover {
  transform: translateY(-3px);
  background: rgba(255, 255, 255, 0.15);
}

@media (max-width: 480px) {
  .qrcode-content {
    padding: 20px;
  }
  
  .qrcode-header h3 {
    font-size: 1.5rem;
  }
  
  .qrcode-actions {
    flex-direction: column;
    gap: 10px;
  }
  
  .download-btn, .close-btn {
    width: 100%;
  }
}
</style> 