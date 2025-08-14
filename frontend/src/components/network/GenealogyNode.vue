<template>
  <div class="gene-node">
    <!-- Card estilizado -->
    <div class="card">
      <div class="card-header">
        <div class="avatar-wrap">
          <img :src="avatarSrc" alt="avatar" class="avatar" />
          <span class="status" title="Ativo">✓</span>
        </div>
        <div class="info">
          <div class="name">{{ displayName }}</div>
          <div class="username">@{{ username }}</div>
          <div class="meta">
            <span class="meta-item">📅 {{ joinDate }}</span>
            <span class="meta-item">👥 Diretos: {{ directsCount }}</span>
            <span class="meta-item">🧩 Equipe: {{ teamCount }}</span>
          </div>
        </div>
        <div class="actions">
          <button class="btn-actions" @click="toggleMenu">Ações ▾</button>
          <div v-if="showMenu" class="menu" @click.stop>
            <button class="menu-item" @click="emit('viewProfile', node)">Ver Perfil</button>
            <button class="menu-item" @click="emit('message', node)">Enviar Mensagem</button>
          </div>
        </div>
      </div>
      <div class="card-footer">
        <span class="level">▦ Nvl. {{ level }}</span>
      </div>
    </div>

    <!-- Filhos -->
    <div v-if="node.children?.length" class="gene-children">
      <GenealogyNode v-for="child in node.children" :key="child.id" :node="child" />
    </div>
  </div>
  
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({ node: { type: Object, required: true } })
const emit = defineEmits(['viewProfile','message'])

const username = computed(() => props.node.user?.username || 'usuario')
const displayName = computed(() => props.node.display_name || username.value.toUpperCase())
const directsCount = computed(() => props.node.children?.length || 0)

function countDesc(n) {
  return 1 + (n.children?.reduce((acc, c) => acc + countDesc(c), 0) || 0)
}
const teamCount = computed(() => Math.max(countDesc(props.node) - 1, 0))
const level = computed(() => props.node.level || 1)
const joinDate = computed(() => {
  const iso = props.node.dtt_record
  if (!iso) return '-'
  const d = new Date(iso)
  return d.toLocaleDateString('pt-BR')
})
const avatarSrc = computed(() => props.node.user?.image_profile || 'https://placehold.co/64x64/png')

const showMenu = ref(false)
function toggleMenu(ev) {
  ev?.stopPropagation?.()
  showMenu.value = !showMenu.value
  if (showMenu.value) {
    const onDoc = () => { showMenu.value = false; document.removeEventListener('click', onDoc) }
    document.addEventListener('click', onDoc)
  }
}
</script>

<style scoped>
.gene-node { text-align: left; display: inline-block; }
.card { width: 310px; background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 2px rgba(0,0,0,.06); overflow: hidden; }
.card-header { display: flex; align-items: center; gap: 10px; padding: 10px 12px; }
.avatar-wrap { position: relative; }
.avatar { width: 52px; height: 52px; border-radius: 9999px; object-fit: cover; border: 3px solid #22c55e; }
.status { position: absolute; right: -2px; bottom: -2px; background: #22c55e; color: #fff; border-radius: 9999px; font-size: 10px; width: 16px; height: 16px; display: grid; place-items: center; border: 2px solid #fff; }
.info { flex: 1; min-width: 0; }
.name { font-weight: 700; font-size: 14px; line-height: 1.1; color: #0f172a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.username { font-size: 12px; color: #64748b; }
.meta { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 2px; font-size: 12px; color: #334155; }
.meta-item { display: inline-flex; align-items: center; gap: 4px; }
.actions { position: relative; }
.btn-actions { background: #0ea5e9; color: #fff; border: none; border-radius: 9999px; padding: 6px 10px; font-size: 12px; cursor: pointer; }
.menu { position: absolute; right: 0; top: 30px; background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; box-shadow: 0 10px 20px rgba(15,23,42,.08); min-width: 140px; z-index: 10; }
.menu-item { display: block; width: 100%; text-align: left; padding: 8px 10px; background: transparent; border: none; cursor: pointer; font-size: 12px; }
.menu-item:hover { background: #f1f5f9; }
.card-footer { border-top: 1px solid #e5e7eb; padding: 8px 12px; display: flex; justify-content: space-between; align-items: center; }
.level { font-size: 12px; color: #475569; }
.gene-children { display: flex; justify-content: center; gap: 16px; margin-top: 14px; }
</style>

