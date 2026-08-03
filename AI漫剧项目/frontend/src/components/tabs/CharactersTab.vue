<template>
  <div class="space-y-4">
    <!-- 人物子库 -->
    <div class="panel">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-medium">人物子库</h3>
        <button class="btn-ghost !text-xs" @click="createLib">+ 新建子库</button>
      </div>
      <div class="flex gap-2 flex-wrap">
        <button
          v-for="lib in libraries"
          :key="lib.id"
          class="px-3 py-1.5 rounded-xl text-sm transition-all"
          :class="activeLib?.id === lib.id ? 'bg-gradient-to-r from-brand-violet/25 to-brand-cyan/15 text-white border border-brand-violet/30' : 'bg-abyss-900/60 text-gray-400 border border-white/10 hover:border-white/20'"
          @click="activeLib = lib; loadChars()"
        >{{ lib.name }}</button>
      </div>
    </div>

    <!-- 角色卡片墙 -->
    <div v-if="activeLib" class="panel">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-medium">{{ activeLib.name }} · 角色</h3>
        <div class="flex gap-2">
          <input v-model="newChar.name" class="input !w-36 !py-1.5" placeholder="角色名" />
          <button class="btn-primary !text-xs" @click="addChar">添加</button>
        </div>
      </div>

      <div class="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <div v-for="c in characters" :key="c.id" class="rounded-xl border border-white/10 bg-abyss-900/60 p-3">
          <div class="flex justify-center mb-3">
            <img
              v-if="c.ref_images?.length"
              :src="c.ref_images[0]"
              class="w-24 aspect-[9/16] rounded-lg object-cover"
              alt="角色形象"
            />
            <div v-else class="w-24 aspect-[9/16] rounded-lg bg-abyss-800 grid place-items-center text-gray-600 text-xs">暂无形象</div>
          </div>
          <h4 class="text-sm font-medium mb-1">{{ c.name }}</h4>
          <p class="text-[11px] text-gray-500 leading-relaxed line-clamp-3">{{ c.desc }}</p>
          <button class="btn-ghost !text-xs w-full mt-3" @click="genImages(c)">生成形象</button>
        </div>
      </div>
    </div>

    <p v-if="!libraries.length" class="text-center text-gray-600 text-sm py-12">
      还没有人物子库 —— 点击「新建子库」开始建立角色资产
    </p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAppStore } from '../../stores/app'
import { api } from '../../api'

const props = defineProps({ projectId: Number })
const app = useAppStore()
const libraries = ref([])
const activeLib = ref(null)
const characters = ref([])
const newChar = ref({ name: '' })

async function loadLibs() {
  libraries.value = await api.get('/character/libraries')
  if (!activeLib.value && libraries.value.length) {
    activeLib.value = libraries.value[0]
    loadChars()
  }
}
async function loadChars() {
  if (!activeLib.value) return
  characters.value = await api.get(`/character/libraries/${activeLib.value.id}/characters`)
}
async function createLib() {
  const name = prompt('子库名称：')
  if (!name) return
  const lib = await api.post('/character/libraries', { name, desc: '', project_ids: [props.projectId] })
  libraries.value = await api.get('/character/libraries')
  activeLib.value = lib
  loadChars()
}
async function addChar() {
  if (!newChar.value.name) return
  await api.post('/character/characters', { library_id: activeLib.value.id, name: newChar.value.name, desc: '待补充角色设定' })
  newChar.value.name = ''
  loadChars()
}
async function genImages(c) {
  await api.post(`/character/characters/${c.id}/images`)
  loadChars()
}
onMounted(loadLibs)
</script>
