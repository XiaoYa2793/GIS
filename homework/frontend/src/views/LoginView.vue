<template>
  <div class="login-page">
    <div class="login-background"></div>
    <div class="login-container">
      <div class="login-form-container">
        <div class="login-logo">
          <h1>BTS</h1>
          <p>Beijing Travel System</p>
        </div>
        
        <div class="login-header">
          <h2>{{ isLogin ? '登录' : '注册' }}</h2>
          <p>{{ isLogin ? '欢迎回来北京旅行平台' : '加入北京旅行平台' }}</p>
        </div>

        <el-form :model="form" label-position="top" :rules="rules" ref="loginForm">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="form.username" placeholder="请输入用户名" prefix-icon="User" />
          </el-form-item>

          <el-form-item label="密码" prop="password">
            <el-input 
              v-model="form.password" 
              type="password" 
              placeholder="请输入密码" 
              prefix-icon="Lock" 
              show-password 
              @keyup.enter="submitForm"
            />
          </el-form-item>

          <!-- 注册时显示确认密码和邮箱 -->
          <template v-if="!isLogin">
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input 
                v-model="form.confirmPassword" 
                type="password" 
                placeholder="请确认密码" 
                prefix-icon="Lock" 
                show-password 
              />
            </el-form-item>
            
            <el-form-item label="电子邮箱" prop="email">
              <el-input v-model="form.email" placeholder="请输入电子邮箱" prefix-icon="Message" />
            </el-form-item>
          </template>

          <div class="default-account-tip" v-if="isLogin">
            默认账号: admin / 密码: 123456
          </div>

          <el-form-item>
            <el-button 
              type="primary" 
              :loading="loading" 
              @click="submitForm" 
              class="submit-button"
            >
              {{ isLogin ? '登录' : '注册' }}
            </el-button>
          </el-form-item>

          <div class="login-options">
            <span @click="toggleLoginMode">
              {{ isLogin ? '没有账号？点击注册' : '已有账号？点击登录' }}
            </span>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElNotification } from 'element-plus'

export default {
  name: 'LoginView',
  
  setup() {
    const router = useRouter()
    const loginForm = ref(null)
    const loading = ref(false)
    const isLogin = ref(true)

    const form = reactive({
      username: '',
      password: '',
      confirmPassword: '',
      email: ''
    })

    // 表单验证规则
    const rules = computed(() => {
      const baseRules = {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '用户名长度应为3-20个字符', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码长度至少为6个字符', trigger: 'blur' }
        ]
      }

      // 注册模式下添加额外验证
      if (!isLogin.value) {
        baseRules.confirmPassword = [
          { required: true, message: '请确认密码', trigger: 'blur' },
          { 
            validator: (rule, value, callback) => {
              if (value !== form.password) {
                callback(new Error('两次输入密码不一致'))
              } else {
                callback()
              }
            }, 
            trigger: 'blur' 
          }
        ]
        
        baseRules.email = [
          { required: true, message: '请输入电子邮箱', trigger: 'blur' },
          { type: 'email', message: '请输入有效的电子邮箱地址', trigger: 'blur' }
        ]
      }
      
      return baseRules
    })

    // 切换登录/注册模式
    const toggleLoginMode = () => {
      isLogin.value = !isLogin.value
      // 重置表单
      if (loginForm.value) {
        loginForm.value.resetFields()
      }
    }

    // 显示欢迎消息
    const showWelcomeMessage = (username) => {
      // 显示一个通知
      ElNotification({
        title: isLogin.value ? '登录成功' : '注册成功',
        message: isLogin.value 
          ? `欢迎回来，${username}！正在为您准备精彩的北京旅行体验...` 
          : `欢迎加入北京旅行系统，${username}！您的账号已成功创建`,
        type: 'success',
        duration: 3000,
        position: 'top-right'
      })
      
      // 同时显示一个消息提示
      ElMessage({
        message: isLogin.value ? '登录成功' : '注册成功',
        type: 'success',
        duration: 2000,
        showClose: true
      })
    }

    // 提交表单
    const submitForm = async () => {
      if (!loginForm.value) return
      
      await loginForm.value.validate(async (valid) => {
        if (!valid) return
        
        loading.value = true
        
        try {
          const apiUrl = isLogin.value 
            ? '/api/auth/login' 
            : '/api/auth/register'
            
          const reqData = {
            username: form.username,
            password: form.password
          }
          
          // 注册时添加邮箱
          if (!isLogin.value) {
            reqData.email = form.email
          }
          
          const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(reqData)
          })
          
          const data = await response.json()
          
          if (!response.ok) {
            throw new Error(data.error || '操作失败')
          }
          
          // 保存token和用户信息
          localStorage.setItem('accessToken', data.access_token)
          localStorage.setItem('user', JSON.stringify(data.user))
          
          // 显示欢迎消息
          showWelcomeMessage(data.user.username)
          
          if (isLogin.value) {
            // 短暂延迟后跳转，让用户有时间看到成功提示
            setTimeout(() => {
              // 方法1：使用location.href强制页面完全刷新
              // 这确保在加载首页时会重新初始化所有组件
              window.location.href = '/'
              
              // 方法2(备用)：使用window.location.replace，它不会在历史记录中留下重定向记录
              // window.location.replace('/')
            }, 1500)
          } else {
            // 注册成功后跳转到登录页
            setTimeout(() => {
              router.push('/login')
            }, 1500)
          }
        } catch (error) {
          ElMessage.error(error.message || '操作失败，请稍后重试')
          console.error('Auth error:', error)
        } finally {
          loading.value = false
        }
      })
    }

    // 自动填写默认账户（仅用于测试）
    const fillDefaultAccount = () => {
      if (isLogin.value) {
        form.username = 'admin'
        form.password = '123456'
      }
    }

    return {
      loginForm,
      form,
      rules,
      loading,
      isLogin,
      toggleLoginMode,
      submitForm,
      fillDefaultAccount
    }
  }
}
</script>

<style scoped>
.login-page {
  height: 100vh;
  width: 100vw;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.login-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #0a192f, #172a46);
  z-index: -1;
}

.login-background::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url('/static/images/beijing_bg.jpg') center center;
  background-size: cover;
  opacity: 0.15;
  z-index: -1;
}

.login-container {
  width: 100%;
  max-width: 1200px;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  z-index: 1;
}

.login-form-container {
  width: 100%;
  max-width: 450px;
  padding: 40px;
  background: rgba(26, 31, 44, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  color: #fff;
}

.login-logo {
  text-align: center;
  margin-bottom: 20px;
}

.login-logo h1 {
  font-size: 3rem;
  font-weight: bold;
  color: #42b983;
  margin: 0;
  text-shadow: 0 0 15px rgba(66, 185, 131, 0.5);
}

.login-logo p {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.8);
  margin: 5px 0 0;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  font-size: 2rem;
  color: #fff;
  margin: 0 0 10px;
}

.login-header p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1rem;
  margin: 0;
}

.default-account-tip {
  text-align: center;
  margin: 10px 0;
  padding: 10px;
  background: rgba(66, 185, 131, 0.1);
  border-radius: 4px;
  color: #42b983;
  font-size: 0.9rem;
}

.submit-button {
  width: 100%;
  height: 44px;
  margin-top: 20px;
  font-size: 1rem;
  background: #42b983;
  border: none;
}

.submit-button:hover {
  background: #3aa876;
}

.login-options {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  font-size: 0.9rem;
  color: #42b983;
  cursor: pointer;
}

.login-options span:hover {
  text-decoration: underline;
}

:deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.1);
}

:deep(.el-input__inner) {
  color: #fff;
}

:deep(.el-form-item__label) {
  color: rgba(255, 255, 255, 0.9);
}
</style> 