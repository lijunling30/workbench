import { defineStore } from 'pinia'
import { api } from '../api'

// 全局状态：确认闸口队列 + 任务中心
export const useAppStore = defineStore('app', {
  state: () => ({
    confirmQueue: [],   // 确认卡队列 [{id, module, intent, params_json, cost_estimate, status}]
    gateSetting: { gate_disabled: false, disabled_modules: [] },
    toast: '',
  }),
  actions: {
    // 通用 AI 请求：创建 -> 若 draft 则进确认卡队列，否则视为已执行
    async aiRequest(module, intent, params, cost_estimate, { silent = false } = {}) {
      const req = await api.post('/ai/requests', {
        module, intent, params, cost_estimate,
      })
      if (req.status === 'draft') {
        this.confirmQueue.push(req)
      } else if (req.status === 'bypassed') {
        this.toast = '已执行（闸口已关闭）'
      }
      return req
    },
    async confirm(id) {
      await api.post(`/ai/requests/${id}/confirm`)
      this.removeFromQueue(id)
      this.toast = '任务已执行'
    },
    async reject(id, note) {
      await api.post(`/ai/requests/${id}/reject`, { action: 'reject', edit_note: note })
      this.removeFromQueue(id)
      this.toast = '已驳回请求'
    },
    async cancel(id) {
      await api.post(`/ai/requests/${id}/cancel`)
      this.removeFromQueue(id)
    },
    removeFromQueue(id) {
      this.confirmQueue = this.confirmQueue.filter((q) => q.id !== id)
    },
    async updateGate(data) {
      this.gateSetting = await api.put('/ai/settings/gate', data)
    },
    showToast(msg) {
      this.toast = msg
      setTimeout(() => (this.toast = ''), 2500)
    },
  },
})
