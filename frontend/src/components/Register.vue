<template>
  <div class="auth-bg">
    <div class="auth-card">
      <h2>Register for Quiz Master</h2>
      <form @submit.prevent="register">
        <label>Username:</label>
        <input v-model="form.username" required placeholder="Enter your username" />
        <label>Password:</label>
        <input v-model="form.password" type="password" required placeholder="Create a password" />
        <label>Full Name:</label>
        <input v-model="form.fullName" required placeholder="Enter your full name" />
        <label>Qualification:</label>
        <select v-model="form.qualification" required>
          <option disabled value="">Select your qualification</option>
          <option>High School</option>
          <option>Diploma</option>
          <option>Bachelor's Degree</option>
          <option>Master's Degree</option>
          <option>PhD</option>
          <option>Other</option>
        </select>
        <label>Date of Birth:</label>
        <input v-model="form.dob" type="date" />
        <button type="submit">Submit</button>
      </form>
      <div class="links">
        <router-link to="/login">Existing user?</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { registerUser } from '../services/authService.js';

const form = ref({ username: '', password: '', fullName: '', qualification: '', dob: '' });

const register = async () => {
  try {
    await registerUser({
      username: form.value.username,
      password: form.value.password,
      full_name: form.value.fullName,
      qualification: form.value.qualification,
      dob: form.value.dob
    });
    alert('Registration successful!');
  } catch (err) {
    alert(err.message || 'Registration failed');
  }
};
</script>

<style scoped>
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
input,
select {
  padding: 0.7rem 1rem;
  border: 1px solid #cfd8dc;
  border-radius: 8px;
  font-size: 1rem;
  transition: border 0.2s, box-shadow 0.2s;
  outline: none;
  background: #fff;
}
input:focus,
select:focus {
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