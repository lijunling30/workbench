<template>
  <router-view />
  <!-- 确认闸口：全局确认卡浮层 -->
  <div
    v-if="store.confirmQueue.length"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
    @click.self="store.removeFromQueue(store.confirmQueue[0].id)"
  >
    <TransitionGroup name="pop">
      <div
        v-for="card in store.confirmQueue"
        :key="card.id"
        class="glass w-[440px] max-w-[92vw] p-6"
      >
        <div class="flex items-center gap-2 mb-1">
          <span class="w-2 h-2 rounded-full bg-brand-violet animate-pulse" />
          <span class="text-xs text-gray-400 tracking-widest">AI 需求确认闸口</span>
        </div>
        <h3 class="text-lg font-semibold mb-1">{{ moduleName(card.module) }}</h3>
        <p class="text-gray-300 mb-4">{{ card.intent }}</p>

        <div class="space-y-2 mb-4">
          <div class="flex justify-between text-sm">
            <span class="text-gray-500">预估成本</span>
            <span class="font-mono text-brand-violet">
              ¥{{ costText(card.cost_estimate) }}
            </span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-500">关键参数</span>
            <span class="text-gray-300 truncate max-w-[240px]">{{ paramSummary(card) }}</span>
          </div>
        </div>

        <div class="flex gap-2">
          <button class="btn-primary flex-1" @click="store.confirm(card.id)">确认生成</button>
          <button class="btn-ghost" @click="store.removeFromQueue(card.id)">修改</button>
          <button class="btn-danger" @click="store.cancel(card.id)">放弃</button>
        </div>
        <label class="flex items-center gap-2 mt-4 text-xs text-gray-500 cursor-pointer">
          <input
            type="checkbox"
            v-model="disableSession"
            class="accent-brand-violet"
          />
          本次会话不再确认（关闭闸口）
        </label>
      </div>
    </TransitionGroup>
  </div>

  <!-- 全局 toast -->
  <Transition name="fade">
    <div
      v-if="store.toast"
      class="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 px-4 py-2 rounded-xl glass text-sm"
    >
      {{ store.toast }}
    </div>
  </Transition>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useAppStore } from './stores/app'

const store = useAppStore()
const disableSession = ref(false)

watch(disableSession, (v) => {
  store.updateGate({
    ...store.gateSetting,
    gate_disabled: v,
  })
})

const MODULES = {
  novel: 'AI 小说生成', script: '剧本结构化', shot: '分镜设计',
  character: '角色形象', keyframe: '关键帧抽卡', video: '镜头视频生成',
  audio: '配音配乐', render: '成片渲染',
}
const moduleName = (m) => MODULES[m] || m

const costText = (ce) => {
  if (!ce) return '—'
  const { min = 0, max = 0 } = ce
  return min === max ? `${min}` : `${min}~${max}`
}
const paramSummary = (card) => {
  const p = card.params_json || {}
  const keys = ['genre', 'chapter_count', 'count', 'shot_id', 'novel_id', 'script_id', 'vendor']
  const parts = keys.filter((k) => p[k] !== undefined).map((k) => `${k}=${p[k]}`)
  return parts.join('  ') || '见输入参数'
}
</script>
