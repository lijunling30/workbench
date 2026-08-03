<template>
  <div class="space-y-4">
    <div class="panel">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-medium">分镜时间线</h3>
        <span class="text-xs text-gray-500">{{ shots.length }} 个镜头 · 点击卡片抽卡</span>
      </div>

      <!-- 分镜卡片流 -->
      <div class="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
        <div
          v-for="s in shots"
          :key="s.id"
          class="group rounded-xl border border-white/10 bg-abyss-900/60 p-3 cursor-pointer transition-all hover:border-brand-violet/40"
          :class="selected?.id === s.id ? 'border-brand-violet/60 shadow-glow' : ''"
          @click="select(s)"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-mono text-brand-violet">#{{ s.shot_no }}</span>
            <span class="text-[10px] px-1.5 py-0.5 rounded-full" :class="statusCls(s.status)">{{ statusText(s.status) }}</span>
          </div>
          <div class="text-xs text-gray-400 mb-1">
            {{ s.shot_type }} · {{ s.camera_move }} · {{ s.duration }}s
          </div>
          <p class="text-[11px] text-gray-500 line-clamp-2 leading-relaxed">{{ s.prompt_zh }}</p>
        </div>
      </div>
    </div>

    <!-- 选中镜头的抽卡面板 -->
    <div v-if="selected" class="panel">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-medium">镜头 #{{ selected.shot_no }} · 关键帧抽卡</h3>
        <button class="btn-primary !text-xs" @click="draw" :disabled="busy">
          {{ busy ? '生成中…' : keyframes.length ? '再抽一轮' : '抽卡' }}
        </button>
      </div>

      <!-- 抽卡九宫格（PRD A-1） -->
      <div class="grid grid-cols-3 gap-3">
        <div
          v-for="kf in keyframes"
          :key="kf.id"
          class="relative rounded-xl overflow-hidden border transition-all cursor-pointer"
          :class="kf.is_approved ? 'border-brand-cyan shadow-glow' : 'border-white/10 hover:border-brand-violet/40'"
          @click="approve(kf)"
        >
          <img :src="kf.image_url" class="w-full aspect-[9/16] object-cover" alt="关键帧候选" />
          <div class="absolute top-2 left-2 flex items-center gap-1">
            <span class="text-[10px] px-1.5 py-0.5 rounded bg-black/60 backdrop-blur text-amber-300 font-mono">AI {{ kf.score }}</span>
            <span v-if="kf.is_approved" class="text-[10px] px-1.5 py-0.5 rounded bg-brand-cyan text-white">已选</span>
          </div>
        </div>
        <div
          v-for="i in (3 - keyframes.length)"
          :key="'ph' + i"
          class="aspect-[9/16] rounded-xl border border-dashed border-white/10 grid place-items-center text-gray-600 text-xs"
        >候选中</div>
      </div>

      <!-- 视频生成 -->
      <div v-if="approvedKeyframe" class="mt-5 flex items-center gap-3">
        <button class="btn-primary" @click="genVideo" :disabled="videoBusy">
          {{ videoBusy ? '生成中…' : '生成镜头视频（Vidu）' }}
        </button>
        <span class="text-xs text-gray-500">时长 {{ selected.duration }}s · 预计 ¥{{ (selected.duration * 0.5).toFixed(1) }}</span>
      </div>

      <!-- 视频结果 -->
      <div v-if="videos.length" class="mt-4 grid grid-cols-2 gap-3">
        <div v-for="v in videos" :key="v.id" class="bg-abyss-900/60 rounded-xl p-3">
          <div class="flex items-center gap-2 text-xs mb-1">
            <span class="text-brand-violet">{{ v.vendor }}</span>
            <span class="text-gray-500">{{ v.status }}</span>
            <span class="text-gray-600 font-mono">¥{{ v.cost }}</span>
          </div>
          <div class="aspect-video bg-black rounded-lg grid place-items-center text-gray-600 text-xs">视频占位（{{ selected.duration }}s）</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAppStore } from '../../stores/app'
import { api } from '../../api'

const props = defineProps({ projectId: Number })
const app = useAppStore()
const shots = ref([])
const selected = ref(null)
const keyframes = ref([])
const videos = ref([])
const busy = ref(false)
const videoBusy = ref(false)

const approvedKeyframe = computed(() => keyframes.value.find((k) => k.is_approved))
const statusText = (s) => ({ draft: '待抽卡', keyframed: '已抽卡', video_ready: '可生成' }[s] || s)
const statusCls = (s) => ({
  draft: 'bg-gray-500/15 text-gray-400',
  keyframed: 'bg-brand-violet/15 text-brand-violet',
  video_ready: 'bg-brand-cyan/15 text-brand-cyan',
}[s] || 'bg-gray-500/15 text-gray-400')

async function loadShots() {
  const novels = await api.get(`/content/projects/${props.projectId}/novels`)
  const arr = []
  for (const n of novels) {
    for (const sc of await api.get(`/content/novels/${n.id}/scripts`)) {
      arr.push(...(await api.get(`/content/scripts/${sc.id}/shots`)))
    }
  }
  shots.value = arr
}

async function select(s) {
  selected.value = s
  keyframes.value = await api.get(`/assets/shots/${s.id}/keyframes`)
  videos.value = await api.get(`/assets/shots/${s.id}/videos`)
}

async function draw() {
  busy.value = true
  try {
    const before = app.confirmQueue.length
    await app.aiRequest('keyframe', `为镜头 #${selected.value.shot_no} 生成 3 张候选关键帧`,
      { shot_id: selected.value.id, count: 3, project_id: props.projectId },
      { min: 0.3, max: 0.9, desc: '3 张关键帧' })
    if (app.confirmQueue.length === before) keyframes.value = await api.get(`/assets/shots/${selected.value.id}/keyframes`)
  } finally {
    busy.value = false
  }
}

async function approve(kf) {
  await api.post(`/assets/keyframes/${kf.id}/approve`)
  keyframes.value = await api.get(`/assets/shots/${selected.value.id}/keyframes`)
}

async function genVideo() {
  videoBusy.value = true
  try {
    const before = app.confirmQueue.length
    await app.aiRequest('video', `为镜头 #${selected.value.shot_no} 生成 ${selected.value.duration}s 视频`,
      { shot_id: selected.value.id, keyframe_id: approvedKeyframe.value?.id, vendor: 'vidu', project_id: props.projectId },
      { min: selected.value.duration * 0.5, max: selected.value.duration * 0.5, desc: '镜头视频' })
    if (app.confirmQueue.length === before) {
      videos.value = await api.get(`/assets/shots/${selected.value.id}/videos`)
      loadShots()
    }
  } finally {
    videoBusy.value = false
  }
}

// 确认卡确认后刷新
watch(() => app.confirmQueue.length, async (n, o) => {
  if (o > 0 && n === 0) {
    if (selected.value) {
      keyframes.value = await api.get(`/assets/shots/${selected.value.id}/keyframes`)
      videos.value = await api.get(`/assets/shots/${selected.value.id}/videos`)
    }
    loadShots()
  }
})

onMounted(loadShots)
</script>
