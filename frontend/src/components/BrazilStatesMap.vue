<template>
  <div class="w-full">
    <div class="flex items-center justify-between mb-2">
      <div class="text-xs text-gray-500" v-if="selected">
        UF selecionada: <span class="font-medium">{{ selected }}</span>
      </div>
    </div>

    <div class="select-none">
      <svg
        :viewBox="viewBoxAttr"
        class="w-full h-auto"
        :style="svgStyle"
        xmlns="http://www.w3.org/2000/svg"
        role="img"
        aria-label="Mapa do Brasil"
        ref="svgRef"
      >
        <defs>
          <linearGradient v-for="(val, uf) in normalizedSales" :key="'g-'+uf" :id="'grad-'+uf" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" :stop-color="gradientFrom(uf)" />
            <stop offset="100%" :stop-color="gradientTo(uf)" />
          </linearGradient>
        </defs>
        <g v-for="loc in brazilMap.locations" :key="loc.id">
          <path
            :d="loc.path"
            :class="['svg-map__location', { 'is-hover': hoveredUf === loc.id }]"
            :id="loc.id"
            :aria-checked="selected === loc.id ? 'true' : 'false'"
            @click="handleClick(loc.id)"
            @mouseenter="hoveredUf = loc.id"
            @mouseleave="hoveredUf = ''"
            :style="{ fill: fillFor(loc.id) }"
          />
          <text
            v-if="labelPos[loc.id]"
            :x="labelPos[loc.id].x"
            :y="labelPos[loc.id].y"
            text-anchor="middle"
            dominant-baseline="middle"
            :font-size="fontSizeFor(loc.id)"
            class="state-label"
            pointer-events="none"
          >
            {{ loc.id.toUpperCase() }}
          </text>
        </g>
      </svg>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import brazil from '@svg-maps/brazil'

const emit = defineEmits(['select'])
const props = defineProps({
  modelValue: { type: String, default: '' },
  height: { type: Number, default: 0 }, // 0 = auto
  colorful: { type: Boolean, default: true },
  salesByUf: { type: Object, default: () => ({}) }, // { 'SP': 10, 'MG': 2 }
})

const selected = ref(props.modelValue || '')
const brazilMap = brazil
const svgRef = ref(null)
const labelPos = ref({})
const viewBoxAttr = ref('0 0 1000 1000')
const hoveredUf = ref('')

const svgStyle = computed(() => (props.height > 0 ? { height: props.height + 'px' } : {}))

const maxSales = computed(() => {
  const vals = Object.values(props.salesByUf || {})
  return vals.length ? Math.max(...vals.map(v => Number(v) || 0)) : 0
})

const normalizedSales = computed(() => {
  const max = maxSales.value || 1
  const entries = Object.entries(props.salesByUf || {})
  const out = {}
  for (const [uf, val] of entries) out[uf.toUpperCase()] = Math.max(0, Math.min(1, Number(val) / max))
  return out
})

function handleClick(uf) {
  if (!uf) return
  selected.value = uf.toUpperCase()
  emit('select', selected.value)
}

function computeLabelPositions() {
  nextTick(() => {
    const svgEl = svgRef.value
    if (!svgEl) return
    const positions = {}
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity
    for (const loc of brazilMap.locations) {
      const pathEl = svgEl.querySelector(`path#${loc.id}`)
      if (!pathEl) continue
      try {
        const b = pathEl.getBBox()
        positions[loc.id] = { x: b.x + b.width / 2, y: b.y + b.height / 2 }
        minX = Math.min(minX, b.x)
        minY = Math.min(minY, b.y)
        maxX = Math.max(maxX, b.x + b.width)
        maxY = Math.max(maxY, b.y + b.height)
      } catch {}
    }
    labelPos.value = positions

    // Ajusta viewBox para remover bordas vazias
    if (isFinite(minX) && isFinite(minY) && isFinite(maxX) && isFinite(maxY)) {
      const pad = 8
      const w = Math.max(1, (maxX - minX) + pad * 2)
      const h = Math.max(1, (maxY - minY) + pad * 2)
      viewBoxAttr.value = `${minX - pad} ${minY - pad} ${w} ${h}`
    }
  })
}

onMounted(() => {
  computeLabelPositions()
  setTimeout(computeLabelPositions, 50)
})

function fontSizeFor(uf) {
  const small = new Set(['SE','AL','PB','RN','DF','ES','RJ','SE'])
  return small.has(uf) ? 20 : 24
}

function gradientFrom(uf) {
  const t = normalizedSales.value[uf] || 0.6
  // azul claro variável
  return `rgba(147,197,253,${0.3 + t * 0.4})`
}
function gradientTo(uf) {
  const t = normalizedSales.value[uf] || 0.6
  // azul mais forte
  return `rgba(37,99,235,${0.4 + t * 0.5})`
}

function fillFor(uf) {
  uf = (uf || '').toUpperCase()
  if (!props.colorful) return undefined
  const hasSale = (props.salesByUf && Number(props.salesByUf[uf]) > 0)
  if (!hasSale) return '#e5e7eb'
  return `url(#grad-${uf})`
}
</script>

<style scoped>
.svg-map__location {
  stroke: #9ca3af; /* gray-400 */
  stroke-width: 1;
  transition: fill 0.15s ease, filter 0.15s ease, stroke 0.15s ease;
  cursor: pointer;
}
.svg-map__location[aria-checked='true'] {
  fill: #2563eb; /* blue-600 */
}
.svg-map__location.is-hover {
  filter: brightness(1.12);
  stroke: #1d4ed8; /* blue-700 */
  stroke-width: 2;
}

.state-label {
  fill: #111827; /* gray-900 */
  stroke: #ffffff;
  stroke-width: 2px;
  paint-order: stroke fill;
  font-weight: 500; /* sem negrito pesado */
}
</style>


