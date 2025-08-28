<template>
  <li :style="liStyle">
    <div class="inline-flex items-center gap-2">
      <button v-if="hasChildren" @click="onToggle(node)" class="w-6 h-6 inline-flex items-center justify-center rounded border text-xs bg-white hover:bg-gray-50">
        {{ isCollapsed ? '+' : '−' }}
      </button>
      <span class="tree-node" :class="badgeClass">{{ node.user?.username }} <small class="opacity-60">({{ countDesc(node)-1 }})</small></span>
    </div>
    <ul v-if="hasChildren && !isCollapsed">
      <TreeNode v-for="child in node.children" :key="child.id || child.user?.username" :node="child" :level="level+1" :indent="indent" :collapsed-set="collapsedSet" :on-toggle="onToggle" />
    </ul>
  </li>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
  node: { type: Object, required: true },
  level: { type: Number, default: 0 },
  indent: { type: Number, default: 24 },
  collapsedSet: { type: Object, default: () => new Set() },
  onToggle: { type: Function, default: () => {} }
})
const node = props.node
const countDesc = (n) => 1 + (n.children?.reduce((acc,c)=>acc+countDesc(c),0) || 0)
const hasChildren = computed(() => (node.children?.length || 0) > 0)
const nodeId = computed(() => node.id || node.user?.username)
const isCollapsed = computed(() => props.collapsedSet?.has(nodeId.value))
const colors = [
  'bg-blue-50 border-blue-300 text-blue-800',
  'bg-emerald-50 border-emerald-300 text-emerald-800',
  'bg-purple-50 border-purple-300 text-purple-800',
  'bg-orange-50 border-orange-300 text-orange-800',
  'bg-amber-50 border-amber-300 text-amber-800'
]
const badgeClass = computed(() => colors[props.level % colors.length])
const liStyle = computed(() => ({ marginLeft: props.level ? `${props.indent}px` : '0px', marginTop: '8px' }))
</script>

<style scoped>
ul { padding-left: 1rem; border-left: 1px dashed #cbd5e1; margin-left: .5rem; }
.tree-node { display: inline-block; padding: 6px 10px; border: 1px solid; border-radius: 8px; }
</style>













