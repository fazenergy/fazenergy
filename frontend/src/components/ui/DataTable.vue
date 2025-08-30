<template>
  <div class="border rounded-md overflow-hidden flex flex-col" :style="containerStyle">
    <div class="relative flex-1 overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-blue-800 text-white select-none">
          <tr>
            <th v-if="hasActions" class="px-1 py-2 text-left w-0">{{ actionsLabel }}</th>
            <th v-for="col in columns" :key="col.key"
                class="px-3 py-2 text-left border-b border-blue-700"
                :class="[headerAlign(col), col.width]">
              {{ col.label }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in pagedRows" :key="getRowKey(row)" class="even:bg-gray-50 hover:bg-gray-100">
            <td v-if="hasActions" class="px-1 py-1 border-b whitespace-nowrap w-0">
              <slot name="actions" :row="row" />
            </td>
            <td v-for="col in columns" :key="col.key" class="px-3 py-2 border-b"
                :class="[cellAlign(col), col.width]">
              <slot :name="`col:${col.key}`" :row="row">{{ row[col.key] ?? '-' }}</slot>
            </td>
          </tr>
          <tr v-if="!loading && rows.length === 0">
            <td :colspan="columns.length + (hasActions ? 1 : 0)" class="px-3 py-6 text-center text-gray-500">Nenhum registro encontrado.</td>
          </tr>
        </tbody>
      </table>

      <!-- Loading overlay -->
      <div v-if="loading" class="absolute inset-0 bg-white/60 grid place-items-center">
        <div class="h-8 w-8 rounded-full border-2 border-blue-600 border-t-transparent animate-spin"></div>
      </div>
    </div>

    <!-- Footer with pagination -->
    <div class="flex items-center justify-between px-3 py-2 text-xs text-gray-600 border-t bg-white">
      <div>
        Mostrando de {{ startIndex + 1 }} até {{ endIndex }} de {{ rows.length }} registros
      </div>
      <div class="flex items-center gap-2">
        <button class="px-2 py-1 border rounded disabled:opacity-50" :disabled="page === 1" @click="page--">Anterior</button>
        <input type="number" v-model.number="page" class="w-12 text-center border rounded py-1" min="1" :max="maxPage">
        <span>/ {{ maxPage }}</span>
        <button class="px-2 py-1 border rounded disabled:opacity-50" :disabled="page === maxPage" @click="page++">Próximo</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, toRef, useSlots } from 'vue'

const props = defineProps({
  columns: { type: Array, required: true },
  rows: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  pageSize: { type: Number, default: 10 },
  rowKey: { type: [String, Function], default: 'id' },
  showActions: { type: Boolean, default: true },
  minHeight: { type: String, default: '300px' },
})

const columns = toRef(props, 'columns')
const rows = toRef(props, 'rows')

const slots = useSlots()
const hasActions = computed(() => props.showActions && !!slots.actions)
const actionsLabel = computed(() => 'Ações')

const pageState = defineModel('page', { type: Number, default: 1 })
const page = pageState

const maxPage = computed(() => Math.max(1, Math.ceil(rows.value.length / props.pageSize)))
const startIndex = computed(() => Math.min((page.value - 1) * props.pageSize, rows.value.length))
const endIndex = computed(() => Math.min(startIndex.value + props.pageSize, rows.value.length))
const pagedRows = computed(() => rows.value.slice(startIndex.value, endIndex.value))

function getRowKey(row) {
  return typeof props.rowKey === 'function' ? props.rowKey(row) : row[props.rowKey]
}

function headerAlign(col) {
  return col.align === 'right' ? 'text-right' : col.align === 'center' ? 'text-center' : 'text-left'
}
function cellAlign(col) {
  return col.align === 'right' ? 'text-right' : col.align === 'center' ? 'text-center' : 'text-left'
}

const containerStyle = computed(() => ({ minHeight: props.minHeight }))
</script>


