<template>
  <div class="flex items-center justify-center min-h-screen bg-gradient-to-r from-purple-500 to-blue-500 dark:from-gray-900 dark:to-gray-800">
    <div class="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg w-full max-w-md">
      <h1 class="text-2xl font-bold mb-6 text-center text-gray-800 dark:text-white">
        Acesso ao Sistema
      </h1>
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block mb-1 text-gray-700 dark:text-gray-300">Usuário</label>
          <input
            v-model="username"
            type="text"
            placeholder="login"
            class="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          />
        </div>
        <div>
          <label class="block mb-1 text-gray-700 dark:text-gray-300">Senha</label>
          <input
            v-model="password"
            type="password"
            placeholder="******"
            class="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          />
        </div>
        <button
          type="submit"
          class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded transition duration-200"
        >
          Entrar
        </button>
      </form>
      <p class="text-xs text-gray-600 dark:text-gray-400 mt-4 text-center">
        Esqueceu a senha? <a href="#" class="underline">Resetar como admin</a>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth' // Importa o store de autenticação '../../store/auth'

const username = ref('')
const password = ref('')
const router = useRouter()
const auth = useAuthStore()

const handleLogin = async () => {
  try {
    await auth.login(username.value, password.value)
    router.push('/dashboard')
  } catch (error) {
    alert('Credenciais inválidas. Tente novamente.')
    console.error(error)
  }
}
</script>
