<!-- src/views/AccessDenied.vue -->
<template>
  <div class="flex flex-col items-center justify-center h-screen text-center">
    <h1 class="text-4xl font-bold mb-4 text-red-600">Acesso Negado</h1>
    <p class="text-lg mb-6">Você não tem permissão para acessar esta página.</p>
    <router-link
      to="/dashboard"
      class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
    >
      Voltar para o Dashboard
    </router-link>
  </div>
</template>
