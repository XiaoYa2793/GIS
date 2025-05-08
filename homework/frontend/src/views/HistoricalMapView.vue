<template>
  <div class="historical-map-view">
    <!-- 错误提示 -->
    <div class="error-message" v-if="error">
      <el-alert
        :title="'加载失败'"
        type="error"
        description="无法加载历史地图数据"
        show-icon
        :closable="false"
      >
        <div class="error-details">
          <p>{{ error }}</p>
          <button @click="retryLoading" class="retry-btn">
            <el-icon><Refresh /></el-icon> 重试
          </button>
        </div>
      </el-alert>
    </div>

    <div class="header-section">
      <h1>北京历史地图</h1>
      <p>探索北京城不同时期的历史变迁与城市发展</p>
    </div>

    <!-- 时间轴和时期选择 -->
    <div class="timeline-section">
      <h2>
        <el-icon><Timer /></el-icon>
        时间轴
      </h2>
      <div class="period-filters">
        <button 
          v-for="period in periods" 
          :key="period"
          :class="{ active: selectedPeriod === period }"
          @click="selectPeriod(period)"
        >
          {{ period }}
        </button>
      </div>
      <div class="timeline">
        <div class="timeline-ruler">
          <div class="ruler-line"></div>
          <div 
            v-for="(map, index) in historicalMaps" 
            :key="map.id"
            class="timeline-marker"
            :class="{ active: selectedMapId === map.id }"
            :style="{ left: `${(index / (historicalMaps.length - 1)) * 100}%` }"
            @click="selectMap(map.id)"
          >
            <div class="marker-dot"></div>
            <div class="marker-label">{{ map.year || '未知年份' }}</div>
          </div>
        </div>
        <!-- 增加时间轴范围指示器 -->
        <div class="timeline-years">
          <div class="timeline-start">{{ getEarliestYear() }}</div>
          <div class="timeline-end">{{ getLatestYear() }}</div>
        </div>
        <!-- 增加时间轴动画播放控制 -->
        <div class="timeline-controls">
          <button class="control-btn" @click="playTimelineAnimation" :disabled="isTimelineAnimating">
            <el-icon class="timeline-icon">
              <component :is="isTimelineAnimating ? 'VideoPause' : 'VideoPlay'"></component>
            </el-icon>
            {{ isTimelineAnimating ? '暂停' : '播放时间轴' }}
          </button>
          <div class="animation-speed" v-if="isTimelineAnimating">
            <span>速度:</span>
            <button 
              v-for="speed in [1, 2, 3]" 
              :key="speed"
              :class="{ active: animationSpeed === speed }"
              @click="animationSpeed = speed"
              class="speed-btn"
            >
              {{ speed }}x
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 地图展示区域 -->
    <div class="map-display-section">
      <div class="map-sidebar">
        <div class="map-controls">
          <h3>地图控制</h3>
          <div class="control-group">
            <label class="switch">
              <input 
                type="checkbox" 
                v-model="showModernMap"
                @change="updateMapLayers"
              >
              <span class="slider"></span>
              <span class="switch-label">
                <el-icon><Map /></el-icon>
                现代底图
              </span>
            </label>
          </div>
          
          <div class="control-group">
            <label class="switch">
              <input 
                type="checkbox" 
                v-model="showHistoricalMap"
                @change="updateMapLayers"
              >
              <span class="slider"></span>
              <span class="switch-label">
                <el-icon><Picture /></el-icon>
                历史地图
              </span>
            </label>
          </div>
          
          <div class="control-group">
            <label class="switch">
              <input 
                type="checkbox" 
                v-model="showMapPoints"
                @change="updateMapLayers"
              >
              <span class="slider"></span>
              <span class="switch-label">
                <el-icon><Location /></el-icon>
                兴趣点
              </span>
            </label>
          </div>
          
          <div class="control-group" v-if="showHistoricalMap">
            <label>
              <el-icon><Refresh /></el-icon>
              历史地图透明度
            </label>
            <input 
              type="range" 
              min="0" 
              max="1" 
              step="0.05" 
              v-model="historicalMapOpacity"
              @input="updateMapLayers"
              class="opacity-slider"
            >
            <div class="slider-value">{{ Math.round(historicalMapOpacity * 100) }}%</div>
          </div>
          
          <!-- 新增叠加方式选择 -->
          <div class="control-group" v-if="showHistoricalMap && showModernMap">
            <label>
              <el-icon><Operation /></el-icon>
              叠加方式
            </label>
            <div class="blend-mode-options">
              <button 
                v-for="mode in blendModes" 
                :key="mode.value"
                :class="{ active: blendMode === mode.value }"
                @click="setBlendMode(mode.value)"
                class="blend-mode-btn"
              >
                {{ mode.label }}
              </button>
            </div>
          </div>
        </div>
        
        <div class="map-info" v-if="selectedMap">
          <h3>{{ selectedMap.name }}</h3>
          <div class="info-period">{{ selectedMap.period }}</div>
          <div class="info-year">{{ selectedMap.year_range }}</div>
          <p class="info-description">{{ selectedMap.description }}</p>
          
          <div class="additional-info" v-if="selectedMap.additional_info">
            <h4>更多信息</h4>
            <p>{{ selectedMap.additional_info }}</p>
          </div>
          
          <div class="points-of-interest" v-if="mapPoints.length > 0">
            <h4>地图兴趣点 ({{ mapPoints.length }})</h4>
            <div class="point-list">
              <div 
                v-for="point in mapPoints" 
                :key="point.id"
                class="point-item"
                :class="{ active: selectedPointId === point.id }"
                @click="selectPoint(point)"
              >
                <div class="point-icon" v-if="point.icon_path">
                  <img :src="getImageUrl(point.icon_path)" :alt="point.name" @error="(e) => handleImageError(e, point)">
                </div>
                <div class="point-details">
                  <div class="point-name">{{ point.name }}</div>
                  <div class="point-type">{{ point.point_type }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="map-container" ref="mapContainer">
        <!-- 加载中提示 -->
        <div class="loading-overlay" v-if="isLoading">
          <div class="loading-spinner"></div>
          <div class="loading-text">地图加载中...</div>
        </div>
        
        <!-- 使用AMap地图组件 -->
        <div id="map-view" class="map-view"></div>
        
        <!-- 历史地图叠加层 -->
        <div 
          v-if="showHistoricalMap && selectedMap && selectedMap.image_path" 
          class="historical-map-overlay"
          :style="{ 
            opacity: historicalMapOpacity,
            mixBlendMode: blendMode
          }"
          :class="{ transitioning: isMapTransitioning }"
        >
          <img 
            :src="getImageUrl(selectedMap.image_path)" 
            :alt="selectedMap.name"
            @load="onHistoricalMapLoad"
          />
        </div>
        
        <!-- 点位信息卡片 -->
        <div class="point-info-card" v-if="selectedPoint">
          <div class="card-header">
            <h3>{{ selectedPoint.name }}</h3>
            <button class="close-btn" @click="clearSelectedPoint">×</button>
          </div>
          <div class="card-body">
            <div class="point-type-tag">{{ selectedPoint.point_type }}</div>
            <p>{{ selectedPoint.description }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 地图时期对比功能 -->
    <div class="map-comparison-section" v-if="historicalMaps.length > 1">
      <h2>地图时期对比</h2>
      <div class="comparison-controls">
        <div class="comparison-select">
          <label>对比地图 1</label>
          <select v-model="comparisonMapId1" @change="updateComparison">
            <option v-for="map in historicalMaps" :key="map.id" :value="map.id">
              {{ map.name }} ({{ map.period }})
            </option>
          </select>
        </div>
        <div class="comparison-select">
          <label>对比地图 2</label>
          <select v-model="comparisonMapId2" @change="updateComparison">
            <option v-for="map in historicalMaps" :key="map.id" :value="map.id">
              {{ map.name }} ({{ map.period }})
            </option>
          </select>
        </div>
        <button 
          class="comparison-btn" 
          @click="showComparison = true" 
          v-if="comparisonMapId1 && comparisonMapId2 && !showComparison"
        >
          开始对比
        </button>
        <button 
          class="comparison-btn close" 
          @click="showComparison = false" 
          v-if="showComparison"
        >
          关闭对比
        </button>
      </div>
      
      <div class="comparison-view" v-if="showComparison">
        <div class="comparison-map left">
          <h3>{{ getMapById(comparisonMapId1)?.name || '地图1' }}</h3>
          <div class="map-image">
            <img 
              :src="getImageUrl(getMapById(comparisonMapId1)?.image_path)" 
              :alt="getMapById(comparisonMapId1)?.name"
              @error="(e) => handleImageError(e, {name: getMapById(comparisonMapId1)?.name, image_path: getMapById(comparisonMapId1)?.image_path})"
            >
            <div class="map-year">{{ getMapById(comparisonMapId1)?.year_range }}</div>
          </div>
        </div>
        
        <div class="comparison-divider">
          <div class="arrow left"></div>
          <div class="timeline-bar"></div>
          <div class="arrow right"></div>
          <div class="time-diff" v-if="getYearDiff() !== null">
            <span>相距约</span>
            <strong>{{ getYearDiff() }}</strong>
            <span>年</span>
          </div>
        </div>
        
        <div class="comparison-map right">
          <h3>{{ getMapById(comparisonMapId2)?.name || '地图2' }}</h3>
          <div class="map-image">
            <img 
              :src="getImageUrl(getMapById(comparisonMapId2)?.image_path)" 
              :alt="getMapById(comparisonMapId2)?.name"
              @error="(e) => handleImageError(e, {name: getMapById(comparisonMapId2)?.name, image_path: getMapById(comparisonMapId2)?.image_path})"
            >
            <div class="map-year">{{ getMapById(comparisonMapId2)?.year_range }}</div>
          </div>
        </div>
      </div>
      
      <!-- 增加地图对比交互选项 -->
      <div class="comparison-options" v-if="showComparison">
        <div class="comparison-option">
          <label>对比模式</label>
          <div class="option-buttons">
            <button 
              v-for="mode in comparisonModes" 
              :key="mode.value"
              :class="{ active: comparisonMode === mode.value }"
              @click="comparisonMode = mode.value"
              class="option-btn"
            >
              {{ mode.label }}
            </button>
          </div>
        </div>
        
        <div class="comparison-feature" v-if="comparisonMode === 'slider'">
          <label>滑动对比</label>
          <div class="slider-container" ref="sliderContainer">
            <div class="slider-map slider-map-left">
              <img 
                :src="getImageUrl(getMapById(comparisonMapId1)?.image_path)" 
                :alt="getMapById(comparisonMapId1)?.name"
              >
            </div>
            <div 
              class="slider-map slider-map-right" 
              :style="{ width: `${100 - sliderPosition}%` }"
            >
              <img 
                :src="getImageUrl(getMapById(comparisonMapId2)?.image_path)" 
                :alt="getMapById(comparisonMapId2)?.name"
              >
            </div>
            <div 
              class="slider-divider" 
              :style="{ left: `${sliderPosition}%` }"
              @mousedown="startSliderDrag"
            >
              <div class="slider-handle"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import axios from 'axios';
import AMapLoader from '@amap/amap-jsapi-loader';
import { VideoPlay, VideoPause, Timer, Map, Location, Picture, Refresh, Operation } from '@element-plus/icons-vue';
import '../assets/map-animations.css'; // 导入动画样式

// 状态变量
const historicalMaps = ref([]);
const mapPoints = ref([]);
const periods = ref([]);
const selectedPeriod = ref('');
const selectedMapId = ref(null);
const selectedPointId = ref(null);
const showModernMap = ref(true);
const showHistoricalMap = ref(true);
const showMapPoints = ref(true);
const historicalMapOpacity = ref(0.7);
const mapInstance = ref(null);
const mapMarkers = ref([]);
const isLoading = ref(true);
const error = ref(null);

// 地图过渡动画状态
const isMapTransitioning = ref(false);

// 新增时间轴动画控制
const isTimelineAnimating = ref(false);
const animationSpeed = ref(2);
const animationInterval = ref(null);

// 新增混合模式
const blendMode = ref('normal');
const blendModes = [
  { label: '正常', value: 'normal' },
  { label: '叠加', value: 'multiply' },
  { label: '滤色', value: 'screen' },
  { label: '差值', value: 'difference' }
];

// 对比功能
const comparisonMapId1 = ref(null);
const comparisonMapId2 = ref(null);
const showComparison = ref(false);
const comparisonMode = ref('side');
const comparisonModes = [
  { label: '并排', value: 'side' },
  { label: '滑动', value: 'slider' }
];

// 滑动对比相关
const sliderPosition = ref(50);
const sliderDragging = ref(false);
const sliderContainer = ref(null);

// 点位信息
const selectedPoint = ref(null);

// 计算属性
const selectedMap = computed(() => {
  if (!selectedMapId.value) return null;
  return historicalMaps.value.find(map => map.id === selectedMapId.value);
});

const filteredMaps = computed(() => {
  if (!selectedPeriod.value) return historicalMaps.value;
  return historicalMaps.value.filter(map => map.period === selectedPeriod.value);
});

// 获取最早年份
const getEarliestYear = () => {
  if (historicalMaps.value.length === 0) return '';
  const years = historicalMaps.value
    .map(map => parseInt(map.year))
    .filter(year => !isNaN(year));
  return Math.min(...years) + '年';
};

// 获取最晚年份
const getLatestYear = () => {
  if (historicalMaps.value.length === 0) return '';
  const years = historicalMaps.value
    .map(map => parseInt(map.year))
    .filter(year => !isNaN(year));
  return Math.max(...years) + '年';
};

// 时间轴动画播放
const playTimelineAnimation = () => {
  if (isTimelineAnimating.value) {
    // 停止动画
    clearInterval(animationInterval.value);
    isTimelineAnimating.value = false;
  } else {
    // 开始动画
    isTimelineAnimating.value = true;
    
    // 从当前选中的地图开始，如果没有选中则从第一个开始
    let currentIndex = selectedMapId.value 
      ? historicalMaps.value.findIndex(m => m.id === selectedMapId.value)
      : 0;
      
    if (currentIndex === -1) currentIndex = 0;
    
    // 设置动画间隔
    animationInterval.value = setInterval(() => {
      currentIndex = (currentIndex + 1) % historicalMaps.value.length;
      selectMapWithTransition(historicalMaps.value[currentIndex].id);
      
      // 如果播放完一轮，暂停
      if (currentIndex === historicalMaps.value.length - 1) {
        setTimeout(() => {
          clearInterval(animationInterval.value);
          isTimelineAnimating.value = false;
        }, 1000);
      }
    }, 3000 / animationSpeed.value);
  }
};

// 监听动画速度变化
watch(animationSpeed, () => {
  if (isTimelineAnimating.value) {
    // 重启动画以应用新速度
    clearInterval(animationInterval.value);
    playTimelineAnimation();
  }
});

// 处理图片URL
const getImageUrl = (imagePath) => {
  if (!imagePath) {
    console.warn('图片路径为空');
    return null;
  }
  
  // 调试信息
  console.log('处理图片路径:', imagePath);
  
  if (imagePath.match(/^https?:\/\//)) {
    console.log('使用完整URL:', imagePath);
    return imagePath;
  }
  
  const fullUrl = `http://localhost:5000${imagePath}`;
  console.log('构建完整URL:', fullUrl);
  return fullUrl;
};

// 图片加载错误处理
const handleImageError = (event, item) => {
  console.error(`图片加载失败:`, {
    名称: item.name,
    路径: item.image_path || item.icon_path
  });
  event.target.src = 'https://via.placeholder.com/600x400?text=图片加载失败';
};

// 选择时期
const selectPeriod = (period) => {
  selectedPeriod.value = period;
  
  // 查找该时期的第一个地图
  const periodMap = historicalMaps.value.find(map => map.period === period);
  if (periodMap) {
    selectMapWithTransition(periodMap.id);
  }
};

// 根据ID获取地图
const getMapById = (id) => {
  if (!id) return null;
  return historicalMaps.value.find(map => map.id === id);
};

// 带过渡动画的地图选择
const selectMapWithTransition = async (mapId) => {
  // 如果是同一个地图，不做任何操作
  if (selectedMapId.value === mapId) return;
  
  // 开始过渡动画
  isMapTransitioning.value = true;
  
  // 设置过渡结束后的回调
  setTimeout(() => {
    // 实际切换地图
    selectedMapId.value = mapId;
    
    // 500ms后结束过渡动画
    setTimeout(() => {
      isMapTransitioning.value = false;
    }, 500);
  }, 300);
};

// 选择地图
const selectMap = async (mapId) => {
  selectMapWithTransition(mapId);
  
  const map = historicalMaps.value.find(m => m.id === mapId);
  if (map && mapInstance.value) {
    // 更新地图中心位置
    if (map.center_coordinate) {
      const [lng, lat] = map.center_coordinate.split(',');
      mapInstance.value.setCenter([parseFloat(lng), parseFloat(lat)]);
    }
    
    // 设置缩放级别
    if (map.zoom_level) {
      mapInstance.value.setZoom(map.zoom_level);
    }
    
    // 更新选中的时期
    selectedPeriod.value = map.period;
    
    // 获取地图点位
    await fetchMapPoints(mapId);
  }
};

// 选择兴趣点
const selectPoint = (point) => {
  selectedPoint.value = point;
  selectedPointId.value = point.id;
  
  // 如果有地图实例，则将地图中心移动到兴趣点位置
  if (mapInstance.value && point.coordinates) {
    const [lng, lat] = point.coordinates.split(',');
    mapInstance.value.setCenter([parseFloat(lng), parseFloat(lat)]);
    mapInstance.value.setZoom(15); // 放大以便查看详情
  }
};

// 清除选中的兴趣点
const clearSelectedPoint = () => {
  selectedPoint.value = null;
  selectedPointId.value = null;
};

// 更新地图图层
const updateMapLayers = () => {
  if (!mapInstance.value) return;
  
  // 处理现代地图显示
  if (showModernMap.value) {
    mapInstance.value.setFeatures(['bg', 'road', 'building', 'point']);
  } else {
    mapInstance.value.setFeatures([]);
  }
  
  // 更新地图标记点的显示状态
  if (mapMarkers.value.length > 0) {
    mapMarkers.value.forEach(marker => {
      if (showMapPoints.value) {
        marker.show();
      } else {
        marker.hide();
      }
    });
  }
};

// 更新对比视图
const updateComparison = () => {
  if (showComparison.value && (!comparisonMapId1.value || !comparisonMapId2.value)) {
    showComparison.value = false;
  }
};

// 历史地图加载完成
const onHistoricalMapLoad = (e) => {
  console.log('历史地图加载完成');
};

// 获取历史地图数据
const fetchHistoricalMaps = async () => {
  try {
    isLoading.value = true;
    console.log('开始获取历史地图数据...');
    
    // 先初始化数据
    try {
      console.log('尝试初始化历史地图数据...');
      const initResponse = await axios.get('http://localhost:5000/api/init-historical-maps');
      console.log('初始化历史地图数据响应:', initResponse.data);
    } catch (err) {
      console.error('初始化历史地图数据失败:', err.message);
      console.error('详细错误:', err);
      // 继续执行，因为数据可能已经初始化
    }
    
    // 获取地图数据
    console.log('获取历史地图数据...');
    const response = await axios.get('http://localhost:5000/api/historical-maps');
    console.log('历史地图数据API响应:', response);
    
    if (response.data && response.data.status === 'success') {
      historicalMaps.value = response.data.data || [];
      console.log('获取到的历史地图数据:', historicalMaps.value);
      
      // 如果有地图数据，自动选择第一个
      if (historicalMaps.value.length > 0) {
        const firstMap = historicalMaps.value[0];
        selectedMapId.value = firstMap.id;
        selectedPeriod.value = firstMap.period;
        console.log(`选择地图: ${firstMap.name}, ID: ${firstMap.id}, 时期: ${firstMap.period}`);
        
        // 设置对比默认值
        comparisonMapId1.value = historicalMaps.value[0].id;
        if (historicalMaps.value.length > 1) {
          comparisonMapId2.value = historicalMaps.value[historicalMaps.value.length - 1].id;
        }
      } else {
        console.warn('未获取到任何历史地图数据');
      }
      
      // 获取所有时期
      const uniquePeriods = [...new Set(historicalMaps.value.map(map => map.period))];
      periods.value = uniquePeriods;
      console.log('获取到的时期:', uniquePeriods);
    } else {
      console.error('获取历史地图数据失败, 响应:', response.data);
      throw new Error('获取历史地图数据失败: ' + JSON.stringify(response.data));
    }
  } catch (err) {
    console.error('获取历史地图数据出错:', err);
    error.value = `获取历史地图数据失败: ${err.message}`;
    
    // 添加错误详情
    if (err.response) {
      // 服务器响应了错误状态码
      console.error('服务器响应错误:', err.response.status, err.response.data);
    }
  } finally {
    isLoading.value = false;
  }
};

// 获取地图兴趣点数据
const fetchMapPoints = async (mapId) => {
  if (!mapId) {
    console.warn('未提供地图ID，无法获取兴趣点');
    return;
  }
  
  try {
    console.log(`获取地图ID=${mapId}的兴趣点`);
    
    // 清除现有标记
    if (mapMarkers.value.length > 0) {
      console.log('清除现有地图标记');
      mapMarkers.value.forEach(marker => {
        mapInstance.value.removeOverlay(marker);
      });
      mapMarkers.value = [];
    }
    
    const response = await axios.get(`http://localhost:5000/api/historical-maps/${mapId}/points`);
    console.log('地图兴趣点数据响应:', response.data);
    
    if (response.data && response.data.status === 'success') {
      // 保存兴趣点数据
      mapPoints.value = response.data.data || [];
      console.log(`获取到${mapPoints.value.length}个兴趣点`);
      
      // 如果有地图实例，添加标记
      if (mapInstance.value && mapPoints.value.length > 0) {
        console.log('向地图添加兴趣点标记');
        
        mapPoints.value.forEach(point => {
          if (!point.coordinates) {
            console.warn(`兴趣点"${point.name}"没有坐标信息，跳过`);
            return;
          }
          
          // 解析坐标
          const [lng, lat] = point.coordinates.split(',').map(Number);
          
          // 创建标记的自定义HTML元素
          const markerContent = document.createElement('div');
          markerContent.className = `map-point ${point.point_type.toLowerCase()}`;
          
          // 添加图标容器
          const iconContainer = document.createElement('div');
          iconContainer.className = 'point-icon-container';
          
          // 添加图标图片
          const iconImg = document.createElement('img');
          iconImg.src = getImageUrl(point.icon_path);
          iconImg.alt = point.name;
          iconImg.width = 32;
          iconImg.height = 32;
          iconImg.addEventListener('error', (e) => handleImageError(e, point));
          
          // 组装DOM
          iconContainer.appendChild(iconImg);
          markerContent.appendChild(iconContainer);
          
          // 创建自定义标记
          const marker = new AMap.Marker({
            position: [lng, lat],
            content: markerContent,
            title: point.name,
            offset: new AMap.Pixel(-16, -16),
            zIndex: 100
          });
          
          // 添加点击事件
          marker.on('click', () => {
            console.log(`点击兴趣点: ${point.name}`);
            selectPoint(point);
            
            // 添加选中样式
            mapMarkers.value.forEach(m => {
              if (m._content) {
                m._content.classList.remove('selected');
              }
            });
            markerContent.classList.add('selected');
            
            // 创建自定义信息窗口
            const infoWindow = new AMap.InfoWindow({
              content: createInfoWindowContent(point),
              offset: new AMap.Pixel(0, -32),
              isCustom: true
            });
            
            infoWindow.open(mapInstance.value, [lng, lat]);
          });
          
          // 添加到地图
          marker.setMap(mapInstance.value);
          
          // 保存到标记数组
          mapMarkers.value.push(marker);
        });
        
        console.log(`已添加${mapMarkers.value.length}个标记到地图`);
      }
    } else {
      console.error('获取兴趣点失败, 响应:', response.data);
      throw new Error('获取地图兴趣点失败');
    }
  } catch (err) {
    console.error(`获取地图兴趣点出错:`, err);
  }
};

// 创建信息窗口内容
const createInfoWindowContent = (point) => {
  const container = document.createElement('div');
  container.className = 'custom-info-window';
  
  const title = document.createElement('div');
  title.className = 'info-window-title';
  title.textContent = point.name;
  
  const body = document.createElement('div');
  body.className = 'info-window-body';
  
  // 添加类型
  const typeP = document.createElement('p');
  typeP.innerHTML = `<strong>类型:</strong> ${point.point_type}`;
  
  // 添加描述
  const descP = document.createElement('p');
  descP.innerHTML = point.description;
  
  body.appendChild(typeP);
  body.appendChild(descP);
  
  container.appendChild(title);
  container.appendChild(body);
  
  return container;
};

// 初始化高德地图
const initMap = async () => {
  try {
    console.log('开始初始化地图...');
    
    // 如果已经有地图实例，先销毁
    if (mapInstance.value) {
      console.log('销毁现有地图实例');
      mapInstance.value.destroy();
      mapInstance.value = null;
    }
    
    console.log('加载高德地图API...');
    const AMap = await AMapLoader.load({
      key: '这里需要替换为你的高德地图Web端开发者Key',  // 使用你的Web端开发者Key
      version: '2.0',
      plugins: ['AMap.ToolBar', 'AMap.Scale', 'AMap.HawkEye'],
      AMapUI: {
        version: '1.1',
        plugins: []
      },
      Loca: {
        version: '2.0.0'
      }
    });
    
    console.log('高德地图API加载成功，创建地图实例');
    
    // 创建地图实例
    mapInstance.value = new AMap.Map('map-view', {
      viewMode: '3D',
      zoom: 12,
      center: [116.397428, 39.90923],
      mapStyle: 'amap://styles/dark',
      pitch: 40,
      skyColor: '#141414'
    });
    
    console.log('地图实例创建成功:', mapInstance.value);
    
    // 添加控件
    mapInstance.value.addControl(new AMap.ToolBar());
    mapInstance.value.addControl(new AMap.Scale());
    
    // 如果有选中的地图，设置地图中心和缩放级别
    if (selectedMap.value) {
      console.log('根据选中的地图设置中心点和缩放级别');
      if (selectedMap.value.center_coordinate) {
        const [lng, lat] = selectedMap.value.center_coordinate.split(',');
        mapInstance.value.setCenter([parseFloat(lng), parseFloat(lat)]);
      }
      
      if (selectedMap.value.zoom_level) {
        mapInstance.value.setZoom(selectedMap.value.zoom_level);
      }
    }
    
    console.log('地图初始化完成');
    
    // 获取地图兴趣点
    if (selectedMapId.value) {
      console.log('获取选中地图的兴趣点');
      await fetchMapPoints(selectedMapId.value);
    }
    
    // 更新图层显示
    updateMapLayers();
    
  } catch (err) {
    console.error('初始化地图出错:', err);
    error.value = `初始化地图失败: ${err.message}`;
    
    if (err.message.includes('key')) {
      error.value += ' - 可能是地图API密钥无效或未设置';
    } else if (err.message.includes('jsapi')) {
      error.value += ' - 无法加载地图API，可能是网络问题或Content Security Policy限制';
    }
  } finally {
    isLoading.value = false;
  }
};

// 监听选中的地图变化
watch(selectedMapId, async (newMapId) => {
  if (newMapId && mapInstance.value) {
    const map = historicalMaps.value.find(m => m.id === newMapId);
    if (map && map.center_coordinate) {
      const [lng, lat] = map.center_coordinate.split(',');
      mapInstance.value.setCenter([parseFloat(lng), parseFloat(lat)]);
      
      if (map.zoom_level) {
        mapInstance.value.setZoom(map.zoom_level);
      }
    }
    
    // 更新地图点位
    await fetchMapPoints(newMapId);
  }
});

// 计算两个地图之间的年份差距
const getYearDiff = () => {
  const map1 = getMapById(comparisonMapId1.value);
  const map2 = getMapById(comparisonMapId2.value);
  
  if (!map1 || !map2 || !map1.year || !map2.year) return null;
  
  const year1 = parseInt(map1.year);
  const year2 = parseInt(map2.year);
  
  if (isNaN(year1) || isNaN(year2)) return null;
  
  return Math.abs(year1 - year2);
};

// 滑动对比的拖动处理
const startSliderDrag = (event) => {
  event.preventDefault();
  sliderDragging.value = true;
  
  const handleMouseMove = (moveEvent) => {
    if (!sliderDragging.value || !sliderContainer.value) return;
    
    const containerRect = sliderContainer.value.getBoundingClientRect();
    const containerWidth = containerRect.width;
    const offsetX = moveEvent.clientX - containerRect.left;
    
    // 计算百分比位置 (0-100)
    let newPosition = (offsetX / containerWidth) * 100;
    
    // 限制在 5-95% 范围内
    newPosition = Math.max(5, Math.min(95, newPosition));
    
    sliderPosition.value = newPosition;
  };
  
  const handleMouseUp = () => {
    sliderDragging.value = false;
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
  };
  
  document.addEventListener('mousemove', handleMouseMove);
  document.addEventListener('mouseup', handleMouseUp);
};

// 监听对比模式变化
watch(comparisonMode, (newMode) => {
  if (newMode === 'slider') {
    // 重置滑动位置
    sliderPosition.value = 50;
  }
});

// 组件挂载
onMounted(() => {
  console.log('历史地图组件已挂载，准备初始化...');
  
  // 初始化地图数据
  fetchHistoricalMaps().then(() => {
    // 初始化地图本身
    console.log('历史地图数据获取完成，准备初始化地图组件...');
    initMap();
  }).catch(err => {
    console.error('初始化过程出错:', err);
  });
});

// 组件卸载前
onBeforeUnmount(() => {
  // 销毁地图实例
  if (mapInstance.value) {
    mapInstance.value.destroy();
  }
  
  // 清除动画定时器
  if (animationInterval.value) {
    clearInterval(animationInterval.value);
  }
});

// 设置混合模式
const setBlendMode = (mode) => {
  blendMode.value = mode;
};

// 重试加载
const retryLoading = () => {
  console.log('重试加载历史地图数据...');
  error.value = null;
  fetchHistoricalMaps();
};
</script>

<style scoped>
.historical-map-view {
  color: white;
}

.header-section {
  text-align: center;
  margin-bottom: 3rem;
}

.header-section h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  color: #42b983;
  text-shadow: 0 0 15px rgba(66, 185, 131, 0.4);
}

.header-section p {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.8);
}

/* 时间轴样式 */
.timeline-section {
  margin-bottom: 3rem;
}

.timeline-section h2 {
  margin-bottom: 1.5rem;
  font-size: 1.8rem;
  color: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.timeline-section h2 .el-icon {
  color: #42b983;
  font-size: 1.5rem;
}

.period-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 2rem;
}

.period-filters button {
  padding: 0.8rem 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.period-filters button:hover {
  background: rgba(66, 185, 131, 0.2);
}

.period-filters button.active {
  background: #42b983;
  box-shadow: 0 0 15px rgba(66, 185, 131, 0.4);
}

.timeline {
  position: relative;
  padding: 2rem 0;
}

.timeline-ruler {
  position: relative;
  height: 60px;
  margin: 0 3rem;
}

.ruler-line {
  position: absolute;
  top: 30px;
  left: 0;
  right: 0;
  height: 4px;
  background: rgba(66, 185, 131, 0.5);
  border-radius: 2px;
}

.timeline-marker {
  position: absolute;
  transform: translateX(-50%);
  cursor: pointer;
  transition: all 0.3s ease;
}

.timeline-marker .marker-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: rgba(66, 185, 131, 0.8);
  margin: 22px auto 10px;
  transition: all 0.3s ease;
}

.timeline-marker .marker-label {
  white-space: nowrap;
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
  font-size: 0.9rem;
  transform: translateY(0);
  transition: all 0.3s ease;
}

.timeline-marker:hover .marker-dot,
.timeline-marker.active .marker-dot {
  background: #42b983;
  transform: scale(1.3);
  box-shadow: 0 0 10px rgba(66, 185, 131, 0.5);
}

.timeline-marker:hover .marker-label,
.timeline-marker.active .marker-label {
  color: white;
  transform: translateY(2px);
}

.timeline-years {
  display: flex;
  justify-content: space-between;
  margin: 0 3rem;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.timeline-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 1.5rem;
  gap: 1rem;
}

.control-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(66, 185, 131, 0.2);
  border: 1px solid rgba(66, 185, 131, 0.5);
  border-radius: 4px;
  color: #42b983;
  padding: 0.6rem 1.2rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.control-btn:hover:not(:disabled) {
  background: rgba(66, 185, 131, 0.3);
}

.control-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.timeline-icon {
  font-style: normal;
  font-size: 1.2rem;
  margin-right: 0.3rem;
}

.animation-speed {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: rgba(255, 255, 255, 0.8);
}

.speed-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 3px;
  color: rgba(255, 255, 255, 0.8);
  padding: 0.3rem 0.6rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.speed-btn.active {
  background: rgba(66, 185, 131, 0.3);
  color: #42b983;
}

/* 地图展示区域样式 */
.map-display-section {
  display: flex;
  gap: 2rem;
  margin-bottom: 3rem;
}

.map-sidebar {
  flex: 0 0 300px;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.map-controls {
  background: rgba(26, 31, 44, 0.8);
  border-radius: 12px;
  padding: 1.5rem;
}

.map-controls h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  font-size: 1.4rem;
  color: #42b983;
}

.control-group {
  margin-bottom: 1.5rem;
}

.control-group:last-child {
  margin-bottom: 0;
}

.switch {
  position: relative;
  display: flex;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: relative;
  width: 3rem;
  height: 1.5rem;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 34px;
  transition: .4s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 1.2rem;
  width: 1.2rem;
  left: 0.15rem;
  bottom: 0.15rem;
  background-color: white;
  border-radius: 50%;
  transition: .4s;
}

input:checked + .slider {
  background-color: #42b983;
}

input:checked + .slider:before {
  transform: translateX(1.5rem);
}

.switch-label {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.map-controls label {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1rem;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.opacity-slider {
  width: 100%;
  margin-top: 0.5rem;
  -webkit-appearance: none;
  height: 4px;
  border-radius: 2px;
  background: rgba(255, 255, 255, 0.2);
  outline: none;
}

.opacity-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #42b983;
  cursor: pointer;
}

.slider-value {
  margin-top: 0.5rem;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  text-align: center;
}

.map-info {
  background: rgba(26, 31, 44, 0.8);
  border-radius: 12px;
  padding: 1.5rem;
}

.map-info h3 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  font-size: 1.4rem;
  color: #42b983;
}

.info-period, .info-year {
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.info-description {
  margin-top: 1rem;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
}

.additional-info {
  margin-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 1.5rem;
}

.additional-info h4 {
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.8);
}

.points-of-interest {
  margin-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 1.5rem;
}

.points-of-interest h4 {
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.8);
}

.point-list {
  max-height: 300px;
  overflow-y: auto;
}

.point-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.8rem;
  border-radius: 8px;
  transition: all 0.3s ease;
  cursor: pointer;
  margin-bottom: 0.5rem;
}

.point-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.point-item.active {
  background: rgba(66, 185, 131, 0.2);
  border-left: 3px solid #42b983;
}

.point-icon {
  width: 30px;
  height: 30px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.point-icon img {
  max-width: 100%;
  max-height: 100%;
}

.point-details {
  flex: 1;
}

.point-name {
  font-weight: bold;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 0.3rem;
}

.point-type {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
}

.map-container {
  flex: 1;
  position: relative;
  height: 600px;
  border-radius: 12px;
  overflow: hidden;
}

.map-view {
  width: 100%;
  height: 100%;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(26, 31, 44, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 3px solid rgba(66, 185, 131, 0.3);
  border-radius: 50%;
  border-top-color: #42b983;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.1rem;
}

.historical-map-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  transition: opacity 0.5s ease;
  z-index: 10;
}

.historical-map-overlay.transitioning {
  opacity: 0 !important;
}

.historical-map-overlay img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.point-info-card {
  position: absolute;
  bottom: 20px;
  left: 20px;
  background: rgba(26, 31, 44, 0.9);
  border-radius: 8px;
  width: 300px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  z-index: 5;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.card-header h3 {
  margin: 0;
  font-size: 1.2rem;
  color: #42b983;
}

.close-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.5rem;
  cursor: pointer;
  line-height: 1;
}

.close-btn:hover {
  color: #ff6b6b;
}

.card-body {
  padding: 1rem;
}

.point-type-tag {
  display: inline-block;
  padding: 0.3rem 0.8rem;
  background: rgba(66, 185, 131, 0.2);
  border-radius: 4px;
  color: #42b983;
  font-size: 0.8rem;
  margin-bottom: 1rem;
}

/* 地图对比功能样式增强 */
.map-comparison-section {
  margin-top: 3rem;
  margin-bottom: 3rem;
  padding: 2rem;
  background: rgba(26, 31, 44, 0.6);
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
}

.map-comparison-section h2 {
  margin-bottom: 1.5rem;
  font-size: 1.8rem;
  color: rgba(255, 255, 255, 0.9);
  border-bottom: 1px solid rgba(66, 185, 131, 0.3);
  padding-bottom: 0.8rem;
}

.comparison-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  margin-bottom: 2rem;
  align-items: flex-end;
}

.comparison-select {
  flex: 1;
  min-width: 200px;
}

.comparison-select label {
  display: block;
  margin-bottom: 0.5rem;
  color: rgba(255, 255, 255, 0.8);
}

.comparison-select select {
  width: 100%;
  padding: 0.8rem;
  background: rgba(26, 31, 44, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: white;
  outline: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.comparison-select select:hover {
  border-color: rgba(66, 185, 131, 0.5);
}

.comparison-btn {
  padding: 0.8rem 1.5rem;
  background: #42b983;
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 120px;
}

.comparison-btn:hover {
  background: #3aa876;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(66, 185, 131, 0.3);
}

.comparison-btn.close {
  background: #ff6b6b;
}

.comparison-btn.close:hover {
  background: #ff5252;
  box-shadow: 0 4px 12px rgba(255, 82, 82, 0.3);
}

.comparison-view {
  display: flex;
  gap: 2rem;
  align-items: center;
  height: 400px;
  margin-bottom: 2rem;
}

.comparison-map {
  flex: 1;
  height: 100%;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(26, 31, 44, 0.8);
  position: relative;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
  transition: all 0.3s ease;
}

.comparison-map:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.35);
}

.comparison-map h3 {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  margin: 0;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.5);
  font-size: 1.2rem;
  color: white;
  z-index: 2;
}

.map-image {
  width: 100%;
  height: 100%;
  position: relative;
}

.map-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.map-year {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 0.8rem;
  background: rgba(0, 0, 0, 0.5);
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.9);
  text-align: center;
}

.comparison-divider {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.timeline-bar {
  width: 4px;
  height: 150px;
  background: rgba(66, 185, 131, 0.5);
  position: relative;
}

.arrow {
  width: 0;
  height: 0;
  border-style: solid;
}

.arrow.left {
  border-width: 8px 12px 8px 0;
  border-color: transparent rgba(66, 185, 131, 0.8) transparent transparent;
}

.arrow.right {
  border-width: 8px 0 8px 12px;
  border-color: transparent transparent transparent rgba(66, 185, 131, 0.8);
}

.time-diff {
  background: rgba(66, 185, 131, 0.2);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.time-diff strong {
  color: #42b983;
  font-size: 1.1rem;
}

/* 对比选项样式 */
.comparison-options {
  background: rgba(26, 31, 44, 0.5);
  padding: 1.5rem;
  border-radius: 8px;
  margin-top: 1rem;
}

.comparison-option {
  margin-bottom: 1.5rem;
}

.comparison-option label,
.comparison-feature label {
  display: block;
  margin-bottom: 0.8rem;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.option-buttons {
  display: flex;
  gap: 1rem;
}

.option-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.8);
  padding: 0.6rem 1.2rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.option-btn.active {
  background: rgba(66, 185, 131, 0.3);
  color: #42b983;
}

/* 滑动对比样式 */
.slider-container {
  position: relative;
  width: 100%;
  height: 400px;
  overflow: hidden;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
  cursor: col-resize;
}

.slider-map {
  position: absolute;
  top: 0;
  bottom: 0;
  overflow: hidden;
}

.slider-map-left {
  left: 0;
  right: 0;
  z-index: 1;
}

.slider-map-right {
  right: 0;
  z-index: 2;
}

.slider-map img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.slider-divider {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 4px;
  background: rgba(66, 185, 131, 0.8);
  z-index: 3;
  transform: translateX(-50%);
  cursor: col-resize;
}

.slider-handle {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 36px;
  height: 36px;
  background: #42b983;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  cursor: col-resize;
}

.slider-handle::before,
.slider-handle::after {
  content: '';
  position: absolute;
  background: rgba(255, 255, 255, 0.8);
  width: 2px;
  height: 14px;
}

.slider-handle::before {
  left: 12px;
}

.slider-handle::after {
  right: 12px;
}

/* 响应式设计增强 */
@media (max-width: 1200px) {
  .map-display-section {
    flex-direction: column;
  }
  
  .map-sidebar {
    flex: none;
    width: 100%;
  }
  
  .map-controls, .map-info {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .comparison-view {
    flex-direction: column;
    height: auto;
  }
  
  .comparison-map {
    height: 300px;
  }
  
  .comparison-divider {
    flex-direction: row;
    width: 100%;
    margin: 1rem 0;
  }
  
  .timeline-bar {
    width: 150px;
    height: 4px;
  }
  
  .arrow.left {
    border-width: 12px 8px 0 8px;
    border-color: rgba(66, 185, 131, 0.8) transparent transparent transparent;
  }
  
  .arrow.right {
    border-width: 0 8px 12px 8px;
    border-color: transparent transparent rgba(66, 185, 131, 0.8) transparent;
  }
  
  .slider-container {
    height: 300px;
  }
}

/* 错误提示样式 */
.error-message {
  margin-bottom: 2rem;
}

.error-details {
  margin-top: 1rem;
}

.retry-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
  background: #f56c6c;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  background: #e64242;
}
</style> 