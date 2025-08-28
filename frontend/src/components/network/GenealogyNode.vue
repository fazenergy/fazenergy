<template>
  <div class="gene-node" :class="{ 'has-children': hasChildren }">
    <!-- Card do licenciado -->
    <div class="card" :class="levelClass">
      <img :src="avatarSrc" alt="avatar" class="avatar" />
      <div class="info">
        <div class="name">{{ displayName }}</div>
        <div class="username">@{{ username }}</div>
        <div class="stats">
          <span>👥 Diretos: {{ directsCount }}</span>
          <span>▦ Nvl. {{ level }}</span>
        </div>
      </div>
      <!-- Toggle central inferior, preso ao card -->
      <button v-if="hasChildren" class="toggle-btn" @click="collapse = !collapse">{{ collapse ? '+' : '−' }}</button>
    </div>

    <!-- Conector vertical pai → linha horizontal dos filhos -->
    <div v-if="hasChildren && !collapse" class="connector-v"></div>

    <!-- Conexões + Filhos -->
    <div v-if="hasChildren && !collapse" class="gene-children">
      <div class="children-hline"></div>
      <div class="children-wrap">
        <div v-for="child in limitedChildren" :key="child.id" class="child-slot">
          <div class="child-vline"></div>
          <GenealogyNode :node="child" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
defineOptions({ name: 'GenealogyNode' })

const props = defineProps({ node: { type: Object, required: true } })

const username = computed(() => props.node.user?.username || 'usuario')
const displayName = computed(() => props.node.display_name || username.value.toUpperCase())
const directsCount = computed(() => props.node.children?.length || 0)
const level = computed(() => Number(props.node.level || 1))
const hasChildren = computed(() => (props.node.children && props.node.children.length > 0))
const defaultAvatar =
  'data:image/svg+xml;utf8,' +
  encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="64" height="64">
      <circle cx="12" cy="8" r="4" fill="#cbd5e1" />
      <path d="M4 20c0-3.3137 3.134-6 8-6s8 2.6863 8 6" fill="#e2e8f0" />
      <circle cx="12" cy="12" r="11" fill="none" stroke="#94a3b8" stroke-width="1.5" />
    </svg>`
  )
const avatarSrc = computed(() => props.node.user?.image_profile || defaultAvatar)

const levelClass = computed(() => {
  switch (level.value) {
    case 1: return 'lvl-1'
    case 2: return 'lvl-2'
    case 3: return 'lvl-3'
    case 4: return 'lvl-4'
    case 5: return 'lvl-5'
    default: return 'lvl-6'
  }
})

// Colapso individual (por nó)
const collapse = ref(false)
const limitedChildren = computed(() => props.node.children || [])
</script>

<style scoped>
.gene-node { text-align: center; display: inline-block; position: relative; padding: 10px 12px; }

.card { position: relative; width: 200px; background: #fff; border: 2px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 2px rgba(0,0,0,.06); padding: 8px; display: inline-flex; align-items: center; gap: 10px; }
.avatar { width: 40px; height: 40px; border-radius: 9999px; object-fit: cover; border: 3px solid #e5e7eb; }
.info { text-align: left; }
.name { font-weight: 700; font-size: 13px; line-height: 1.1; color: #0f172a; }
.username { font-size: 11px; color: #64748b; margin-top: 2px; }
.stats { margin-top: 4px; display: flex; gap: 8px; font-size: 11px; color: #334155; }

/* Children connectors */
.connector-v { width: 2px; height: 12px; background: #cbd5e1; margin: 0 auto; }
.gene-children { margin-top: -2px; }
.children-hline { height: 2px; background: #cbd5e1; width: 100%; position: relative; left: 0; }
.children-wrap { display: flex; justify-content: center; gap: 18px; margin-top: 0; }
.child-slot { position: relative; padding-top: 8px; }
.child-vline { position: absolute; top: 0; left: 50%; width: 2px; height: 20px; background: #cbd5e1; transform: translateX(-50%); }

/* Level colors */
.lvl-1 { border-color: #22c55e; }
.lvl-1 .avatar { border-color: #22c55e; }
.lvl-2 { border-color: #2563eb; }
.lvl-2 .avatar { border-color: #2563eb; }
.lvl-3 { border-color: #f59e0b; }
.lvl-3 .avatar { border-color: #f59e0b; }
.lvl-4 { border-color: #a855f7; }
.lvl-4 .avatar { border-color: #a855f7; }
.lvl-5 { border-color: #ef4444; }
.lvl-5 .avatar { border-color: #ef4444; }
.lvl-6 { border-color: #64748b; }
.lvl-6 .avatar { border-color: #64748b; }

/* Toggle button central */
.toggle-btn {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  bottom: -12px;
  width: 24px;
  height: 24px;
  border: 1px solid #cbd5e1;
  background: #fff;
  border-radius: 6px;
  line-height: 1;
  font-weight: 700;
  z-index: 1;
}
</style>

