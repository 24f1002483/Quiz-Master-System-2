<template>
  <div class="auth-bg">
    <div class="auth-card">
      <h2>Login to Quiz Master</h2>
      <form @submit.prevent="login">
        <label>Username:</label>
        <input v-model="form.username" required placeholder="Enter your username" />
        <label>Password:</label>
        <input v-model="form.password" type="password" required placeholder="Enter your password" />
        <button type="submit">Login</button>
      </form>
      <div class="links">
        <router-link to="/register">New user?</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { loginAdmin } from '../services/authService.js';
import { useRouter } from 'vue-router';
import { checkAuth } from '../services/authService.js';

const router = useRouter();
const form = ref({ username: '', password: '' });

const login = async () => {
  try {
    const response = await loginAdmin(form.value.username, form.value.password);
    
    // Store the JWT token in localStorage
    if (response.access_token) {
      localStorage.setItem('token', response.access_token);
    }
    
    const user = await checkAuth();
    if (user.role === 'admin') {
      router.push('/admin/dashboard');
    } else {
      router.push('/dashboard');
    }
  } catch (err) {
    alert(err.message || 'Login failed');
  }
};
</script>

<style scoped>
/* You can reuse the styles from your Register.vue for consistency */
.auth-bg {
  min-height: 100vh;
  background: linear-gradient(135deg, #e0e7ff 60%, #f5f5f5 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}
.auth-card {
  background: #fff;
  padding: 2.5rem 2.5rem 2rem 2.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(44, 62, 80, 0.10);
  max-width: 400px;
  width: 100%;
  text-align: center;
}
.auth-card h2 {
  margin-bottom: 1.5rem;
  color: #2c3e50;
  font-size: 1.7rem;
  font-weight: 700;
}
form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
label {
  text-align: left;
  color: #555;
  font-size: 1rem;
  margin-bottom: 0.2rem;
}
input {
  padding: 0.7rem 1rem;
  border: 1px solid #cfd8dc;
  border-radius: 8px;
  font-size: 1rem;
  transition: border 0.2s, box-shadow 0.2s;
  outline: none;
}
input:focus {
  border: 1.5px solid #42b983;
  box-shadow: 0 0 0 2px #e0f7fa;
}
button {
  background: linear-gradient(90deg, #42b983 60%, #4f8cff 100%);
  color: #fff;
  font-weight: 600;
  padding: 0.8rem 0;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  margin-top: 0.5rem;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(79, 140, 255, 0.13);
  transition: background 0.2s, box-shadow 0.2s;
}
button:hover {
  background: linear-gradient(90deg, #4f8cff 60%, #42b983 100%);
  box-shadow: 0 4px 16px rgba(66, 185, 131, 0.18);
}
.links {
  margin-top: 1.2rem;
}
.links a {
  color: #4f8cff;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}
.links a:hover {
  color: #42b983;
}
</style> 