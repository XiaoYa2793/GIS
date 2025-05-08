<template>
  <div class="map-page">
    <div class="input-container">
      <!-- 搜索和导航输入区域 -->
      <div class="input-group">
        <div class="search-wrapper">
          <input 
            v-model="searchPlace" 
            placeholder="搜索地点" 
            @keyup.enter="searchLocation" 
            @input="handleSearchInput"
            class="search-input"
          >
          <button @click="searchLocation" class="search-btn">
            <span class="btn-icon">🔍</span>
          </button>
        </div>
        
        <div class="nav-inputs">
          <div class="input-with-label">
            <span class="input-label">起点</span>
            <input v-model="startPlace" placeholder="请输入起点" class="styled-input">
          </div>
          <div class="input-with-label">
            <span class="input-label">终点</span>
            <input v-model="endPlace" placeholder="请输入终点" class="styled-input">
          </div>
          <button @click="showTransportModes = true" class="route-btn">查询路线</button>
        </div>
      </div>
      
      <!-- 交通方式选择 -->
      <div class="transport-mode-container" v-if="showTransportModes">
        <div class="transport-mode">
          <button @click="() => fetchRouteByPlace('driving')" class="transport-btn">
            <span class="transport-icon">🚗</span>
            <span>驾车</span>
          </button>
          <button @click="() => fetchRouteByPlace('transit')" class="transport-btn">
            <span class="transport-icon">🚇</span>
            <span>公交地铁</span>
          </button>
          <button @click="() => fetchRouteByPlace('riding')" class="transport-btn">
            <span class="transport-icon">🚲</span>
            <span>骑行</span>
          </button>
          <button @click="() => fetchRouteByPlace('walking')" class="transport-btn">
            <span class="transport-icon">🚶</span>
            <span>步行</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 在交通方式下添加策略选择 -->
    <div class="strategy-mode" v-if="showTransportModes && strategy">
      <label>
        <select v-model="strategy" class="strategy-select">
          <option value="">默认推荐</option>
          <option value="LEAST_TRANSFER">少换乘</option>
          <option value="LEAST_WALKING">少步行</option>
          <option value="SUBWAY_FIRST">地铁优先</option>
          <option value="BUS_FIRST">公交优先</option>
        </select>
      </label>
    </div>

    <div id="map-container"></div>

    <div class="route-panel" v-if="routeInfo">
      <div class="route-header">
        <h3>路线信息</h3>
        <button @click="backToTransportSelection" class="back-button">返回</button>
      </div>
      
      <div class="route-summary">
        <div class="summary-item">
          <span class="summary-icon">🛣️</span>
          <div class="summary-detail">
            <span class="summary-label">总距离</span>
            <span class="summary-value">{{ (routeInfo.distance / 1000).toFixed(1) }} 公里</span>
          </div>
        </div>
        <div class="summary-item">
          <span class="summary-icon">⏱️</span>
          <div class="summary-detail">
            <span class="summary-label">预计时间</span>
            <span class="summary-value">{{ Math.floor(routeInfo.duration / 60) }} 分钟</span>
          </div>
        </div>
      </div>
      
      <div class="route-selector" v-if="routeOptions.length > 1">
        <button 
          v-for="(route, index) in routeOptions" 
          :key="index"
          @click="selectRoute(index)"
          :class="{ active: selectedRouteIndex === index }"
          class="route-option"
        >
          <span class="route-number">{{ index + 1 }}</span>
          <span>{{ route.tactic || `路线${index + 1}` }} ({{ (route.distance / 1000).toFixed(1) }}公里)</span>
        </button>
      </div>

      <!-- 添加公交地铁详细信息 -->
      <div v-if="routeInfo.transit_details" class="transit-details">
        <h4>换乘信息</h4>
        <div class="transit-steps">
          <div v-for="(detail, index) in routeInfo.transit_details" :key="index" class="transit-step">
            <div class="step-icon">
              <span v-if="detail.line_name && detail.line_name.includes('地铁')">🚇</span>
              <span v-else-if="detail.line_name">🚌</span>
              <span v-else>🚶</span>
            </div>
            <div class="step-info">
              <div class="step-headline">
                <span v-if="detail.line_name && detail.line_name.includes('地铁')" class="line-subway">
                  地铁: {{ detail.line_name }}
                </span>
                <span v-else-if="detail.line_name" class="line-bus">
                  公交: {{ detail.line_name }}
                </span>
                <span v-else class="line-walk">
                  步行
                </span>
                <span class="step-duration">{{ Math.floor(detail.duration / 60) }}分钟</span>
              </div>
              <div v-if="detail.start_station && detail.end_station" class="step-stations">
                {{ detail.start_station }} → {{ detail.end_station }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>

</template>

<script setup>
import { onMounted, ref, watch } from 'vue';
import axios from 'axios';

// 声明BMap为全局变量以便在组件内使用
const BMap = window.BMap;

// 添加控制显示的状态
const showTransportModes = ref(false);
const startPlace = ref('');
const endPlace = ref('');
const searchPlace = ref('');
const strategy = ref('');
const routeInfo = ref(null);
let map = null;

// 删除导航提示状态

// 删除实地导航相关状态和函数

// 修改handleSearchInput方法
const handleSearchInput = async () => {
  // 删除所有内容，只保留空函数或完全移除
};

// 初始化地图
const initMap = async () => {
  try {
    console.log("开始初始化地图...");
    // 检查地图容器是否存在
    const mapContainer = document.getElementById('map-container');
    if (!mapContainer) {
      console.error("地图容器不存在，无法初始化地图");
      return;
    }
    console.log("地图容器尺寸:", mapContainer.offsetWidth, "x", mapContainer.offsetHeight);
    
    // 优先使用BMap (非GL版本)
    if (window.BMap) {
      console.log("使用BMap API初始化地图");
      map = new window.BMap.Map('map-container');
      map.centerAndZoom(new window.BMap.Point(116.404, 39.915), 15);
      map.enableScrollWheelZoom(true);
      
      // 添加地图控件
      try {
        const scaleCtrl = new window.BMap.ScaleControl();
        map.addControl(scaleCtrl);
        const zoomCtrl = new window.BMap.ZoomControl();
        map.addControl(zoomCtrl);
        console.log("地图控件添加成功");
      } catch (ctrlError) {
        console.error("添加地图控件失败:", ctrlError);
      }
    } 
    // 如果BMap不可用，尝试使用BMapGL
    else if (window.BMapGL) {
      console.log("使用BMapGL API初始化地图");
      map = new window.BMapGL.Map('map-container');
      map.centerAndZoom(new window.BMapGL.Point(116.404, 39.915), 15);
      map.enableScrollWheelZoom(true);
      
      // 添加地图控件
      try {
        const scaleCtrl = new window.BMapGL.ScaleControl();
        map.addControl(scaleCtrl);
        const zoomCtrl = new window.BMapGL.ZoomControl();
        map.addControl(zoomCtrl);
        console.log("地图控件添加成功");
      } catch (ctrlError) {
        console.error("添加地图控件失败:", ctrlError);
      }
    }
    // 如果两者都不可用，尝试直接加载
    else {
      console.log("地图API未加载，尝试直接加载...");
      
      // 直接加载百度地图API
      await new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = 'https://api.map.baidu.com/api?v=3.0&ak=lKDN054tffFbo2jiOa1G87Rs9P3YH5QW';
        script.onload = () => {
          console.log("百度地图API加载成功");
          resolve();
        };
        script.onerror = (error) => {
          console.error("百度地图API加载失败:", error);
          reject(error);
        };
        document.head.appendChild(script);
      });
      
      // 重新检查API是否加载
      if (window.BMap) {
        console.log("成功加载BMap API，初始化地图");
        map = new window.BMap.Map('map-container');
        map.centerAndZoom(new window.BMap.Point(116.404, 39.915), 15);
        map.enableScrollWheelZoom(true);
      } else {
        throw new Error('无法加载百度地图API');
      }
    }
    
    console.log("地图初始化成功");
  } catch (error) {
    console.error('地图初始化失败:', error);
    alert("地图加载失败: " + error.message);
  }
};


// 绘制路线
const drawRoute = (routes) => {
  map.clearOverlays();
  
  routes.forEach((route, index) => {
    if (!route.points || route.points.length < 2) {
      console.error('无效的路线点数据:', route);
      return;
    }

    // 确保所有点都是有效的数字
    const bdPoints = route.points.map(point => {
      if (isNaN(point[0]) || isNaN(point[1])) {
        console.error('无效的坐标点:', point);
        return new BMap.Point(0, 0);
      }
      return new BMap.Point(point[1], point[0]);
    });

    // 使用曲线绘制路线
    const polyline = new BMap.Polyline(bdPoints, {
      strokeColor: index === selectedRouteIndex.value ? '#3388ff' : '#aaaaaa',
      strokeWeight: index === selectedRouteIndex.value ? 5 : 3,
      strokeOpacity: index === selectedRouteIndex.value ? 0.9 : 0.5,
      enableEditing: false,
      enableClicking: true,
      strokeStyle: 'solid'  // 确保使用实线而非虚线
    });

    // 添加路线点标记
    if (bdPoints.length > 0) {
      const startIcon = new BMap.Icon('/images/navigation/start.png', new BMap.Size(32, 32));
      const endIcon = new BMap.Icon('/images/navigation/end.png', new BMap.Size(32, 32));
      
      const startMarker = new BMap.Marker(bdPoints[0], {icon: startIcon});
      const endMarker = new BMap.Marker(bdPoints[bdPoints.length - 1], {icon: endIcon});
      
      map.addOverlay(startMarker);
      map.addOverlay(endMarker);
    }

    map.addOverlay(polyline);
    
    if (index === 0) {
      map.setViewport(bdPoints);
    }
  });
};

// 根据地名获取导航路线
// 在routeInfo下方添加新状态
const selectedRouteIndex = ref(0);
const routeOptions = ref([]);

// 修改fetchRouteByPlace方法
// 在fetchRouteByPlace方法中添加mode参数
const fetchRouteByPlace = async (mode = 'driving') => {
  try {
    // 添加参数验证
    if (!startPlace.value || !endPlace.value) {
      alert('请先输入起点和终点');
      return;
    }
    
    // 隐藏交通方式选择
    showTransportModes.value = false;
    
    console.log('请求参数:', { 
      start: startPlace.value,
      end: endPlace.value,
      mode,
      strategy: strategy.value
    });
    
    const res = await axios.get('/api/navigation-by-place', {
      params: {
        start: startPlace.value,
        end: endPlace.value,
        mode,
        strategy: strategy.value
      }
    });
    
    if (res.data.status === 0) {
      console.log('路线数据:', res.data.routes);
      routeOptions.value = res.data.routes;
      selectedRouteIndex.value = 0;
      routeInfo.value = routeOptions.value[0];
      
      // 处理驾车路线数据
      if (mode === 'driving') {
        routeOptions.value.forEach(route => {
          if (!route.points && route.steps) {
            // 从steps中提取路径点
            route.points = [];
            route.steps.forEach(step => {
              if (step.path) {
                const points = step.path.split(';');
                points.forEach(point => {
                  const [lng, lat] = point.split(',');
                  route.points.push([parseFloat(lat), parseFloat(lng)]);
                });
              }
            });
          }
        });
      }

      // 确保路线数据有效
      if (routeOptions.value.some(route => !route.points || route.points.length < 2)) {
        console.error('无效的路线数据:', routeOptions.value);
        alert('获取的路线数据不完整');
        return;
      }
      
      drawRoute(routeOptions.value);
      console.log('当前路线策略:', routeOptions.value[0].tactic);
      console.log('返回的路线信息:', routeInfo.value); // 打印查看 tactic 字段
    }
  } catch (err) {
    console.error('获取路线失败:', {
      error: err,
      requestConfig: err.config,
      response: err.response?.data
    });
    
    let errorMsg = '无法获取路线信息';
    if (err.response?.status === 503) {
      errorMsg = '地图服务暂时不可用，请稍后再试';
    } else if (err.response?.data?.message) {
      errorMsg += `: ${err.response.data.message}`;
    } else if (mode === 'transit') {
      errorMsg += '，公交地铁路线数据可能暂时不可用';
    }
    
    alert(errorMsg);
    showTransportModes.value = true; // 出错时重新显示交通方式选择
  }
};

// 添加路线点修改函数
const modifyRoutePoints = (points, offset) => {
  return points.map(point => {
    // 对每个点添加随机偏移
    const randomOffset = (Math.random() - 0.5) * offset;
    return [point[0] + randomOffset, point[1] + randomOffset];
  });
};

// 添加选择路线的方法
const selectRoute = (index) => {
  if (index < 0 || index >= routeOptions.value.length) return;
  
  selectedRouteIndex.value = index;
  // 直接更新 routeInfo，确保视图更新
  routeInfo.value = { ...routeOptions.value[index] };  // 使用浅拷贝来确保对象更新
  //routeInfo.value = routeOptions.value[index];
  // 调试：查看当前策略
  console.log('当前路线的策略:', routeInfo.value.tactic);
  drawRoute(routeOptions.value);
};
const searchLocation = async () => {
  if (!searchPlace.value.trim()) return;
  
  try {
    // 清空导航输入框和路线信息
    startPlace.value = '';
    endPlace.value = '';
    routeInfo.value = null;
    
    // 清除地图上的所有覆盖物（包括路线）
    map.clearOverlays();
    
    const res = await axios.get('/api/geocode', {
      params: { 
        address: searchPlace.value
      }
    });
    
    if (res.data.status === 0) {
      const { lat, lng } = res.data.location;
      // 确保坐标是数字类型
      const point = new BMap.Point(Number(lng), Number(lat));
      map.centerAndZoom(point, 15);
      
      // 添加标记
      const marker = new BMap.Marker(point);
      map.addOverlay(marker);
      
      // 添加信息窗口
      const infoWindow = new BMap.InfoWindow(searchPlace.value);
      marker.addEventListener("click", () => {
        map.openInfoWindow(infoWindow, point);
      });
      
      // 添加调试日志
      console.log('地图坐标:', point.lng, point.lat);
    }
  } catch (err) {
    console.error('搜索地点失败:', err);
    alert('搜索地点失败，请重试');
  }
};

onMounted(async () => {
  console.log("组件已挂载，准备初始化地图...");
  
  // 检查百度地图API是否已加载
  if (!window.BMapGL && !window.BMap) {
    console.log("地图API尚未加载，尝试等待加载...");
    
    // 尝试等待地图加载
    let maxAttempts = 10;
    let attempts = 0;
    
    const waitForBMap = () => {
      return new Promise((resolve) => {
        const checkInterval = setInterval(() => {
          attempts++;
          
          if (window.BMapGL || window.BMap) {
            clearInterval(checkInterval);
            console.log("地图API已加载，可以初始化地图");
            resolve(true);
          } else if (attempts >= maxAttempts) {
            clearInterval(checkInterval);
            console.error("等待地图API加载超时");
            resolve(false);
          }
        }, 500);
      });
    };
    
    const mapLoaded = await waitForBMap();
    if (!mapLoaded) {
      console.error("地图API加载失败，请刷新页面重试");
      alert("地图加载失败，请刷新页面重试");
      return;
    }
  }
  
  await initMap();
});
// 添加返回选择交通方式的方法
const backToTransportSelection = () => {
  routeInfo.value = null;
  showTransportModes.value = true;
  map.clearOverlays();
};

</script>

<style scoped>
/* 基础样式重置和全局变量 */
:root {
  --primary-color: #3388ff;
  --primary-dark: #2570e3;
  --primary-light: #5ba4ff;
  --secondary-color: #50c878;
  --accent-color: #ff6b6b;
  --text-color: #f0f0f0;
  --light-text: #b8c6db;
  --lighter-text: #8babd0;
  --dark-bg: #111827;
  --darker-bg: #0a101f;
  --panel-bg: rgba(17, 24, 39, 0.85);
  --card-bg: rgba(30, 41, 59, 0.7);
  --hover-bg: rgba(55, 65, 81, 0.6);
  --border-color: rgba(99, 109, 128, 0.3);
  --light-border: rgba(255, 255, 255, 0.1);
  --shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  --hover-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
  --neon-shadow: 0 0 15px rgba(51, 136, 255, 0.5);
  --transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  --border-radius: 12px;
  --button-radius: 8px;
  --gradient-primary: linear-gradient(135deg, #4b6cb7, #182848);
  --gradient-accent: linear-gradient(135deg, #ff6b6b, #ff8e8e);
  --gradient-success: linear-gradient(135deg, #43cea2, #185a9d);
  --gradient-transit: linear-gradient(135deg, #5c258d, #4389a2);
  --gradient-walking: linear-gradient(135deg, #56ab2f, #a8e063);
  --gradient-riding: linear-gradient(135deg, #2193b0, #6dd5ed);
  --gradient-driving: linear-gradient(135deg, #f46b45, #eea849);
  --glass-effect: backdrop-filter: blur(12px);
}

/* 页面基础布局 */
.map-page {
  position: relative;
  width: 100%;
  height: 100vh;
  font-family: 'PingFang SC', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  background: var(--dark-bg);
  color: var(--text-color);
  overflow: hidden;
}

.map-page::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url('/images/map-bg.jpg') center center;
  background-size: cover;
  opacity: 0.2;
  z-index: 0;
}

#map-container {
  width: 100%;
  height: calc(100vh - 70px);
  min-height: 500px;
  position: relative;
  z-index: 5;
  background-color: #0a1015;
  box-shadow: inset 0 0 40px rgba(0, 0, 0, 0.4);
  border-radius: 0 0 var(--border-radius) var(--border-radius);
  overflow: hidden;
}

/* 确保地图容器不被其他元素遮挡 */
.BMap_mask {
  background: transparent !important;
}

/* 顶部输入容器样式 */
.input-container {
  position: relative;
  z-index: 10;
  background: rgba(12, 15, 25, 0.85);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
  padding: 20px;
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--light-border);
  position: relative;
  overflow: hidden;
}

.input-container::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, var(--primary-color), var(--secondary-color), var(--accent-color));
  z-index: 1;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 15px;
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
}

/* 搜索框样式 */
.search-wrapper {
  display: flex;
  position: relative;
  max-width: 700px;
  margin: 0 auto;
  width: 100%;
}

.search-input {
  flex: 1;
  padding: 15px 20px;
  padding-left: 50px;
  border: 1px solid var(--border-color);
  border-radius: 30px;
  font-size: 16px;
  outline: none;
  transition: var(--transition);
  width: 100%;
  background-color: rgba(255, 255, 255, 0.05);
  color: var(--text-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  letter-spacing: 0.5px;
}

.search-input::placeholder {
  color: var(--light-text);
  opacity: 0.7;
}

.search-input:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(51, 136, 255, 0.2), var(--neon-shadow);
  background-color: rgba(255, 255, 255, 0.08);
}

.search-wrapper::before {
  content: "🔍";
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 18px;
  opacity: 0.7;
  pointer-events: none;
  z-index: 2;
}

.search-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: var(--gradient-primary);
  color: white;
  border: none;
  border-radius: 50%;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: var(--transition);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.search-btn:hover {
  transform: translateY(-50%) scale(1.05);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.3), var(--neon-shadow);
}

.btn-icon {
  font-size: 20px;
}

/* 导航输入区域 */
.nav-inputs {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  background: rgba(30, 41, 59, 0.4);
  padding: 20px;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  border: 1px solid var(--light-border);
}

.input-with-label {
  position: relative;
  flex: 1;
  min-width: 200px;
}

.input-label {
  position: absolute;
  left: 15px;
  top: -10px;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  padding: 2px 12px;
  font-size: 12px;
  color: white;
  border-radius: 20px;
  z-index: 2;
  font-weight: 500;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.styled-input {
  width: 100%;
  padding: 18px 15px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: 14px;
  outline: none;
  transition: var(--transition);
  background-color: rgba(255, 255, 255, 0.05);
  color: var(--text-color);
  letter-spacing: 0.5px;
}

.styled-input:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(51, 136, 255, 0.2), var(--neon-shadow);
  background-color: rgba(255, 255, 255, 0.08);
}

.route-btn {
  min-width: 130px;
  background: var(--gradient-primary);
  color: white;
  border: none;
  border-radius: var(--button-radius);
  padding: 14px 24px;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  letter-spacing: 0.7px;
  position: relative;
  overflow: hidden;
  text-transform: uppercase;
  font-size: 14px;
}

.route-btn::before {
  content: "";
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: rgba(255, 255, 255, 0.1);
  transform: rotate(45deg);
  z-index: 1;
  transition: var(--transition);
  pointer-events: none;
}

.route-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3), var(--neon-shadow);
}

.route-btn:hover::before {
  transform: rotate(45deg) translateY(-10%);
}

/* 交通方式选择 */
.transport-mode-container {
  margin-top: 20px;
  animation: fadeInUp 0.4s ease;
  background: rgba(30, 41, 59, 0.5);
  padding: 20px;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  border: 1px solid var(--light-border);
  backdrop-filter: blur(12px);
}

.transport-mode {
  display: flex;
  gap: 15px;
  overflow-x: auto;
  padding: 10px 0;
  justify-content: center;
}

.transport-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 18px 15px;
  min-width: 120px;
  background: var(--card-bg);
  border: 1px solid var(--light-border);
  border-radius: var(--button-radius);
  transition: var(--transition);
  cursor: pointer;
  color: var(--text-color);
  font-size: 15px;
  font-weight: 500;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
  position: relative;
  overflow: hidden;
}

.transport-btn:nth-child(1) {
  background: linear-gradient(to bottom right, rgba(255, 152, 0, 0.2), rgba(255, 87, 34, 0.2));
}

.transport-btn:nth-child(2) {
  background: linear-gradient(to bottom right, rgba(33, 150, 243, 0.2), rgba(13, 71, 161, 0.2));
}

.transport-btn:nth-child(3) {
  background: linear-gradient(to bottom right, rgba(76, 175, 80, 0.2), rgba(27, 94, 32, 0.2));
}

.transport-btn:nth-child(4) {
  background: linear-gradient(to bottom right, rgba(156, 39, 176, 0.2), rgba(74, 20, 140, 0.2));
}

.transport-btn::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, transparent, var(--primary-color), transparent);
  opacity: 0;
  transition: var(--transition);
}

.transport-btn:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
  border-color: rgba(51, 136, 255, 0.4);
}

.transport-btn:hover::after {
  opacity: 1;
}

.transport-icon {
  font-size: 28px;
  margin-bottom: 10px;
  background: rgba(255, 255, 255, 0.1);
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  margin-bottom: 12px;
  transition: var(--transition);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.transport-btn:hover .transport-icon {
  transform: scale(1.1);
  box-shadow: 0 0 20px rgba(51, 136, 255, 0.3);
}

/* 策略选择样式 */
.strategy-mode {
  position: absolute;
  top: 150px;
  right: 25px;
  z-index: 20;
  background: var(--panel-bg);
  padding: 12px 15px;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
  backdrop-filter: blur(12px);
  border: 1px solid var(--light-border);
  animation: fadeInRight 0.4s ease;
}

.strategy-select {
  padding: 10px 15px;
  border: 1px solid var(--border-color);
  border-radius: var(--button-radius);
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-color);
  font-size: 14px;
  outline: none;
  cursor: pointer;
  transition: var(--transition);
}

.strategy-select:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(51, 136, 255, 0.2);
}

.strategy-select option {
  background-color: var(--darker-bg);
  color: var(--text-color);
}

/* 路线信息面板 */
.route-panel {
  position: absolute;
  top: 100px;
  left: 25px;
  background: var(--panel-bg);
  color: var(--text-color);
  padding: 25px;
  border-radius: var(--border-radius);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
  z-index: 100;
  min-width: 320px;
  max-width: 400px;
  max-height: calc(100vh - 220px);
  overflow-y: auto;
  backdrop-filter: blur(12px);
  border: 1px solid var(--light-border);
  animation: fadeInLeft 0.5s ease;
}

.route-panel::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 5px;
  height: 100%;
  background: linear-gradient(to bottom, var(--primary-color), transparent);
  border-radius: var(--border-radius) 0 0 var(--border-radius);
}

.route-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--light-border);
}

.route-header h3 {
  margin: 0;
  color: white;
  font-size: 20px;
  font-weight: 600;
  display: inline-block;
  position: relative;
}

.route-header h3::after {
  content: "";
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 40px;
  height: 3px;
  background: var(--primary-color);
  border-radius: 3px;
}

.back-button {
  padding: 8px 15px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: none;
  border-radius: 30px;
  cursor: pointer;
  font-size: 13px;
  transition: var(--transition);
  border: 1px solid var(--light-border);
}

.back-button:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 路线摘要信息 */
.route-summary {
  display: flex;
  gap: 15px;
  background: var(--card-bg);
  padding: 20px;
  border-radius: var(--border-radius);
  margin-bottom: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--light-border);
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.summary-icon {
  font-size: 22px;
  background: rgba(51, 136, 255, 0.15);
  width: 46px;
  height: 46px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.summary-detail {
  display: flex;
  flex-direction: column;
}

.summary-label {
  font-size: 12px;
  color: var(--light-text);
  letter-spacing: 0.5px;
}

.summary-value {
  font-size: 18px;
  font-weight: 600;
  color: white;
  letter-spacing: 0.5px;
}

/* 路线选择器 */
.route-selector {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
  color: #2193b0;
}

.route-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px;
  background: var(--card-bg);
  border: 1px solid var(--light-border);
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: var(--transition);
  text-align: left;
  font-size: 14px;
  color: var(--text-color);
  position: relative;
  overflow: hidden;
}

.route-option::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: var(--primary-color);
  opacity: 0;
  transition: var(--transition);
}

.route-option:hover {
  background: var(--hover-bg);
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.15);
}

.route-option:hover::before {
  opacity: 1;
}

.route-option.active {
  background: linear-gradient(to right, rgba(51, 136, 255, 0.2), rgba(30, 41, 59, 0.7));
  border-color: rgba(51, 136, 255, 0.5);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
  transform: translateY(-3px);
}

.route-option.active::before {
  opacity: 1;
}

.route-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: var(--primary-color);
  color: white;
  border-radius: 50%;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 3px 10px rgba(51, 136, 255, 0.3);
  letter-spacing: 0.5px;
}

.route-option.active .route-number {
  background: white;
  color: var(--primary-color);
}

/* 公交地铁详细信息 */
.transit-details {
  margin-top: 20px;
  border-top: 1px solid var(--light-border);
  padding-top: 20px;
}

.transit-details h4 {
  color: white;
  margin: 0 0 15px 0;
  font-size: 18px;
  font-weight: 600;
  display: inline-block;
  position: relative;
  letter-spacing: 0.5px;
}

.transit-details h4::after {
  content: "";
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 30px;
  height: 3px;
  background: var(--primary-color);
  border-radius: 3px;
}

.transit-steps {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.transit-step {
  display: flex;
  gap: 15px;
  padding: 15px;
  background: var(--card-bg);
  border-radius: var(--border-radius);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--light-border);
  transition: var(--transition);
  position: relative;
  overflow: hidden;
}

.transit-step::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 3px;
  height: 100%;
  opacity: 0;
  transition: var(--transition);
}

.transit-step:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.transit-step:hover::before {
  opacity: 1;
}

.step-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 40px;
  height: 40px;
  border-radius: 50%;
  font-size: 20px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.transit-step:nth-child(1) .step-icon,
.transit-step:nth-child(1)::before {
  background: linear-gradient(135deg, #5c258d, #4389a2);
  color: white;
}

.transit-step:nth-child(2) .step-icon,
.transit-step:nth-child(2)::before {
  background: linear-gradient(135deg, #134e5e, #71b280);
  color: white;
}

.transit-step:nth-child(3) .step-icon,
.transit-step:nth-child(3)::before {
  background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
  color: white;
}

.transit-step:nth-child(4) .step-icon,
.transit-step:nth-child(4)::before {
  background: linear-gradient(135deg, #396afc, #2948ff);
  color: white;
}

.step-info {
  flex: 1;
}

.step-headline {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.line-subway {
  color: #5c258d;
  font-weight: 600;
  font-size: 15px;
  display: inline-block;
  padding: 3px 10px;
  background: rgba(92, 37, 141, 0.15);
  border-radius: 20px;
  letter-spacing: 0.5px;
}

.line-bus {
  color: #43cea2;
  font-weight: 600;
  font-size: 15px;
  display: inline-block;
  padding: 3px 10px;
  background: rgba(67, 206, 162, 0.15);
  border-radius: 20px;
  letter-spacing: 0.5px;
}

.line-walk {
  color: #ff6b6b;
  font-weight: 600;
  font-size: 15px;
  display: inline-block;
  padding: 3px 10px;
  background: rgba(255, 107, 107, 0.15);
  border-radius: 20px;
  letter-spacing: 0.5px;
}

.step-duration {
  font-size: 13px;
  color: var(--light-text);
  background: rgba(255, 255, 255, 0.08);
  padding: 3px 10px;
  border-radius: 20px;
  letter-spacing: 0.5px;
  font-weight: 500;
}

.step-stations {
  font-size: 13px;
  color: var(--light-text);
  background: rgba(255, 255, 255, 0.05);
  padding: 8px 12px;
  border-radius: 8px;
  margin-top: 5px;
  letter-spacing: 0.5px;
  line-height: 1.5;
}

/* 动画效果 */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeInUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

@keyframes fadeInLeft {
  from { transform: translateX(-30px); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

@keyframes fadeInRight {
  from { transform: translateX(30px); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .route-panel {
    left: 50%;
    transform: translateX(-50%);
    top: auto;
    bottom: 20px;
    max-width: 90%;
    max-height: 60vh;
    width: 90%;
  }

  .nav-inputs {
    flex-direction: column;
  }

  .input-with-label {
    min-width: 100%;
  }

  .route-btn {
    width: 100%;
    margin-top: 10px;
  }

  .strategy-mode {
    top: auto;
    bottom: 20px;
    right: 20px;
  }
  
  .transport-mode {
    justify-content: flex-start;
    padding: 5px 0 15px;
  }
  
  .transport-btn {
    min-width: 90px;
    padding: 12px 5px;
  }
  
  .transport-icon {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
}

/* 自定义滚动条 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}

::-webkit-scrollbar-thumb {
  background: rgba(51, 136, 255, 0.5);
  border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(51, 136, 255, 0.7);
}
</style>

