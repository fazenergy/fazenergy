<template>
  <li>
    <span class="tree-node">{{ node.user?.username }} <small class="opacity-60">({{ countDesc(node)-1 }})</small></span>
    <ul v-if="node.children?.length">
      <TreeNode v-for="child in node.children" :key="child.id" :node="child" />
    </ul>
  </li>
</template>

<script setup>
const props = defineProps({ node: { type: Object, required: true } })
const node = props.node
const countDesc = (n) => 1 + (n.children?.reduce((acc,c)=>acc+countDesc(c),0) || 0)
</script>

<style scoped>
ul { padding-left: 1rem; border-left: 1px dashed #cbd5e1; margin-left: .5rem; }
.tree-node { display: inline-block; padding: 4px 8px; background: #fff; border: 1px solid #e5e7eb; border-radius: 4px; }
</style>





