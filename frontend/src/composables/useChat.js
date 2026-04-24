import { ref } from 'vue'
import { streamChat } from '../api/client'

const messages = ref([])
const conversationId = ref(null)
const streaming = ref(false)

export function useChat() {
  async function sendMessage(text) {
    messages.value.push({ role: 'user', content: text })
    messages.value.push({ role: 'assistant', content: '' })
    streaming.value = true

    try {
      const response = await streamChat(text, conversationId.value)
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      const assistantIdx = messages.value.length - 1
      let buffer = ''

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
            if (parsed.text) {
              messages.value[assistantIdx].content += parsed.text
            }
          } catch {
            // skip malformed chunks
          }
        }
      }
    } catch (err) {
      const last = messages.value[messages.value.length - 1]
      if (last.role === 'assistant' && !last.content) {
        last.content = 'Failed to get response. Please try again.'
      }
    } finally {
      streaming.value = false
    }
  }

  function clearChat() {
    messages.value = []
    conversationId.value = null
  }

  return { messages, conversationId, streaming, sendMessage, clearChat }
}
