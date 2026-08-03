<template>
  <div class="space-y-4">
    <!-- 成本看板 -->
    <div class="panel">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-medium">成本对账</h3>
        <span class="text-xs text-gray-500">A-2 成本模型 · 按生成消耗计费</span>
      </div>
      <div class="grid grid-cols-3 gap-4">
        <div class="bg-abyss-900/60 rounded-xl p-4">
          <p class="text-xs text-gray-500 mb-1">项目总花费</p>
          <p class="text-2xl font-mono text-brand-violet">¥{{ summary.spent ?? 0 }}</p>
        </div>
        <div class="bg-abyss-900/60 rounded-xl p-4">
          <p class="text-xs text-gray-500 mb-1">预算上限</p>
          <p class="text-2xl font-mono">¥{{ project?.budget_limit }}</p>
        </div>
        <div class="bg-abyss-900/60 rounded-xl p-4">
          <p class="text-xs text-gray-500 mb-1">使用占比</p>
          <p class="text-2xl font-mono" :class="(summary.ratio ?? 0) >= 80 ? 'text-amber-400' : 'text-brand-cyan'">
            {{ summary.ratio ?? 0 }}%
          </p>
        </div>
      </div>
    </div>

    <!-- 成本明细 -->
    <div class="panel">
      <h3 class="font-medium mb-4">生成明细</h3>
      <div class="space-y-2">
        <div v-for="log in logs" :key="log.id" class="flex items-center gap-3 text-sm bg-abyss-900/60 rounded-lg px-4 py-2.5">
          <span class="w-16 text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-gray-400 text-center">{{ moduleName(log.module) }}</span>
          <span class="text-gray-500 flex-1 truncate">{{ log.vendor }} / {{ log.model }}</span>
          <span class="text-gray-600 font-mono text-xs">{{ log.tokens ? log.tokens + ' tok' : (log.duration ? log.duration + 's' : '') }}</span>
          <span class="text-brand-violet font-mono">¥{{ log.amount }}</span>
        </div>
        <p v-if="!logs.length" class="text-center text-gray-600 text-sm py-8">暂无生成记录</p>
      </div>
    </div>

    <!-- 成片导出 -->
    <div class="panel">
      <h3 class="font-medium mb-4">成片导出</h3>
      <div class="flex items-center gap-3">
        <label class="flex items-center gap-2 text-sm text-gray-400 cursor-pointer">
          <input type="checkbox" v-model="enableAudit" class="accent-brand-violet" />
          启用合规检验（M13 可选）
        </label>
        <button class="btn-primary ml-auto" @click="render" :disabled="rendering">
          {{ rendering ? '渲染中…' : '渲染成片' }}
        </button>
      </div>
      <p class="text-[11px] text-gray-600 mt-2">所有导出成片强制携带 AI 生成标识（显式角标 + 元数据水印），无开关</p>

      <div v-if="finalVideos.length" class="mt-4 space-y-2">
        <div v-for="fv in finalVideos" :key="fv.id" class="flex items-center gap-3 text-sm bg-abyss-900/60 rounded-xl p-4">
          <span class="text-xs text-gray-400">第 {{ fv.episode_no }} 集</span>
          <span class="text-[10px] px-2 py-0.5 rounded-full bg-brand-violet/15 text-brand-violet">AI 标识 ✓</span>
          <span class="text-[10px] px-2 py-0.5 rounded-full" :class="fv.audit_status === 'passed' ? 'bg-brand-cyan/15 text-brand-cyan' : 'bg-gray-500/15 text-gray-400'">
            {{ auditText(fv.audit_status) }}
          </span>
          <span class="ml-auto text-xs text-gray-500 font-mono">总成本 ¥{{ fv.cost_total }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAppStore } from '../../stores/app'
import { api } from '../../api'

const props = defineProps({ projectId: Number })
const app = useAppStore()
const summary = ref({})
const logs = ref([])
const project = ref(null)
const finalVideos = ref([])
const enableAudit = ref(false)
const rendering = ref(false)

const moduleName = (m) => ({ novel: '小说', script: '剧本', shot: '分镜', character: '角色', keyframe: '关键帧', video: '视频', audio: '配音', render: '渲染' }[m] || m)
const auditText = (s) => ({ passed: '已通过', skipped: '已跳过', pending: '待审', reject: '未通过' }[s] || s)

async function load() {
  summary.value = await api.get(`/projects/${props.projectId}/costs`)
  logs.value = await api.get(`/costs/projects/${props.projectId}/logs`)
  project.value = await api.get(`/projects/${props.projectId}`)
  finalVideos.value = await api.get(`/assets/projects/${props.projectId}/final-videos`)
}

async function render() {
  rendering.value = true
  try {
    const before = app.confirmQueue.length
    await app.aiRequest('render', '渲染当前项目成片（强制携带 AI 标识）',
      { project_id: props.projectId, episode_no: 1, enable_audit: enableAudit.value },
      { min: 0.5, max: 0.5, desc: '渲染费用' })
    if (app.confirmQueue.length === before) await load()
  } finally {
    rendering.value = false
  }
}

onMounted(load)
</script>
