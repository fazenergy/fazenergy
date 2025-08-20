<template>
  <div class="border rounded">
    <div class="flex flex-wrap gap-1 p-2 border-b bg-gray-50 text-xs">
      <button type="button" @click="cmd('bold')" class="px-2 py-1 border rounded hover:bg-gray-100">B</button>
      <button type="button" @click="cmd('italic')" class="px-2 py-1 border rounded hover:bg-gray-100 italic">I</button>
      <button type="button" @click="cmd('underline')" class="px-2 py-1 border rounded hover:bg-gray-100"><span class="underline">U</span></button>
      <button type="button" @click="cmd('insertUnorderedList')" class="px-2 py-1 border rounded hover:bg-gray-100">• Lista</button>
      <button type="button" @click="cmd('insertOrderedList')" class="px-2 py-1 border rounded hover:bg-gray-100">1. Lista</button>
      <button type="button" @click="insertLink" class="px-2 py-1 border rounded hover:bg-gray-100">Link</button>
      <button type="button" @click="clearFormatting" class="px-2 py-1 border rounded hover:bg-gray-100">Limpar</button>
    </div>
    <div
      ref="editor"
      class="p-3 text-sm focus:outline-none overflow-auto"
      :style="{ minHeight: minHeight, maxHeight: maxHeight }"
      contenteditable
      :placeholder="placeholder"
      @input="onInput"
      @blur="onInput"
    />
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: 'Digite o conteúdo...' },
  minHeight: { type: String, default: '160px' },
  maxHeight: { type: String, default: '260px' }
})
const emit = defineEmits(['update:modelValue'])

const editor = ref(null)

onMounted(() => {
  if (editor.value) editor.value.innerHTML = props.modelValue || ''
})

watch(() => props.modelValue, (val) => {
  if (!editor.value) return
  if (editor.value.innerHTML !== (val || '')) {
    editor.value.innerHTML = val || ''
  }
})

function onInput() {
  emit('update:modelValue', editor.value?.innerHTML || '')
}

function cmd(command) {
  document.execCommand(command, false)
  onInput()
}

function insertLink() {
  const url = prompt('URL do link:')
  if (url) {
    document.execCommand('createLink', false, url)
    onInput()
  }
}

function clearFormatting() {
  document.execCommand('removeFormat', false)
  onInput()
}
</script>

<style scoped>
[contenteditable][placeholder]:empty:before {
  content: attr(placeholder);
  color: #9ca3af;
}
</style>


