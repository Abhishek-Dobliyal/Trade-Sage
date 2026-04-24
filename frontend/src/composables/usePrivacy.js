import { ref } from 'vue'

const hidden = ref(false)

export function usePrivacy() {
  function toggle() {
    hidden.value = !hidden.value
  }

  function mask(value) {
    return hidden.value ? '••••••' : value
  }

  return { hidden, toggle, mask }
}
