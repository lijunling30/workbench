<template>
  <div class="min-h-screen p-6 flex flex-col">
    <!-- 顶栏 -->
    <header class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-3">
        <button class="btn-ghost !px-3" @click="$router.push('/projects')">← 项目</button>
        <div>
          <h1 class="font-semibold text-lg">{{ project?.name || '加载中…' }}</h1>
          <p class="text-xs text-gray-500">{{ project?.genre }} · {{ project?.style_id }}</p>
        </div>
      </div>
      <div class="flex items-center gap-4 text-xs">
        <div class="glass px-3 py-1.5 flex items-center gap-2">
          <span class="text-gray-500">已花费</span>
          <span class="font-mono text-brand-violet">¥{{ cost.spent ?? 0 }}</span>
          <span class="text-gray-600">/ ¥{{ project?.budget_limit }}</span>
          <span
            v-if="cost.status"
            class="px-1.5 py-0.5 rounded text-[10px]"
            :class="cost.status === 'ok' ? 'bg-brand-cyan/15 text-brand-cyan' : cost.status === 'warning' ? 'bg-amber-500/15 text-amber-400' : 'bg-red-500/15 text-red-400'"
          >{{ costText }}</span>
        </div>
        <button class="btn-ghost !text-xs" @click="$router.push('/projects')">任务中心</button>
      </div>
    </header>

    <!-- 主体：左流程导航 + 右内容 -->
    <div class="flex flex-1 gap-5 min-h-0">
      <aside class="w-52 shrink-0 glass p-3 flex flex-col gap-1">
        <div
          v-for="(s, i) in steps"
          :key="s.id"
          class="px-3 py-2.5 rounded-xl cursor-pointer flex items-center gap-3 transition-all"
          :class="step === s.id
            ? 'bg-gradient-to-r from-brand-violet/20 to-brand-cyan/10 text-white border border-brand-violet/30'
            : 'text-gray-400 hover:bg-white/5'"
          @click="step = s.id"
        >
          <span class="w-6 h-6 rounded-full grid place-items-center text-[11px] border border-current/40" :class="doneSteps.includes(s.id) ? 'bg-brand-cyan/20 text-brand-cyan' : ''">
            {{ i + 1 }}
          </span>
          <span class="text-sm">{{ s.name }}</span>
        </div>
      </aside>

      <main class="flex-1 min-w-0 overflow-y-auto pr-1">
        <NovelTab v-if="step === 'novel'" :project-id="projectId" @done="loadAll" />
        <ScriptTab v-else-if="step === 'script'" :project-id="projectId" />
        <ShotsTab v-else-if="step === 'shots'" :project-id="projectId" />
        <CharactersTab v-else-if="step === 'character'" :project-id="projectId" />
        <CostTab v-else-if="step === 'cost'" :project-id="projectId" />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api'
import NovelTab from '../components/tabs/NovelTab.vue'
import ScriptTab from '../components/tabs/ScriptTab.vue'
import ShotsTab from '../components/tabs/ShotsTab.vue'
import CharactersTab from '../components/tabs/CharactersTab.vue'
import CostTab from '../components/tabs/CostTab.vue'

const route = useRoute()
const projectId = Number(route.params.projectId)
const project = ref(null)
const cost = ref({})
const step = ref('novel')

const steps = [
  { id: 'novel', name: 'AI 小说' },
  { id: 'script', name: '剧本' },
  { id: 'shots', name: '分镜 & 关键帧' },
  { id: 'character', name: '角色资产库' },
  { id: 'cost', name: '成本与导出' },
]

const doneSteps = computed(() => {
  const done = []
  return done
})
const costText = computed(() => ({ ok: '预算充足', warning: '已达 80%', blocked: '预算超限' }[cost.value.status] || ''))

async function loadAll() {
  project.value = await api.get(`/projects/${projectId}`)
  cost.value = await api.get(`/projects/${projectId}/costs`)
}
onMounted(loadAll)
watch(step, () => {})
</script>
