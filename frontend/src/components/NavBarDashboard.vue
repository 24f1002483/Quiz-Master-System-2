<template>
  <header class="navbar">
    <nav class="nav-links">
      <router-link v-for="link in navLinks" :key="link.text" :to="link.to" class="nav-link">{{ link.text }}</router-link>
      <button v-if="showLogout" @click="onLogout" class="logout-btn">Logout</button>
    </nav>
    <div class="search-bar">
      <button @click="onSearch" class="search-btn">Search</button>
    </div>
    <div class="welcome-msg">Welcome {{ welcomeName }}</div>
  </header>
</template>

<script setup>
import { computed } from 'vue';
const props = defineProps({
  userType: { type: String, required: true }, // 'admin' or 'user'
  welcomeName: { type: String, required: true },
  onLogout: { type: Function, required: true },
  onSearch: { type: Function, required: true },
});
const navLinks = computed(() => {
  console.log('NavBarDashboard userType:', props.userType);
  if (props.userType === 'admin') {
    const links = [
      { text: 'Home', to: '/admin' },
      { text: 'Quiz', to: '/admin/quizzes' },
      { text: 'Export', to: '/admin/export' },
      { text: 'Summary', to: '/admin/summary' },
    ];
    console.log('Admin nav links:', links);
    return links;
  } else {
    const links = [
      { text: 'Home', to: '/user' },
      { text: 'Scores', to: '/user/scores' },
      { text: 'Summary', to: '/user/summary' },
    ];
    console.log('User nav links:', links);
    return links;
  }
});
const showLogout = true;
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #7ecbfa;
  border: 2px solid orange;
  border-radius: 16px 16px 0 0;
  padding: 0.5rem 1.5rem;
  min-height: 48px;
  margin-bottom: 1rem;
}
.nav-links {
  display: flex;
  align-items: center;
  gap: 1.2rem;
}
.nav-link {
  color: #1ca01c;
  text-decoration: none;

  font-weight: 500;
  font-size: 1.05rem;
}
.nav-link.router-link-exact-active {
  text-decoration: underline;
}
.logout-btn {
  background: #e74c3c;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.3rem 0.9rem;
  margin-left: 1rem;
  cursor: pointer;
  font-weight: 500;
}
.search-bar {
  display: flex;
  align-items: center;
}
.search-btn {
  background: #fff;
  border: 2px solid #222;
  border-radius: 8px;
  padding: 0.2rem 1.2rem;
  font-weight: 600;
  cursor: pointer;
  font-size: 1rem;
  box-shadow: 1px 1px 2px #ccc;
}
.welcome-msg {
  color: #1a6ec1;
  font-weight: 600;
  font-size: 1.1rem;
}
</style> 