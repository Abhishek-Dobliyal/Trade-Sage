import { ref } from 'vue'
import { streamChat } from '../api/client'

const messages = ref([])
const conversationId = ref(null)
const streaming = ref(false)
const thinking = ref(false)
const selectedModel = ref(null)

export function useChat() {
  async function sendMessage(text) {
    messages.value.push({ role: 'user', content: text })
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
              messages.value.push({ role: 'assistant', content: `Error: ${parsed.error}` })
              break
            }
            if (parsed.text) {
              if (thinking.value) {
                thinking.value = false
                messages.value.push({ role: 'assistant', content: '' })
                assistantIdx = messages.value.length - 1
              }
              messages.value[assistantIdx].content += parsed.text
            }
          } catch {
            // skip malformed chunks
          }
        }
      }
    } catch (err) {
      thinking.value = false
      const last = messages.value[messages.value.length - 1]
      if (last.role === 'assistant' && !last.content) {
        last.content = 'Failed to get response. Please try again.'
      } else if (last.role === 'user') {
        messages.value.push({ role: 'assistant', content: 'Failed to get response. Please try again.' })
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
