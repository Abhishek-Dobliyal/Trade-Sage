<template>
  <div class="flex flex-col h-screen">
    <PageHeader title="Chat with TradeSage">
      <button
        v-if="messages.length"
        class="text-sm text-gray-500 hover:text-gray-300 transition-colors"
        @click="clearChat"
      >
        <i class="fa-solid fa-rotate-right mr-1"></i> New Chat
      </button>
    </PageHeader>

    <div ref="messagesContainer" class="flex-1 overflow-y-auto p-6 space-y-4">
      <div v-if="!messages.length" class="flex flex-col items-center justify-center h-full text-center">
        <i class="fa-solid fa-comments text-4xl text-gray-700 mb-4"></i>
        <h2 class="text-xl font-semibold text-gray-400 mb-2">Ask TradeSage anything</h2>
        <p class="text-sm text-gray-500 mb-6 max-w-md">
          Get portfolio analysis, stock recommendations, and market insights powered by AI.
        </p>
        <div class="flex flex-wrap justify-center gap-2">
          <button
            v-for="chip in promptChips"
            :key="chip"
            class="px-3 py-1.5 bg-gray-800 border border-gray-700 rounded-full text-sm text-gray-400 hover:text-emerald-400 hover:border-emerald-500/30 transition-colors"
            @click="sendMessage(chip)"
          >
            {{ chip }}
          </button>
        </div>
      </div>

      <div
        v-for="(msg, i) in messages"
        :key="i"
        :class="[
          'flex',
          msg.role === 'user' ? 'justify-end' : 'justify-start',
        ]"
      >
        <div
          :class="[
            'max-w-2xl rounded-2xl px-4 py-3 text-sm animate__animated animate__fadeIn',
            msg.role === 'user'
              ? 'bg-emerald-600 text-white rounded-br-md'
              : 'bg-gray-800 border border-gray-700 text-gray-200 rounded-bl-md',
          ]"
        >
          <div
            v-if="msg.role === 'assistant'"
            class="prose prose-invert prose-sm max-w-none"
            v-html="renderMarkdown(msg.content)"
          ></div>
          <span v-else>{{ msg.content }}</span>
          <span
            v-if="msg.role === 'assistant' && streaming && i === messages.length - 1"
            class="inline-block w-1.5 h-4 bg-emerald-400 ml-1 animate-pulse rounded-sm"
          ></span>
        </div>
      </div>

      <!-- Thinking indicator -->
      <div v-if="thinking" class="flex justify-start">
        <div class="bg-gray-800 border border-gray-700 rounded-2xl rounded-bl-md px-5 py-4 animate__animated animate__fadeIn">
          <div class="flex items-center gap-3">
            <div class="flex gap-1">
              <span class="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
              <span class="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
              <span class="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
            </div>
            <span class="text-xs text-gray-500">Analyzing...</span>
          </div>
        </div>
      </div>
    </div>

    <div class="p-4 border-t border-gray-800 bg-gray-900/50">
      <form class="flex gap-3 max-w-4xl mx-auto" @submit.prevent="handleSubmit">
        <input
          v-model="input"
          type="text"
          placeholder="Ask about your portfolio, markets, or stocks..."
          class="flex-1 bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-emerald-500 transition-colors"
          :disabled="streaming"
        />
        <button
          type="submit"
          :disabled="!input.trim() || streaming"
          class="px-5 py-3 bg-emerald-600 hover:bg-emerald-500 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded-xl text-sm font-medium transition-colors"
        >
          <i class="fa-solid fa-paper-plane"></i>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import { marked } from 'marked'
import PageHeader from '../components/layout/PageHeader.vue'
import { useChat } from '../composables/useChat'

const { messages, streaming, thinking, sendMessage, clearChat } = useChat()
const input = ref('')
const messagesContainer = ref(null)

const promptChips = [
  'Analyze my portfolio risk',
  'What should I buy this week?',
  'Which sectors are overweight?',
  'Summarize market sentiment',
]

function renderMarkdown(text) {
  if (!text) return ''
  return marked.parse(text, { breaks: true })
}

async function handleSubmit() {
  const text = input.value.trim()
  if (!text || streaming.value) return
  input.value = ''
  await sendMessage(text)
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

watch(() => messages.value.length, scrollToBottom)
watch(() => messages.value[messages.value.length - 1]?.content, scrollToBottom)
</script>
