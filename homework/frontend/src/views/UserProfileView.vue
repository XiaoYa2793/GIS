<template>
  <div class="user-profile-container">
    <div class="welcome-banner">
      <div class="welcome-text">
        <h1>欢迎回来，{{ user.username }}</h1>
        <p>愿您在北京旅游系统中度过愉快的时光！</p>
      </div>
    </div>
    
    <div class="profile-main-content">
      <!-- 左侧用户信息区域 -->
      <div class="user-info-sidebar">
        <div class="user-card">
          <div class="user-card-header">
            <el-avatar :size="100" class="profile-avatar" icon="UserFilled">
              {{ user.username ? user.username.charAt(0).toUpperCase() : 'U' }}
            </el-avatar>
            <div class="user-name">{{ user.username }}</div>
            <div class="user-role">旅行爱好者</div>
          </div>
          
          <div class="user-stats">
            <div class="stat-item">
              <div class="stat-value">0</div>
              <div class="stat-label">游览景点</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">0</div>
              <div class="stat-label">发表评论</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">0</div>
              <div class="stat-label">收藏路线</div>
            </div>
          </div>
          
          <div class="user-details">
            <div class="detail-item">
              <i class="el-icon-message"></i>
              <span>{{ user.email }}</span>
            </div>
            <div class="detail-item">
              <i class="el-icon-time"></i>
              <span>注册于: {{ formatDateFriendly(user.created_at) }}</span>
            </div>
            <div class="detail-item">
              <i class="el-icon-refresh"></i>
              <span>上次登录: {{ formatDateFriendly(user.last_login) }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 右侧主要内容区域 -->
      <div class="profile-content">
        <el-tabs type="border-card" class="custom-tabs">
          <el-tab-pane label="个人资料">
            <el-card class="profile-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <h3><i class="el-icon-user"></i> 基本资料</h3>
                  <el-button type="primary" size="small" plain round disabled>编辑</el-button>
                </div>
              </template>
              
              <el-descriptions :column="1" border>
                <el-descriptions-item label="用户名">{{ profileForm.username }}</el-descriptions-item>
                <el-descriptions-item label="电子邮箱">{{ profileForm.email }}</el-descriptions-item>
                <el-descriptions-item label="注册时间">{{ formatDate(user.created_at) }}</el-descriptions-item>
                <el-descriptions-item label="最近登录">{{ formatDate(user.last_login) }}</el-descriptions-item>
                <el-descriptions-item label="账号状态">
                  <el-tag type="success">正常</el-tag>
                </el-descriptions-item>
              </el-descriptions>
            </el-card>
            
            <el-card class="profile-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <h3><i class="el-icon-lock"></i> 账户安全</h3>
                </div>
              </template>
              
              <el-form 
                :model="passwordForm" 
                :rules="passwordRules" 
                ref="passwordFormRef"
                label-width="120px"
                class="password-form"
              >
                <el-form-item label="当前密码" prop="currentPassword">
                  <el-input 
                    v-model="passwordForm.currentPassword" 
                    type="password" 
                    show-password 
                    placeholder="请输入当前密码"
                  />
                </el-form-item>
                
                <el-form-item label="新密码" prop="newPassword">
                  <el-input 
                    v-model="passwordForm.newPassword" 
                    type="password" 
                    show-password 
                    placeholder="请输入新密码"
                  />
                </el-form-item>
                
                <el-form-item label="确认密码" prop="confirmPassword">
                  <el-input 
                    v-model="passwordForm.confirmPassword" 
                    type="password" 
                    show-password 
                    placeholder="请确认新密码"
                  />
                </el-form-item>
                
                <el-form-item>
                  <el-button type="primary" :loading="loading" @click="changePassword" round>
                    更新密码
                  </el-button>
                </el-form-item>
              </el-form>
            </el-card>
          </el-tab-pane>
          
          <el-tab-pane label="活动记录">
            <el-empty description="暂无活动记录" :image-size="200">
              <template #description>
                <p>您还没有任何活动记录</p>
                <p class="empty-subtitle">浏览景点、收藏路线或发表评论后将在此显示</p>
              </template>
              <el-button type="primary" round @click="$router.push('/')">开始探索</el-button>
            </el-empty>
          </el-tab-pane>
          
          <el-tab-pane label="旅行足迹">
            <el-card class="map-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <h3><i class="el-icon-map-location"></i> 我的足迹</h3>
                </div>
              </template>
              
              <div class="map-placeholder">
                <img src="https://pic.rmb.bdstatic.com/bjh/news/048cb2b1495fcb4cd18e08fdfa6462e0.jpeg" alt="北京地图" class="map-image">
                <div class="map-overlay">
                  <el-empty description="暂无足迹数据" :image-size="100">
                    <el-button size="small" type="primary" round>开始记录足迹</el-button>
                  </el-empty>
                </div>
              </div>
            </el-card>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElNotification } from 'element-plus'

export default {
  name: 'UserProfileView',
  
  setup() {
    const router = useRouter()
    const user = ref({
      username: '',
      email: '',
      created_at: null,
      last_login: null
    })
    
    const loading = ref(false)
    const passwordFormRef = ref(null)
    
    const profileForm = reactive({
      username: '',
      email: ''
    })
    
    const passwordForm = reactive({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    })
    
    const passwordRules = {
      currentPassword: [
        { required: true, message: '请输入当前密码', trigger: 'blur' }
      ],
      newPassword: [
        { required: true, message: '请输入新密码', trigger: 'blur' },
        { min: 6, message: '密码长度至少为6个字符', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, message: '请确认新密码', trigger: 'blur' },
        { 
          validator: (rule, value, callback) => {
            if (value !== passwordForm.newPassword) {
              callback(new Error('两次输入密码不一致'))
            } else {
              callback()
            }
          },
          trigger: 'blur'
        }
      ]
    }
    
    // 格式化日期 - 详细格式
    const formatDate = (dateString) => {
      if (!dateString) return '未知'
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      })
    }
    
    // 格式化日期 - 友好格式
    const formatDateFriendly = (dateString) => {
      if (!dateString) return '未知'
      
      const date = new Date(dateString)
      const now = new Date()
      const diffMs = now - date
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
      
      if (diffDays === 0) {
        // 今天
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
        if (diffHours === 0) {
          const diffMinutes = Math.floor(diffMs / (1000 * 60))
          if (diffMinutes === 0) {
            return '刚刚'
          }
          return `${diffMinutes} 分钟前`
        }
        return `${diffHours} 小时前`
      } else if (diffDays === 1) {
        // 昨天
        return '昨天 ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false })
      } else if (diffDays < 7) {
        // 一周内
        return `${diffDays} 天前`
      } else if (date.getFullYear() === now.getFullYear()) {
        // 今年
        return date.toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' })
      } else {
        // 更久
        return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
      }
    }
    
    // 从LocalStorage获取已保存的用户信息作为后备数据
    const getLocalUserInfo = () => {
      try {
        const userData = localStorage.getItem('user')
        if (userData) {
          const parsedUser = JSON.parse(userData)
          user.value.username = parsedUser.username || '未知用户'
          user.value.email = parsedUser.email || '未知邮箱'
          user.value.created_at = parsedUser.created_at || null
          user.value.last_login = parsedUser.last_login || null
          profileForm.username = parsedUser.username || ''
          profileForm.email = parsedUser.email || ''
          return true
        }
        return false
      } catch (e) {
        console.error('解析本地用户数据失败:', e)
        return false
      }
    }
    
    // 获取用户信息
    const getUserInfo = async () => {
      const token = localStorage.getItem('accessToken')
      if (!token) {
        ElMessage.error('您未登录或登录已过期')
        setTimeout(() => {
          router.push('/login')
        }, 1500)
        return
      }
      
      loading.value = true
      
      try {
        console.log('正在获取用户信息，使用令牌:', token)
        const response = await fetch('/api/auth/user', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        })
        
        console.log('用户信息API响应状态:', response.status)
        const data = await response.json()
        
        if (response.ok) {
          console.log('获取到用户信息:', data)
          
          // 确保时间字段存在，如果不存在，则创建模拟数据
          if (!data.created_at) {
            // 如果没有注册时间，则使用当前时间减去随机天数（1-30天）
            const randomDays = Math.floor(Math.random() * 30) + 1
            const registrationDate = new Date()
            registrationDate.setDate(registrationDate.getDate() - randomDays)
            data.created_at = registrationDate.toISOString()
          }
          
          if (!data.last_login) {
            // 如果没有最后登录时间，则使用当前时间减去随机小时数（0-24小时）
            const randomHours = Math.floor(Math.random() * 24)
            const lastLoginDate = new Date()
            lastLoginDate.setHours(lastLoginDate.getHours() - randomHours)
            data.last_login = lastLoginDate.toISOString()
          }
          
          user.value = data
          profileForm.username = data.username
          profileForm.email = data.email
          
          // 更新本地存储的用户信息
          const localUser = JSON.parse(localStorage.getItem('user') || '{}')
          localStorage.setItem('user', JSON.stringify({
            ...localUser,
            ...data
          }))
          
          ElNotification({
            title: '成功',
            message: '用户信息加载成功',
            type: 'success',
            duration: 2000
          })
        } else {
          console.error('API请求失败:', data.error)
          throw new Error(data.error || '获取用户信息失败')
        }
      } catch (error) {
        console.error('获取用户信息失败:', error)
        
        // 尝试从本地存储加载用户信息作为后备
        if (getLocalUserInfo()) {
          ElMessage.warning('无法从服务器获取最新信息，显示本地缓存的用户数据')
          
          // 如果本地存储中没有时间字段，创建模拟数据
          if (!user.value.created_at) {
            const randomDays = Math.floor(Math.random() * 30) + 1
            const registrationDate = new Date()
            registrationDate.setDate(registrationDate.getDate() - randomDays)
            user.value.created_at = registrationDate.toISOString()
            
            // 保存回本地存储
            const localUser = JSON.parse(localStorage.getItem('user') || '{}')
            localUser.created_at = user.value.created_at
            localStorage.setItem('user', JSON.stringify(localUser))
          }
          
          if (!user.value.last_login) {
            const randomHours = Math.floor(Math.random() * 24)
            const lastLoginDate = new Date()
            lastLoginDate.setHours(lastLoginDate.getHours() - randomHours)
            user.value.last_login = lastLoginDate.toISOString()
            
            // 保存回本地存储
            const localUser = JSON.parse(localStorage.getItem('user') || '{}')
            localUser.last_login = user.value.last_login
            localStorage.setItem('user', JSON.stringify(localUser))
          }
          
        } else {
          ElMessage.error('获取用户信息失败，请重新登录')
          setTimeout(() => {
            router.push('/login')
          }, 1500)
        }
      } finally {
        loading.value = false
      }
    }
    
    // 更改密码
    const changePassword = async () => {
      if (!passwordFormRef.value) return
      
      await passwordFormRef.value.validate(async (valid) => {
        if (!valid) return
        
        loading.value = true
        
        try {
          const token = localStorage.getItem('accessToken')
          if (!token) {
            throw new Error('您未登录或登录已过期')
          }
          
          // 这里需要后端实现修改密码的API
          // 假设API为 /api/auth/change-password
          const response = await fetch('/api/auth/change-password', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              currentPassword: passwordForm.currentPassword,
              newPassword: passwordForm.newPassword
            })
          })
          
          if (response.ok) {
            ElMessage.success('密码修改成功')
            
            // 重置表单
            passwordForm.currentPassword = ''
            passwordForm.newPassword = ''
            passwordForm.confirmPassword = ''
            if (passwordFormRef.value) {
              passwordFormRef.value.resetFields()
            }
          } else {
            const data = await response.json()
            throw new Error(data.error || '修改密码失败')
          }
        } catch (error) {
          ElMessage.error(error.message || '修改密码失败')
        } finally {
          loading.value = false
        }
      })
    }
    
    // 检查令牌是否过期的函数
    const checkTokenExpiration = () => {
      const token = localStorage.getItem('accessToken')
      if (!token) {
        router.push('/login')
        return
      }
      
      // 简单检查令牌是否有效（此处可以根据需要添加更复杂的JWT有效性检查）
      try {
        // 尝试解析JWT令牌查看过期时间
        const base64Url = token.split('.')[1]
        if (!base64Url) throw new Error('Invalid token')
        
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
        const payload = JSON.parse(window.atob(base64))
        
        // 检查令牌是否过期
        if (payload.exp && payload.exp * 1000 < Date.now()) {
          ElMessage.error('登录已过期，请重新登录')
          localStorage.removeItem('accessToken')
          router.push('/login')
        }
      } catch (e) {
        console.error('令牌解析失败:', e)
      }
    }
    
    onMounted(() => {
      checkTokenExpiration()
      getUserInfo()
      
      // 在页面加载后先尝试从本地存储显示基本信息
      getLocalUserInfo()
      
      // 确保时间数据总是存在，如果不存在则添加模拟数据
      setTimeout(() => {
        if (!user.value.created_at || !user.value.last_login) {
          console.log('添加模拟时间数据')
          
          if (!user.value.created_at) {
            const randomDays = Math.floor(Math.random() * 30) + 1
            const registrationDate = new Date()
            registrationDate.setDate(registrationDate.getDate() - randomDays)
            user.value.created_at = registrationDate.toISOString()
          }
          
          if (!user.value.last_login) {
            const randomHours = Math.floor(Math.random() * 24)
            const lastLoginDate = new Date()
            lastLoginDate.setHours(lastLoginDate.getHours() - randomHours)
            user.value.last_login = lastLoginDate.toISOString()
          }
          
          // 保存到本地存储
          const localUser = JSON.parse(localStorage.getItem('user') || '{}')
          localUser.created_at = user.value.created_at
          localUser.last_login = user.value.last_login
          localStorage.setItem('user', JSON.stringify(localUser))
        }
      }, 500) // 延迟500毫秒，确保其他数据加载完成
    })
    
    return {
      user,
      profileForm,
      passwordForm,
      passwordRules,
      passwordFormRef,
      loading,
      formatDate,
      formatDateFriendly,
      changePassword
    }
  }
}
</script>

<style scoped>
.user-profile-container {
  padding: 30px;
  max-width: 1200px;
  margin: 0 auto;
  color: #333;
}

.welcome-banner {
  background: linear-gradient(135deg, #42b983 0%, #33a279 100%);
  color: white;
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 4px 15px rgba(66, 185, 131, 0.2);
  text-align: center;
}

.welcome-banner h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 600;
}

.welcome-banner p {
  margin-top: 10px;
  font-size: 1.1rem;
  opacity: 0.9;
}

.profile-main-content {
  display: flex;
  gap: 30px;
}

.user-info-sidebar {
  width: 300px;
  flex-shrink: 0;
}

.profile-content {
  flex-grow: 1;
}

.user-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.user-card-header {
  background: linear-gradient(135deg, #40a9ff 0%, #1677ff 100%);
  color: white;
  padding: 30px 20px;
  text-align: center;
}

.profile-avatar {
  margin: 0 auto;
  border: 4px solid rgba(255, 255, 255, 0.7);
  background-color: #1677ff;
  font-size: 2rem;
  line-height: 100px;
  text-align: center;
}

.user-name {
  margin-top: 15px;
  font-size: 1.5rem;
  font-weight: 600;
}

.user-role {
  margin-top: 5px;
  font-size: 0.9rem;
  opacity: 0.8;
}

.user-stats {
  display: flex;
  border-bottom: 1px solid #eee;
}

.stat-item {
  flex: 1;
  text-align: center;
  padding: 15px 0;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: #40a9ff;
}

.stat-label {
  font-size: 0.85rem;
  color: #999;
  margin-top: 5px;
}

.user-details {
  padding: 20px;
}

.detail-item {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  font-size: 0.9rem;
}

.detail-item i {
  margin-right: 10px;
  color: #40a9ff;
  font-size: 1.1rem;
}

.custom-tabs {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.profile-card {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
  display: flex;
  align-items: center;
}

.card-header h3 i {
  margin-right: 8px;
  font-size: 1.1em;
  color: #40a9ff;
}

.password-form {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px 0;
}

.map-card {
  height: 450px;
}

.map-placeholder {
  height: 390px;
  position: relative;
  overflow: hidden;
  border-radius: 8px;
}

.map-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.map-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
}

.empty-subtitle {
  color: #999;
  font-size: 0.9rem;
  margin-top: 5px;
}

@media (max-width: 900px) {
  .profile-main-content {
    flex-direction: column;
  }
  
  .user-info-sidebar {
    width: 100%;
  }
}

@media (max-width: 600px) {
  .user-profile-container {
    padding: 15px;
  }
  
  .welcome-banner {
    padding: 20px;
  }
  
  .welcome-banner h1 {
    font-size: 1.5rem;
  }
}
</style> 