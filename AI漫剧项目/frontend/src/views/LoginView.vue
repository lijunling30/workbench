<template>
  <div class="min-h-screen flex items-center justify-center relative overflow-hidden">
    <!-- 品牌背景 -->
    <div class="absolute inset-0 pointer-events-none">
      <div class="absolute -top-40 -right-40 w-[600px] h-[600px] rounded-full bg-brand-violet/15 blur-[120px]" />
      <div class="absolute -bottom-40 -left-40 w-[600px] h-[600px] rounded-full bg-brand-cyan/10 blur-[120px]" />
    </div>

    <div class="relative w-[400px] max-w-[92vw]">
      <div class="text-center mb-10">
        <h1 class="text-5xl font-bold grad-text tracking-wide">漫镜工场</h1>
        <p class="mt-3 text-gray-400 text-sm tracking-[0.3em]">MANJU STUDIO · AI 漫剧工业化平台</p>
      </div>

      <div class="glass p-8">
        <div class="flex mb-6 rounded-xl bg-abyss-900/60 p-1">
          <button
            class="flex-1 py-2 rounded-lg text-sm font-medium transition-all"
            :class="mode === 'login' ? 'bg-gradient-to-r from-brand-violet/30 to-brand-cyan/20 text-white' : 'text-gray-500'"
            @click="mode = 'login'"
          >登录</button>
          <button
            class="flex-1 py-2 rounded-lg text-sm font-medium transition-all"
            :class="mode === 'register' ? 'bg-gradient-to-r from-brand-violet/30 to-brand-cyan/20 text-white' : 'text-gray-500'"
            @click="mode = 'register'"
          >注册</button>
        </div>

        <form class="space-y-4" @submit.prevent="submit">
          <div>
            <label class="text-xs text-gray-500 mb-1 block">手机号</label>
            <input v-model="phone" class="input" placeholder="请输入手机号" />
          </div>
          <div>
            <label class="text-xs text-gray-500 mb-1 block">密码</label>
            <input v-model="password" type="password" class="input" placeholder="请输入密码" />
          </div>
          <button type="submit" class="btn-primary w-full py-3 mt-2" :disabled="loading">
            {{ loading ? '请稍候…' : mode === 'login' ? '进入工作台' : '创建账号' }}
          </button>
        </form>

        <p v-if="error" class="mt-3 text-red-400 text-xs">{{ error }}</p>
      </div>

      <p class="text-center text-gray-600 text-xs mt-6">从小说到成片 · 一个工作台完成</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const mode = ref('login')
const phone = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  if (!phone.value || !password.value) return (error.value = '请填写手机号和密码')
  loading.value = true
  error.value = ''
  try {
    if (mode.value === 'login') await auth.login(phone.value, password.value)
    else await auth.register(phone.value, password.value)
    router.push('/projects')
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>
