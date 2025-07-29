<template>
  <div id="app">
    <main>
      <router-view />
    </main>
    <SessionWarning />
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import sessionService from '../services/sessionService.js';
import SessionWarning from './SessionWarning.vue';

const router = useRouter();

onMounted(() => {
  // Only initialize session service if user is logged in
  const token = localStorage.getItem('token');
  const user = localStorage.getItem('user');
  
  if (token && user) {
    console.log('User is logged in, initializing session service');
    sessionService.init();
  } else {
    console.log('No user logged in, skipping session service initialization');
  }
});

onUnmounted(() => {
  // Cleanup session service when app unmounts
  sessionService.cleanup();
});
</script>

<style scoped>
#app {
  font-family: 'Segoe UI', Arial, sans-serif;
  background: linear-gradient(135deg, #f5f5f5 60%, #e0e7ff 100%);
  min-height: 100vh;
}
main {
  padding: 2rem;
}
</style> 