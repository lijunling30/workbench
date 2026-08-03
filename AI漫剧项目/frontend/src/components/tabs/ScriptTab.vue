<template>
  <div class="space-y-4">
    <div v-for="s in scripts" :key="s.id" class="panel">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-medium">剧本 · {{ s.scenes.length }} 场</h3>
        <button class="btn-primary !text-xs" @click="toShots(s)">生成分镜 →</button>
      </div>

      <!-- 情绪曲线 -->
      <div class="flex items-end gap-1 mb-5 h-16 bg-abyss-900/60 rounded-xl p-3">
        <div v-for="c in s.emotion_curve" :key="c.scene_no" class="flex-1 flex flex-col items-center gap-1">
          <span class="text-[9px] text-gray-500">{{ c.emotion }}</span>
          <div
            class="w-full rounded-t transition-all"
            :style="{ height: `${22 + (c.scene_no % 5) * 8}px` }"
            :class="c.emotion.includes('紧张') || c.emotion.includes('虐') ? 'bg-red-500/40' : 'bg-brand-violet/50'"
          />
          <span class="text-[9px] text-gray-600">S{{ c.scene_no }}</span>
        </div>
      </div>

      <!-- 场景 -->
      <div class="space-y-3">
        <div v-for="sc in s.scenes" :key="sc.no" class="bg-abyss-900/60 rounded-xl p-4">
          <div class="flex items-center gap-2 mb-2">
            <span class="text-[10px] px-2 py-0.5 rounded-full bg-brand-violet/15 text-brand-violet">S{{ sc.no }}</span>
            <span class="text-sm text-gray-300">{{ sc.location }}</span>
            <span class="text-xs text-gray-500">· {{ sc.emotion }}</span>
          </div>
          <p class="text-xs text-gray-500 mb-2">{{ sc.narration }}</p>
          <div v-for="(d, i) in sc.dialogue" :key="i" class="text-sm mb-1">
            <span class="text-brand-cyan">{{ d.character }}：</span>
            <span class="text-gray-300">{{ d.line }}</span>
          </div>
        </div>
      </div>
    </div>
    <p v-if="!scripts.length" class="text-center text-gray-600 text-sm py-12">
      暂无剧本 —— 在「AI 小说」页点击「转为剧本」
    </p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAppStore } from '../../stores/app'
import { api } from '../../api'

const props = defineProps({ projectId: Number })
const app = useAppStore()
const scripts = ref([])

async function load() {
  const novels = await api.get(`/content/projects/${props.projectId}/novels`)
  const arr = []
  for (const n of novels) {
    arr.push(...(await api.get(`/content/novels/${n.id}/scripts`)))
  }
  scripts.value = arr
}

async function toShots(s) {
  const before = app.confirmQueue.length
  await app.aiRequest('shot', `将剧本拆解为分镜镜头`, { script_id: s.id, project_id: props.projectId }, { min: 0.02, max: 0.1, desc: '约 9 个镜头' })
  if (app.confirmQueue.length === before) load()
}

onMounted(load)
</script>
