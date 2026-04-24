import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

export function streamChat(message, conversationId = null) {
  const body = JSON.stringify({
    message,
    conversation_id: conversationId,
    stream: true,
  })

  return fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body,
  })
}

export default api
