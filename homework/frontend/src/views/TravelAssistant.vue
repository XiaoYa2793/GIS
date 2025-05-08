<template>
  <div class="travel-assistant">
    <div class="chat-container">
      <!-- 侧边栏 -->
      <aside class="sidebar" :class="{ 'collapsed': sidebarCollapsed }">
        <h2>旅行对话</h2>
        <button @click="createNewTopic" class="new-topic-btn">➕ 新话题</button>
        <ul class="chat-list">
          <li
            v-for="topic in topics"
            :key="topic.id"
            :class="{ active: topic.id === activeTopicId }"
            @click="switchTopic(topic.id)"
          >
            <span>{{ topic.name }}</span>
            <button class="delete-btn" @click.stop="clearTopicMessages(topic.id)">🗑️</button>
          </li>
        </ul>
        
        <!-- 侧边栏切换按钮 -->
        <button class="toggle-sidebar" @click="toggleSidebar">
          <i :class="sidebarCollapsed ? 'fas fa-chevron-right' : 'fas fa-chevron-left'"></i>
        </button>
      </aside>

      <!-- 主聊天区域 -->
      <main class="chat-main" :class="{ 'expanded': sidebarCollapsed }">
        <header class="chat-header">
          <strong>旅行助手 TravelBot</strong>
          <div class="user-section">
            <img :src="userAvatar" alt="用户头像" class="avatar" />
            <label for="upload-avatar" class="upload-label">更换头像</label>
            <input id="upload-avatar" type="file" accept="image/*" @change="onAvatarUpload" hidden />
          </div>
        </header>

        <section class="chat-box" ref="chatBox">
          <!-- 欢迎消息 -->
          <div v-if="currentMessages.length === 0" class="welcome-message">
            <h3>欢迎使用旅行助手！</h3>
            <p>您可以询问我关于北京旅游的任何问题，例如：</p>
            <ul>
              <li>北京有哪些著名景点？</li>
              <li>故宫的参观攻略是什么？</li>
              <li>如何前往颐和园？</li>
              <li>北京的美食推荐</li>
            </ul>
          </div>
          
          <div
            v-for="(msg, index) in currentMessages"
            :key="index"
            :class="['chat-message', msg.role]"
          >
            <img
              class="avatar"
              :src="msg.role === 'user' ? userAvatar : botAvatar"
              :alt="msg.role"
            />
            <div class="bubble" v-html="formatMessage(msg.text)"></div>
          </div>
          
          <div v-if="loading" class="loading-indicator">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
          </div>
        </section>

        <footer class="chat-input">
          <input
            type="text"
            v-model="userInput"
            placeholder="告诉我你的旅行需求，我会为你提供帮助..."
            @keydown.enter="sendMessage"
            :disabled="loading"
          />
          <button @click="sendMessage" :disabled="loading" class="send-btn">
            <i class="fas fa-paper-plane"></i>
          </button>
        </footer>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed, watch } from 'vue';
import axios from 'axios';

// 状态变量
const userAvatar = ref(localStorage.getItem('user_avatar') || 'https://cdn-icons-png.flaticon.com/512/1077/1077114.png');
const botAvatar = ref('https://cdn-icons-png.flaticon.com/512/4712/4712109.png');
const topics = ref(JSON.parse(localStorage.getItem('chat_topics')) || []);
const activeTopicId = ref(localStorage.getItem('active_topic_id') || '');
const userInput = ref('');
const currentMessages = ref([]);
const chatBox = ref(null);
const loading = ref(false);
const sidebarCollapsed = ref(localStorage.getItem('travel_sidebar_collapsed') === 'true');

// 切换侧边栏展开/收起
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value;
  localStorage.setItem('travel_sidebar_collapsed', sidebarCollapsed.value);
};

// 创建新话题
const createNewTopic = () => {
  const topicName = `旅行计划 ${new Date().toLocaleDateString()}`;
  const newTopic = {
    id: 'topic_' + Date.now(),
    name: topicName,
    messages: []
  };
  topics.value.push(newTopic);
  activeTopicId.value = newTopic.id;
  saveTopics();
  loadMessages(newTopic.id);
};

// 切换话题
const switchTopic = (topicId) => {
  activeTopicId.value = topicId;
  saveTopics();
  loadMessages(topicId);
};

// 加载当前话题的消息
const loadMessages = (topicId) => {
  const topic = topics.value.find(t => t.id === topicId);
  currentMessages.value = topic ? [...topic.messages] : [];
  nextTick(() => {
    scrollToBottom();
  });
};

// 发送消息
const sendMessage = async () => {
  const message = userInput.value.trim();
  if (!message || loading.value) return;
  
  appendMessage('user', message);
  userInput.value = '';
  loading.value = true;
  
  try {
    // 模拟API请求延迟
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // 这里是模拟回复，实际项目中应该调用真实的API
    const botResponse = generateBotResponse(message);
    appendMessage('bot', botResponse);
  } catch (error) {
    console.error('消息发送失败:', error);
    appendMessage('bot', '很抱歉，我暂时无法回应您的问题。请稍后再试。');
  } finally {
    loading.value = false;
  }
};

// 添加消息到当前话题
const appendMessage = (role, text) => {
  const topic = topics.value.find(t => t.id === activeTopicId.value);
  if (topic) {
    topic.messages.push({ role, text });
    saveTopics();
    currentMessages.value = [...topic.messages];
    nextTick(() => {
      scrollToBottom();
    });
  }
};

// 清空/删除话题
const clearTopicMessages = (topicId) => {
  const index = topics.value.findIndex(t => t.id === topicId);
  if (index !== -1) {
    topics.value.splice(index, 1);
    if (topicId === activeTopicId.value) {
      activeTopicId.value = topics.value.length ? topics.value[0].id : '';
      if (!activeTopicId.value) createNewTopic();
      else loadMessages(activeTopicId.value);
    }
    saveTopics();
  }
};

// 保存话题到本地存储
const saveTopics = () => {
  localStorage.setItem('chat_topics', JSON.stringify(topics.value));
  localStorage.setItem('active_topic_id', activeTopicId.value);
};

// 滚动到底部
const scrollToBottom = () => {
  if (chatBox.value) {
    chatBox.value.scrollTop = chatBox.value.scrollHeight;
  }
};

// 头像上传处理
const onAvatarUpload = (event) => {
  const file = event.target.files[0];
  if (!file) return;
  
  const reader = new FileReader();
  reader.onload = (e) => {
    userAvatar.value = e.target.result;
    localStorage.setItem('user_avatar', userAvatar.value);
  };
  reader.readAsDataURL(file);
};

// 格式化消息内容（支持简单的Markdown语法）
const formatMessage = (text) => {
  if (!text) return '';
  
  // 替换链接
  let formattedText = text.replace(
    /(https?:\/\/[^\s]+)/g, 
    '<a href="$1" target="_blank" rel="noopener">$1</a>'
  );
  
  // 替换*加粗*文本
  formattedText = formattedText.replace(
    /\*(.*?)\*/g, 
    '<strong>$1</strong>'
  );
  
  // 替换_斜体_文本
  formattedText = formattedText.replace(
    /_(.*?)_/g, 
    '<em>$1</em>'
  );
  
  // 替换换行符
  formattedText = formattedText.replace(/\n/g, '<br>');
  
  return formattedText;
};

// 生成机器人回复（模拟）
const generateBotResponse = (message) => {
  const lowerMsg = message.toLowerCase();
  
  if (lowerMsg.includes('你好') || lowerMsg.includes('嗨') || lowerMsg.includes('hi') || lowerMsg.includes('hello')) {
    return '你好！我是北京旅游助手，很高兴为你提供帮助。请问你有什么旅行计划或问题呢？';
  }
  
  if (lowerMsg.includes('景点') || lowerMsg.includes('去哪玩') || lowerMsg.includes('推荐')) {
    return '北京有许多著名景点，包括：\n\n1. *故宫博物院* - 中国明清两代的皇家宫殿\n2. *长城* - 八达岭、慕田峪和司马台段最为著名\n3. *颐和园* - 保存最完整的皇家园林\n4. *天坛* - 明清两代帝王祭天的场所\n5. *北海公园* - 有着悠久历史的皇家园林\n\n你对哪个景点最感兴趣？我可以提供更详细的信息。';
  }
  
  if (lowerMsg.includes('故宫') || lowerMsg.includes('紫禁城')) {
    return '*故宫参观攻略*：\n\n- 开放时间：8:30-16:30（周一闭馆）\n- 门票价格：60元（旺季），40元（淡季）\n- 建议游览路线：午门 → 太和殿 → 中和殿 → 保和殿 → 乾清宫 → 交泰殿 → 坤宁宫 → 御花园 → 神武门\n- 小贴士：故宫很大，建议预留一整天时间，穿舒适的鞋子，带足水和食物。';
  }
  
  if (lowerMsg.includes('长城')) {
    return '北京周边的长城主要有八达岭、慕田峪、司马台、箭扣等多个段落。\n\n*八达岭长城*是最受欢迎的，交通便利但游客较多；\n*慕田峪长城*风景优美，适合徒步；\n*司马台长城*保存了原始风貌，还有夜游项目；\n*箭扣长城*较为险峻，适合有徒步经验的游客。\n\n你想了解哪一段长城的详细信息？';
  }
  
  if (lowerMsg.includes('美食') || lowerMsg.includes('吃什么')) {
    return '北京的传统美食非常丰富！以下是一些推荐：\n\n1. *北京烤鸭* - 全聚德、大董、便宜坊都是不错的选择\n2. *炸酱面* - 老北京的传统面食\n3. *豆汁* - 特色小吃，味道独特\n4. *驴打滚* - 甜品，由黄米面、豆沙、黄豆粉制作\n5. *爆肚* - 涮羊肚，配以特制蘸料\n\n此外，北京的胡同里还有很多隐藏的美食小店，值得探索！';
  }
  
  if (lowerMsg.includes('交通') || lowerMsg.includes('怎么去')) {
    return '北京的公共交通非常便利，主要有以下几种方式：\n\n1. *地铁* - 覆盖面广，是游览城市的最佳选择\n2. *公交车* - 线路丰富，但可能受到交通拥堵影响\n3. *出租车* - 方便但费用较高，高峰期可能难打车\n4. *共享单车* - 适合短距离出行，在景区周边很方便\n\n建议下载"高德地图"或"百度地图"APP，可以提供实时的公交和地铁路线规划。';
  }
  
  if (lowerMsg.includes('住宿') || lowerMsg.includes('酒店') || lowerMsg.includes('住哪')) {
    return '北京的住宿区域推荐：\n\n1. *王府井/东单* - 市中心位置，购物方便，交通便利\n2. *西单* - 商业区，靠近金融街\n3. *三里屯/朝阳区* - 时尚区域，夜生活丰富\n4. *后海/南锣鼓巷* - 老北京胡同风情，文艺范十足\n5. *北京站/北京西站附近* - 交通枢纽，适合中转游客\n\n根据你的预算和喜好，你更倾向于哪一类住宿？';
  }
  
  if (lowerMsg.includes('预算') || lowerMsg.includes('花费') || lowerMsg.includes('多少钱')) {
    return '北京旅游的预算参考（每人每天）：\n\n- *经济型*：300-500元（含住宿、餐饮和交通）\n- *中档*：500-1000元（含较好的住宿和餐饮）\n- *高端*：1000元以上（含高档酒店和特色餐厅）\n\n主要景点门票参考：\n- 故宫：60元（旺季）\n- 长城（八达岭）：40元\n- 颐和园：30元\n- 天坛：15元\n\n北京的交通费用相对便宜，地铁基本在3-8元之间，公交车大多在1-2元。';
  }
  
  // 默认回复
  return '感谢您的问题！作为北京旅游助手，我很乐意为您提供关于北京旅游的信息。您可以询问我关于景点推荐、美食、交通、住宿或旅行规划的问题。如果您有特定的需求，请告诉我，我会尽力提供帮助。';
};

// 组件挂载时初始化
onMounted(() => {
  if (!activeTopicId.value || topics.value.length === 0) {
    createNewTopic();
  } else {
    loadMessages(activeTopicId.value);
  }
});

// 监听消息变化，自动滚动到底部
watch(currentMessages, () => {
  nextTick(() => {
    scrollToBottom();
  });
});
</script>

<style scoped>
.travel-assistant {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-family: 'Segoe UI', Arial, sans-serif;
  color: #333;
}

.chat-container {
  width: 95%;
  height: 94%;
  display: flex;
  flex-direction: row;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

/* 侧边栏样式 */
.sidebar {
  width: 240px;
  flex-shrink: 0;
  background: rgba(26, 31, 44, 0.8);
  color: white;
  /* padding: 20px; */
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  position: relative;
  transition: all 0.3s ease;
}

/* 收起时的侧边栏样式 */
.sidebar.collapsed {
  width: 60px;
  padding: 20px 10px;
}

.sidebar.collapsed h2,
.sidebar.collapsed .new-topic-btn span,
.sidebar.collapsed .chat-list li span,
.sidebar.collapsed .chat-list li .delete-btn {
  display: none;
}

.sidebar h2 {
  margin-top: 0;
  font-size: 1.5rem;
  margin-bottom: 20px;
  text-align: center;
  color: #42b983;
  transition: opacity 0.3s;
}

.new-topic-btn {
  background: #42b983;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 20px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.new-topic-btn:hover {
  background: #2c9d6c;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(44, 157, 108, 0.2);
}

.chat-list {
  list-style: none;
  padding: 0;
  margin: 0;
  flex: 1;
}

.chat-list li {
  padding: 12px 15px;
  margin-bottom: 8px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s;
}

.sidebar.collapsed .chat-list li {
  padding: 12px 5px;
  justify-content: center;
}

.chat-list li:hover {
  background: rgba(255, 255, 255, 0.2);
}

.chat-list li.active {
  background: rgba(66, 185, 131, 0.3);
  color: #fff;
  font-weight: bold;
}

.delete-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.6);
  transition: color 0.2s;
}

.delete-btn:hover {
  color: #ff6b6b;
}

/* 侧边栏切换按钮 */
.toggle-sidebar {
  position: absolute;
  top: 50%;
  right: -15px;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #42b983;
  border: none;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transform: translateY(-50%);
  box-shadow: 0 0 10px rgba(0,0,0,0.3);
  z-index: 10;
  transition: all 0.3s ease;
}

.toggle-sidebar:hover {
  background: #2c9d6c;
  transform: translateY(-50%) scale(1.1);
}

/* 主聊天区域样式 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: rgba(246, 251, 253, 0.8);
  position: relative;
  transition: all 0.3s ease;
}

/* 侧边栏收起时主区域扩展 */
.chat-main.expanded {
  margin-left: 0;
}

.chat-header {
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.8);
}

.chat-header strong {
  font-size: 1.2rem;
  color: #42b983;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #42b983;
}

.upload-label {
  font-size: 0.8rem;
  color: #42b983;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 15px;
  background: rgba(66, 185, 131, 0.1);
  transition: all 0.2s;
}

.upload-label:hover {
  background: rgba(66, 185, 131, 0.2);
}

.chat-box {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.welcome-message {
  background: rgba(66, 185, 131, 0.1);
  border-radius: 12px;
  padding: 20px;
  margin: 10px 0;
  text-align: center;
}

.welcome-message h3 {
  color: #42b983;
  margin-top: 0;
}

.welcome-message ul {
  text-align: left;
  list-style-type: none;
  padding: 0;
}

.welcome-message li {
  padding: 8px 0;
  position: relative;
  padding-left: 25px;
}

.welcome-message li:before {
  content: "👉";
  position: absolute;
  left: 0;
}

.chat-message {
  display: flex;
  gap: 12px;
  max-width: 80%;
}

.chat-message.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.chat-message.bot {
  align-self: flex-start;
}

.bubble {
  padding: 12px 16px;
  border-radius: 18px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: relative;
  line-height: 1.5;
}

.user .bubble {
  background: #42b983;
  color: white;
  border-bottom-right-radius: 4px;
}

.bot .bubble {
  background: white;
  color: #333;
  border-bottom-left-radius: 4px;
}

.loading-indicator {
  display: flex;
  gap: 5px;
  align-self: flex-start;
  background: white;
  padding: 12px 16px;
  border-radius: 18px;
  margin-left: 48px;
}

.dot {
  width: 8px;
  height: 8px;
  background: #42b983;
  border-radius: 50%;
  opacity: 0.8;
  animation: bounce 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) {
  animation-delay: -0.32s;
}

.dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.chat-input {
  display: flex;
  gap: 10px;
  padding: 15px 20px;
  background: white;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.chat-input input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 25px;
  outline: none;
  font-size: 1rem;
  transition: all 0.3s;
}

.chat-input input:focus {
  border-color: #42b983;
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.2);
}

.send-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: none;
  background: #42b983;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
}

.send-btn:hover {
  background: #2c9d6c;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(44, 157, 108, 0.2);
}

.send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 响应式设计 */
@media (max-width: 900px) {
  .chat-container {
    width: 100%;
    height: 100%;
    border-radius: 0;
  }
  
  .sidebar {
    width: 220px;
  }
  
  .sidebar.collapsed {
    width: 50px;
  }
  
  .chat-message {
    max-width: 90%;
  }
}

@media (max-width: 600px) {
  .chat-container {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    height: 150px;
    overflow-x: auto;
    overflow-y: hidden;
    display: flex;
    flex-direction: row;
    align-items: center;
    padding: 10px;
  }
  
  .sidebar.collapsed {
    height: 60px;
    width: 100%;
  }
  
  .toggle-sidebar {
    right: auto;
    top: auto;
    bottom: -15px;
    left: 50%;
    transform: translateX(-50%);
  }
  
  .toggle-sidebar:hover {
    transform: translateX(-50%) scale(1.1);
  }
  
  .chat-list {
    display: flex;
    flex-direction: row;
    gap: 10px;
    overflow-x: auto;
    padding-bottom: 10px;
  }
  
  .chat-list li {
    white-space: nowrap;
    margin-bottom: 0;
  }
  
  .chat-message {
    max-width: 95%;
  }
}
</style>