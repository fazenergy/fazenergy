<template>
  <!-- Área de login com fundo "hero" sutil e interativo -->
  <div ref="heroRef" @mousemove="handleMouse" class="relative flex items-center justify-center min-h-screen bg-[#0e1625] overflow-hidden">
    <!-- Camada decorativa: blobs suaves com blur (sem impactar interação) -->
    <div aria-hidden="true" class="pointer-events-none absolute inset-0 z-0">
      <div class="magnet blob-1" />
      <div class="magnet blob-2" />
      <div class="magnet blob-3" />
      <!-- Logo de fundo, sutil, mesclando com o background -->
      <div class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
        <img v-if="bgLogoUrl" :src="bgLogoUrl" alt="bg-logo" class="bg-logo mix-blend-soft-light" />
      </div>
    </div>

    <div class="relative z-10 bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg w-full max-w-md">
      <div class="mb-4 flex flex-col items-center gap-2">
        <img v-if="logoLoginUrl" :src="logoLoginUrl" alt="logo-login" class="h-12 object-contain" />
        <h1 class="text-2xl font-bold text-center text-gray-800 dark:text-white">Acesso ao Sistema</h1>
      </div>
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
        <!-- Campo OTP (2FA) opcional: exibido quando necessário -->
        <div v-if="showOtp">
          <label class="block mb-1 text-gray-700 dark:text-gray-300">Código 2FA</label>
          <input
            v-model="otp"
            type="text"
            inputmode="numeric"
            maxlength="6"
            placeholder="000000"
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth' // Importa o store de autenticação '../../store/auth'
import { useSettingsStore } from '@/store/settings'

const username = ref('')
const password = ref('')
const otp = ref('')
const showOtp = ref(false)
const router = useRouter()
const auth = useAuthStore()
const settingsStore = useSettingsStore()

onMounted(() => settingsStore.loadFromStorage())
const logoLoginUrl = computed(() => settingsStore.settings.general.logo_login_data_url)
// Usa a logo principal como marca d'água de fundo
const bgLogoUrl = computed(() => settingsStore.settings.general.logo_data_url || settingsStore.settings.general.logo_login_data_url)

// Efeito magnético sutil: desloca levemente as "blobs" conforme o mouse
const heroRef = ref(null)
function handleMouse(e) {
  if (!heroRef.value) return
  const rect = heroRef.value.getBoundingClientRect()
  const x = (e.clientX - rect.left) / rect.width - 0.5
  const y = (e.clientY - rect.top) / rect.height - 0.5
  const moveX = (x * 40).toFixed(1) + 'px'
  const moveY = (y * 40).toFixed(1) + 'px'
  heroRef.value.style.setProperty('--mx', moveX)
  heroRef.value.style.setProperty('--my', moveY)
}

const handleLogin = async () => {
  try {
    // Envia OTP quando houver (o backend exigirá se 2FA estiver habilitado)
    await auth.login(username.value, password.value, otp.value || undefined)
    router.push('/dashboard')
  } catch (error) {
    // Heurística simples: se o backend sinalizar 2FA ausente, mostra o campo
    const needsOtp = /2FA/i.test(error?.response?.data?.detail || '')
    if (needsOtp) showOtp.value = true
    alert(error?.response?.data?.detail || 'Credenciais inválidas. Tente novamente.')
    console.error(error)
  }
}
</script>

<style scoped>
/* Fundo hero magnético (profissional e discreto) */
.magnet {
  position: absolute;
  border-radius: 9999px;
  filter: blur(60px);
  opacity: 0.30; /* intensidade suave */
  transform: translate3d(var(--mx, 0px), var(--my, 0px), 0);
  transition: transform 120ms ease-out; /* efeito "magnético" sutil ao mouse */
}

/* Três blobs em posições opostas para criar profundidade */
.blob-1 {
  width: 520px; height: 520px;
  left: -160px; top: -160px;
  background: radial-gradient(35% 35% at 50% 50%, rgba(52, 211, 153, 0.55), rgba(52, 211, 153, 0.0) 70%);
}
.blob-2 {
  width: 560px; height: 560px;
  right: -180px; top: -120px;
  background: radial-gradient(35% 35% at 50% 50%, rgba(99, 102, 241, 0.55), rgba(99, 102, 241, 0.0) 70%);
}
.blob-3 {
  width: 640px; height: 640px;
  left: -120px; bottom: -220px;
  background: radial-gradient(35% 35% at 50% 50%, rgba(56, 189, 248, 0.55), rgba(56, 189, 248, 0.0) 70%);
}

.bg-logo {
  /* Tamanho grande, responsivo e central */
  width: clamp(560px, 80vw, 1200px);
  height: auto;
  opacity: 0.06; /* bem transparente */
  filter: grayscale(10%) brightness(120%);
}

/* Acessibilidade: reduz animação quando prefer-reduced-motion */
@media (prefers-reduced-motion: reduce) {
  .magnet { transition: none; }
}
</style>
