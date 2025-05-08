<template>
  <div class="video-player">
    <video
      ref="videoRef"
      class="video-element"
      :src="src"
      :poster="poster"
      :autoplay="autoplay"
      :muted="muted"
      :loop="loop"
      :controls="controls"
      :class="{ 'visible': loaded }"
      @loadeddata="handleLoaded"
      @timeupdate="handleTimeUpdate"
      @ended="handleEnded"
      @error="handleError"
      crossorigin="anonymous"
    ></video>
    
    <div class="loading-indicator" v-if="!loaded && !error">
      <div class="spinner"></div>
      <span>加载中...</span>
    </div>
    
    <div class="error-indicator" v-if="error">
      <i class="el-icon-warning-outline"></i>
      <span>视频加载失败</span>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue';

const props = defineProps({
  src: {
    type: String,
    required: true
  },
  poster: {
    type: String,
    default: ''
  },
  autoplay: {
    type: Boolean,
    default: false
  },
  muted: {
    type: Boolean,
    default: true
  },
  loop: {
    type: Boolean,
    default: false
  },
  controls: {
    type: Boolean,
    default: false
  },
  playbackRate: {
    type: Number,
    default: 1
  }
});

const emit = defineEmits(['loaded', 'error', 'timeupdate', 'ended']);

const videoRef = ref(null);
const loaded = ref(false);
const error = ref(false);
const currentTime = ref(0);

// 向父组件暴露视频元素和方法
defineExpose({
  videoElement: videoRef,
  play: () => {
    if (videoRef.value) {
      videoRef.value.play().catch(e => {
        console.error('无法播放视频:', e);
        error.value = true;
        emit('error', e);
      });
    }
  },
  pause: () => {
    if (videoRef.value) {
      videoRef.value.pause();
    }
  },
  stop: () => {
    if (videoRef.value) {
      videoRef.value.pause();
      videoRef.value.currentTime = 0;
    }
  },
  getCurrentTime: () => currentTime.value,
  getDuration: () => videoRef.value?.duration || 0,
  setCurrentTime: (time) => {
    if (videoRef.value) {
      videoRef.value.currentTime = time;
    }
  }
});

const handleLoaded = () => {
  console.log('视频加载成功:', props.src);
  loaded.value = true;
  error.value = false;
  emit('loaded');
  
  // 设置播放速度
  if (videoRef.value && props.playbackRate !== 1) {
    videoRef.value.playbackRate = props.playbackRate;
  }
  
  // 如果设置了自动播放，确保视频开始播放
  if (videoRef.value) {
    console.log('视频已加载，尝试立即播放视频');
    videoRef.value.play()
      .then(() => console.log('播放已启动'))
      .catch(e => {
        console.warn('播放失败，这可能是由于浏览器策略导致的:', e);
        console.log('尝试使用静音播放...');
        // 静音播放通常不受浏览器自动播放策略限制
        if (videoRef.value) {
          videoRef.value.muted = true;
          videoRef.value.play()
            .then(() => console.log('静音播放成功'))
            .catch(e2 => console.error('静音播放也失败了:', e2));
        }
      });
  }
};

// 添加备用视频源尝试逻辑
const tryFallbackSources = () => {
  if (!props.src) return;
  
  // 构建备用URL路径
  const originalUrl = props.src;
  const filename = originalUrl.split('/').pop();
  
  // 尝试不同的路径模式
  const fallbackUrls = [
    `/videos/${filename}`,
    `/static/mv展示/${filename}`,
    `../static/mv展示/${filename}`,
    `../../static/mv展示/${filename}`,
    `static/mv展示/${filename}`,
    `http://localhost:5000/videos/${filename}`,
    `http://localhost:5173/static/mv展示/${filename}`
  ];
  
  console.log('尝试备用视频源...');
  
  // 测试每个备用URL
  Promise.all(
    fallbackUrls.map(url => 
      fetch(url, { method: 'HEAD' })
        .then(res => ({ url, status: res.status }))
        .catch(() => ({ url, status: 500 }))
    )
  ).then(results => {
    // 找到第一个可用的URL
    const validSource = results.find(r => r.status === 200);
    if (validSource) {
      console.log('找到有效的备用视频源:', validSource.url);
      if (videoRef.value) {
        videoRef.value.src = validSource.url;
        videoRef.value.load();
        
        // 重新加载后尝试播放
        if (props.autoplay) {
          console.log('重新加载后尝试播放');
          setTimeout(() => {
            videoRef.value.play()
              .then(() => console.log('备用源播放成功'))
              .catch(e => console.error('备用源播放失败:', e));
          }, 100);
        }
      }
    } else {
      console.error('所有备用视频源都不可用');
      // 最后尝试直接向用户显示一个错误
      error.value = true;
    }
  });
};

const handleTimeUpdate = (event) => {
  currentTime.value = videoRef.value.currentTime;
  emit('timeupdate', {
    currentTime: currentTime.value,
    duration: videoRef.value.duration,
    percentage: (currentTime.value / videoRef.value.duration) * 100
  });
};

const handleEnded = () => {
  console.log('视频播放已结束，触发ended事件');
  
  // 如果设置了循环播放，就不触发ended事件，让视频自动循环播放
  if (!props.loop) {
    // 通知父组件视频已结束
    emit('ended');
  } else {
    console.log('视频设置了循环播放，不触发ended事件');
  }
};

const handleError = (err) => {
  error.value = true;
  console.error('视频加载错误:', err);
  console.error('视频源:', props.src);
  
  // 尝试使用fetch测试视频资源是否可访问
  if (props.src) {
    fetch(props.src, { method: 'HEAD' })
      .then(response => {
        console.log('视频资源状态:', response.status, response.statusText);
        if (!response.ok) {
          console.error('视频资源不可访问:', response.status, response.statusText);
          // 尝试备用源
          tryFallbackSources();
        }
      })
      .catch(fetchErr => {
        console.error('视频资源请求失败:', fetchErr);
        // 尝试备用源
        tryFallbackSources();
      });
  }
  
  emit('error', err);
};

// 监听 src 变化
watch(() => props.src, (newSrc) => {
  console.log('视频源变更为:', newSrc);
  loaded.value = false;
  error.value = false;
  
  // 如果视频元素已经存在，则重置并重新加载
  if (videoRef.value) {
    console.log('重新加载视频');
    videoRef.value.load();
    
    // 在src更改后短暂延迟尝试播放，确保DOM已更新
    if (props.autoplay) {
      setTimeout(() => {
        console.log('src变更后尝试播放');
        videoRef.value.play()
          .then(() => console.log('src变更后播放成功'))
          .catch(e => {
            console.error('src变更后播放失败:', e);
            tryFallbackSources();
          });
      }, 100);
    }
  }
});

// 监听播放速度变化
watch(() => props.playbackRate, (newRate) => {
  if (videoRef.value) {
    videoRef.value.playbackRate = newRate;
  }
});

onMounted(() => {
  // 确保视频元素正确配置
  if (videoRef.value) {
    console.log('VideoPlayer组件挂载，设置视频源:', props.src);
    videoRef.value.load();
    
    // 添加视频事件监听器，用于调试
    videoRef.value.addEventListener('canplay', () => {
      console.log('视频可以播放了');
      // 尝试自动播放
      if (videoRef.value && videoRef.value.paused) {
        videoRef.value.play()
          .then(() => console.log('canplay事件后自动播放成功'))
          .catch(e => console.warn('canplay事件后自动播放失败:', e));
      }
    });
    
    videoRef.value.addEventListener('playing', () => {
      console.log('视频开始播放');
    });
    
    videoRef.value.addEventListener('pause', () => {
      console.log('视频暂停');
    });
    
    videoRef.value.addEventListener('ended', () => {
      console.log('视频播放结束 - 从原生事件');
      // 确保ended事件被正确触发
      handleEnded();
    });
    
    videoRef.value.addEventListener('stalled', () => {
      console.warn('视频播放停滞');
      // 尝试恢复播放
      setTimeout(() => {
        if (videoRef.value && videoRef.value.paused) {
          videoRef.value.play()
            .then(() => console.log('stalled事件后恢复播放成功'))
            .catch(e => console.warn('stalled事件后恢复播放失败:', e));
        }
      }, 1000);
    });
    
    // 添加定时检查，确保视频真的在播放
    const checkInterval = setInterval(() => {
      if (videoRef.value) {
        if (!videoRef.value.paused && videoRef.value.currentTime > 0) {
          console.log('视频确认正在播放，当前时间:', videoRef.value.currentTime, '总时长:', videoRef.value.duration);
          
          // 检查视频是否真的结束了但没有触发ended事件
          if (videoRef.value.currentTime > 0 && videoRef.value.duration > 0) {
            // 如果时间大于总时长-0.5秒，可能表示视频已经结束，但事件未触发
            if (videoRef.value.currentTime >= videoRef.value.duration - 0.5) {
              console.log('检测到视频实际已结束，手动触发ended事件');
              videoRef.value.pause();  // 先暂停视频
              videoRef.value.currentTime = videoRef.value.duration;  // 将时间设置到末尾
              handleEnded();  // 手动触发结束事件
            }
            // 如果视频接近结束，提前触发时间更新，确保父组件知道进度
            else if ((videoRef.value.currentTime / videoRef.value.duration) > 0.95) {
              console.log('视频接近结束，发送最新进度');
              handleTimeUpdate();
            }
          }
        } else if (videoRef.value.paused && !props.loop) {
          // 如果视频已暂停，且不是循环模式，检查是否已到末尾
          if (videoRef.value.duration > 0 && 
              Math.abs(videoRef.value.currentTime - videoRef.value.duration) < 0.5) {
            console.log('视频已暂停且位于结束位置，触发ended事件');
            handleEnded();
          } else if (props.autoplay) {
            // 如果配置了自动播放但视频已暂停，尝试重新播放
            console.warn('视频当前已暂停，尝试重新播放');
            videoRef.value.play().catch(e => console.error('重新播放失败:', e));
          }
        }
      }
    }, 1000);
    
    // 延长定时检查为60秒，确保即使循环播放也能正确监控状态
    setTimeout(() => {
      console.log('结束视频状态定时检查');
      clearInterval(checkInterval);
    }, 60000);
    
    // 使用用户交互事件尝试播放视频
    const userInteractionHandler = () => {
      if (videoRef.value && videoRef.value.paused) {
        console.log('检测到用户交互，尝试播放视频');
        videoRef.value.play()
          .then(() => {
            console.log('用户交互后视频播放成功');
            // 成功后移除事件监听器
            document.removeEventListener('click', userInteractionHandler);
            document.removeEventListener('touchstart', userInteractionHandler);
            document.removeEventListener('keydown', userInteractionHandler);
          })
          .catch(e => console.warn('用户交互后视频播放失败:', e));
      }
    };
    
    document.addEventListener('click', userInteractionHandler);
    document.addEventListener('touchstart', userInteractionHandler);
    document.addEventListener('keydown', userInteractionHandler);
  }
});

onBeforeUnmount(() => {
  // 清理资源
  if (videoRef.value) {
    videoRef.value.pause();
    videoRef.value.src = '';
    videoRef.value.load();
  }
});
</script>

<style scoped>
.video-player {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.video-element {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0;
  transition: opacity 0.5s ease;
}

.video-element.visible {
  opacity: 1;
}

.loading-indicator,
.error-indicator {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  gap: 10px;
  z-index: 10;
}

.error-indicator {
  background: rgba(0, 0, 0, 0.8);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top-color: #42b983;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.error-indicator i {
  font-size: 2rem;
  color: #f56c6c;
}

.error-indicator span {
  font-size: 1rem;
  text-align: center;
  max-width: 80%;
  margin-top: 10px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style> 