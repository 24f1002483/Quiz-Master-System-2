<template>
  <div id="app">
    <NavBar />
    <main>
      <router-view />
    </main>
  </div>
  <div class="welcome-content">
    <h1>Welcome to Quiz Master!</h1>
    <p>Test your knowledge and track your progress. Please use the navigation bar to register or log in.</p>
    <div class="lively-graphic">
      <span>🎉</span>
      <span>🧠</span>
      <span>🏆</span>
    </div>
  </div>
</template>

<script setup>
import NavBar from './NavBar.vue';
</script>

<style scoped>
.welcome-content {
  background: #2c3e50;
  color: #fff;
  text-align: center;
  margin-top: 100px;
  padding: 3rem 2rem;
  border-radius: 12px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  box-shadow: 0 2px 8px rgba(44, 62, 80, 0.08);
  position: relative;
  animation: fadeIn 1.2s;
}
.welcome-content h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  font-family: 'Segoe UI', Arial, sans-serif;
  letter-spacing: 1px;
}
.welcome-content p {
  font-size: 1.2rem;
  margin-bottom: 1.5rem;
}
.lively-graphic {
  font-size: 2.5rem;
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-top: 2rem;
  animation: bounceIn 1.2s;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(40px);}
  to { opacity: 1; transform: translateY(0);}
}
@keyframes bounceIn {
  0% { transform: scale(0.7);}
  60% { transform: scale(1.1);}
  100% { transform: scale(1);}
}
</style>
