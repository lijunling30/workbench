<template>
  <div class="space-y-5">
    <!-- 生成表单 -->
    <div class="panel">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-medium">AI 小说生成</h3>
        <span class="text-[10px] px-2 py-0.5 rounded-full bg-brand-violet/15 text-brand-violet">需求确认闸口</span>
      </div>
      <form class="grid grid-cols-1 md:grid-cols-2 gap-3" @submit.prevent="generate">
        <input v-model="form.title" class="input" placeholder="作品名（如：我在末世开超市）" />
        <input v-model="form.genre" class="input" placeholder="题材（如：末世异能）" required />
        <input v-model="form.premise" class="input md:col-span-2" placeholder="世界观设定（一句话）" />
        <input v-model="form.hero" class="input md:col-span-2" placeholder="主角人设（如：陈凡，28岁退伍军人）" />
        <div class="flex items-center gap-3">
          <span class="text-sm text-gray-500">章节数</span>
          <input v-model.number="form.chapter_count" type="number" min="1" max="10" class="input w-24" />
        </div>
        <div class="flex justify-end">
          <button type="submit" class="btn-primary" :disabled="busy">{{ busy ? '生成中…' : '开始生成' }}</button>
        </div>
      </form>
    </div>

    <!-- 小说列表 -->
    <div v-if="novels.length" class="space-y-5">
      <div v-for="n in novels" :key="n.id" class="panel">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-medium text-lg">{{ n.title }}</h3>
          <div class="flex items-center gap-3 text-xs text-gray-500">
            <span>{{ n.chapters.length }} 章</span>
            <button class="btn-ghost !text-xs" @click="convertScript(n)">转为剧本 →</button>
          </div>
        </div>

        <!-- 角色表 & 设定 -->
        <div class="grid md:grid-cols-2 gap-4 mb-4">
          <div class="bg-abyss-900/60 rounded-xl p-4">
            <p class="text-xs text-gray-500 mb-2">角色表</p>
            <div v-for="c in n.characters" :key="c.name" class="text-sm mb-1.5">
              <span class="text-brand-violet">{{ c.name }}</span>
              <span class="text-gray-500"> · {{ c.role }}</span>
              <p class="text-xs text-gray-600">{{ c.desc }}</p>
            </div>
          </div>
          <div class="bg-abyss-900/60 rounded-xl p-4">
            <p class="text-xs text-gray-500 mb-2">世界观设定</p>
            <div v-for="s in n.settings" :key="s.name" class="text-sm mb-1.5">
              <span class="text-brand-cyan">{{ s.name }}</span>
              <p class="text-xs text-gray-600">{{ s.desc }}</p>
            </div>
          </div>
        </div>

        <!-- 章节 -->
        <div class="space-y-2 max-h-72 overflow-y-auto pr-1">
          <details v-for="ch in n.chapters" :key="ch.no" class="bg-abyss-900/60 rounded-xl px-4 py-3">
            <summary class="cursor-pointer text-sm text-gray-300 select-none">{{ ch.title }}</summary>
            <p class="mt-3 text-sm text-gray-400 leading-relaxed whitespace-pre-line">{{ ch.content }}</p>
          </details>
        </div>
      </div>
    </div>

    <p v-else class="text-center text-gray-600 text-sm py-12">还没有小说，填写上方表单开始创作第一集</p>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useAppStore } from '../../stores/app'
import { api } from '../../api'

const props = defineProps({ projectId: Number })
const emit = defineEmits(['done'])
const app = useAppStore()

const novels = ref([])
const busy = ref(false)
const form = ref({ title: '', genre: '', premise: '', hero: '', chapter_count: 3 })

async function load() {
  novels.value = await api.get(`/content/projects/${props.projectId}/novels`)
}

async function generate() {
  busy.value = true
  try {
    const before = app.confirmQueue.length
    await app.aiRequest('novel', `为《${form.value.title || form.value.genre}》生成 ${form.value.chapter_count} 章小说`, {
      project_id: props.projectId, ...form.value,
    }, { min: 0.01, max: 0.05, desc: '文本生成' })
    if (app.confirmQueue.length === before) await load() // 闸口已关闭，直接执行
  } finally {
    busy.value = false
  }
}

async function convertScript(n) {
  const before = app.confirmQueue.length
  await app.aiRequest('script', `将《${n.title}》转换为剧本`, { novel_id: n.id, project_id: props.projectId }, { min: 0.01, max: 0.05, desc: '结构化抽取' })
  if (app.confirmQueue.length === before) emit('done')
}

// 确认卡确认后刷新
watch(() => app.confirmQueue.length, (n, o) => {
  if (o > 0 && n === 0) load()
})

onMounted(load)
</script>
