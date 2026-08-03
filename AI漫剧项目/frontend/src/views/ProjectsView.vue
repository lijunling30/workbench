<template>
  <div class="min-h-screen p-8">
    <header class="flex items-center justify-between mb-8">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-violet to-brand-cyan grid place-items-center text-white font-bold">漫</div>
        <div>
          <h1 class="font-semibold">项目工作台</h1>
          <p class="text-xs text-gray-500">{{ auth.user?.phone }} · {{ planName }}</p>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <button class="btn-primary" @click="showCreate = true">+ 新建项目</button>
        <button class="btn-ghost" @click="auth.logout(); $router.push('/login')">退出</button>
      </div>
    </header>

    <!-- 项目卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
      <div
        v-for="p in projects"
        :key="p.id"
        class="panel cursor-pointer group transition-all hover:border-brand-violet/40 hover:shadow-glow"
        @click="$router.push(`/workbench/${p.id}`)"
      >
        <div class="flex items-start justify-between mb-3">
          <h3 class="font-medium group-hover:text-brand-violet transition-colors">{{ p.name }}</h3>
          <span class="text-[10px] px-2 py-0.5 rounded-full bg-brand-violet/15 text-brand-violet">{{ platformName(p.target_platform) }}</span>
        </div>
        <p class="text-sm text-gray-500 mb-4 line-clamp-2">{{ p.genre || '未设置题材' }}</p>
        <div class="flex items-center justify-between text-xs text-gray-500">
          <span>风格：{{ p.style_id }}</span>
          <span>预算 ¥{{ p.budget_limit }}</span>
        </div>
      </div>
    </div>

    <!-- 新建项目弹窗 -->
    <div v-if="showCreate" class="fixed inset-0 z-40 flex items-center justify-center bg-black/60 backdrop-blur-sm" @click.self="showCreate = false">
      <div class="glass w-[420px] p-6">
        <h3 class="font-semibold mb-4">新建漫剧项目</h3>
        <form class="space-y-3" @submit.prevent="create">
          <input v-model="form.name" class="input" placeholder="项目名称（如：我在末世开超市）" required />
          <input v-model="form.genre" class="input" placeholder="题材（如：末世异能 / 都市逆袭）" />
          <input v-model="form.style_desc" class="input" placeholder="画风描述（如：日系赛璐璐漫剧风格）" />
          <select v-model="form.target_platform" class="input">
            <option value="douyin">抖音 9:16 竖屏</option>
            <option value="bilibili">B 站 16:9 横屏</option>
          </select>
          <div class="flex gap-2 pt-2">
            <button type="submit" class="btn-primary flex-1">创建</button>
            <button type="button" class="btn-ghost" @click="showCreate = false">取消</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { api } from '../api'

const router = useRouter()
const auth = useAuthStore()
const projects = ref([])
const showCreate = ref(false)
const form = ref({ name: '', genre: '', style_desc: '', target_platform: 'douyin' })

const planName = computed(() => ({ personal: '个人版', team: '团队版', enterprise: '企业版' }[auth.user?.plan] || '个人版'))
const platformName = (p) => (p === 'bilibili' ? 'B站横屏' : '抖音竖屏')

async function load() {
  projects.value = await api.get('/projects')
}
async function create() {
  await api.post('/projects', form.value)
  showCreate.value = false
  load()
}
onMounted(load)
</script>
