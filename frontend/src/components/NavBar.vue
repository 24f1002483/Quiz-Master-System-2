<template>
  <header class="app-header">
    <h1 class="logo">Quiz Master</h1>
    <nav>
      <router-link to="/login">Login</router-link>
      <router-link to="/register">Register</router-link>
    </nav>
  </header>
</template>

<script setup>
// No script logic needed for static nav
</script>

<style scoped>
.app-header {
  background: #2c3e50;
  color: #fff;
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(44, 62, 80, 0.08);
}
.logo {
  margin: 0;
  font-size: 2rem;
  letter-spacing: 1px;
  font-family: 'Segoe UI', Arial, sans-serif;
}
nav {
  display: flex;
  gap: 1.5rem;
}
nav a {
  color: #fff;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}
nav a.router-link-exact-active {
  color: #42b983;
}
nav a:hover {
  color: #a5d6a7;
}
</style>
