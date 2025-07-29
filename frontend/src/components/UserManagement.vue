<template>
  <div class="user-management">
    <h2>User Management</h2>
    <form @submit.prevent="addUser">
      <input v-model="newUser.username" placeholder="Username" required />
      <input v-model="newUser.email" placeholder="Email" required />
      <input v-model="newUser.role" placeholder="Role" required />
      <button type="submit">Add User</button>
    </form>
    <ul>
      <li v-for="u in users" :key="u.id">
        <span>{{ u.username }} ({{ u.email }}, {{ u.role }})</span>
        <button @click="editUser(u)">Edit</button>
        <button @click="deleteUser(u.id)">Delete</button>
      </li>
    </ul>
    <div v-if="editing">
      <h3>Edit User</h3>
      <form @submit.prevent="updateUser">
        <input v-model="editForm.username" required />
        <input v-model="editForm.email" required />
        <input v-model="editForm.role" required />
        <button type="submit">Update</button>
        <button @click="cancelEdit" type="button">Cancel</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const users = ref([]);
const newUser = ref({ username: '', email: '', role: '' });
const editing = ref(false);
const editForm = ref({ id: null, username: '', email: '', role: '' });

const fetchUsers = async () => {
  const res = await axios.get('http://localhost:5000/api/users');
  users.value = res.data;
};

const addUser = async () => {
  await axios.post('http://localhost:5000/api/users', newUser.value);
  newUser.value = { username: '', email: '', role: '' };
  fetchUsers();
};

const editUser = (u) => {
  editing.value = true;
  editForm.value = { ...u };
};

const updateUser = async () => {
  await axios.put(`http://localhost:5000/api/users/${editForm.value.id}`, editForm.value);
  editing.value = false;
  fetchUsers();
};

const deleteUser = async (id) => {
  await axios.delete(`http://localhost:5000/api/users/${id}`);
  fetchUsers();
};

const cancelEdit = () => {
  editing.value = false;
};

onMounted(fetchUsers);
</script>

<style scoped>
.user-management {
  max-width: 600px;
  margin: 2rem auto;
  background: #fff;
  padding: 2rem;
  border-radius: 8px;
  border: 1px solid #ddd;
}
form {
  margin-bottom: 1rem;
}
ul {
  list-style: none;
  padding: 0;
}
li {
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}
</style> 