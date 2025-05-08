<template>
  <div id="three-container"></div>
</template>

<script setup>
import { onMounted, onBeforeUnmount } from 'vue'
import * as THREE from 'three'

let scene, camera, renderer, particles

const init = () => {
  // 创建场景
  scene = new THREE.Scene()

  // 创建相机
  camera = new THREE.PerspectiveCamera(
    75,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
  )
  camera.position.z = 5

  // 创建渲染器
  renderer = new THREE.WebGLRenderer({ alpha: true })
  renderer.setSize(window.innerWidth, window.innerHeight)
  document.getElementById('three-container').appendChild(renderer.domElement)

  // 创建粒子系统
  const geometry = new THREE.BufferGeometry()
  const vertices = []

  for (let i = 0; i < 5000; i++) {
    const x = Math.random() * 2000 - 1000
    const y = Math.random() * 2000 - 1000
    const z = Math.random() * 2000 - 1000
    vertices.push(x, y, z)
  }

  geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3))

  const material = new THREE.PointsMaterial({
    color: 0x42b983,
    size: 2,
    transparent: true,
    opacity: 0.8
  })

  particles = new THREE.Points(geometry, material)
  scene.add(particles)

  // 添加窗口大小变化监听
  window.addEventListener('resize', onWindowResize)
}

const animate = () => {
  requestAnimationFrame(animate)

  particles.rotation.x += 0.001
  particles.rotation.y += 0.001

  renderer.render(scene, camera)
}

const onWindowResize = () => {
  camera.aspect = window.innerWidth / window.innerHeight
  camera.updateProjectionMatrix()
  renderer.setSize(window.innerWidth, window.innerHeight)
}

onMounted(() => {
  init()
  animate()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onWindowResize)
})
</script>

<style scoped>
#three-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  pointer-events: none;
}
</style> 