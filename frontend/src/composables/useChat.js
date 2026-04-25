import { shallowRef } from 'vue'
import { streamChat } from '../api/client'

const messages = shallowRef([])
const conversationId = shallowRef(null)
const streaming = shallowRef(false)
const thinking = shallowRef(false)
const selectedModel = shallowRef(null)

export function useChat() {
  async function sendMessage(text) {
    messages.value = [...messages.value, { role: 'user', content: text }]
    thinking.value = true
    streaming.value = true

    try {
      const response = await streamChat(text, conversationId.value, selectedModel.value)
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let assistantIdx = -1

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const json = line.slice(6)
          try {
            const parsed = JSON.parse(json)
            if (parsed.conversation_id) {
              conversationId.value = parsed.conversation_id
            }
            if (parsed.error) {
              thinking.value = false
              messages.value = [...messages.value, { role: 'assistant', content: `Error: ${parsed.error}` }]
              break
            }
            if (parsed.text) {
              if (thinking.value) {
                thinking.value = false
                messages.value = [...messages.value, { role: 'assistant', content: '' }]
                assistantIdx = messages.value.length - 1
              }
              messages.value = messages.value.map((m, i) =>
                i === assistantIdx ? { ...m, content: m.content + parsed.text } : m
              )
            }
          } catch {
          }
        }
      }
    } catch (err) {
      thinking.value = false
      const last = messages.value[messages.value.length - 1]
      if (last.role === 'assistant' && !last.content) {
        messages.value = messages.value.map((m, i) =>
          i === messages.value.length - 1 ? { ...m, content: 'Failed to get response. Please try again.' } : m
        )
      } else if (last.role === 'user') {
        messages.value = [...messages.value, { role: 'assistant', content: 'Failed to get response. Please try again.' }]
      }
    } finally {
      streaming.value = false
      thinking.value = false
    }
  }

  function clearChat() {
    messages.value = []
    conversationId.value = null
  }

  return { messages, conversationId, streaming, thinking, selectedModel, sendMessage, clearChat }
}