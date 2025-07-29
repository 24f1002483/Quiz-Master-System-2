<template>
  <div class="subject-management">
    <h2>Subject Management</h2>
    <ul>
      <li v-for="subject in subjects" :key="subject.id">
        <span>{{ subject.name }} - {{ subject.description }}</span>
        <button @click="editSubject(subject)">Edit</button>
        <button @click="deleteSubjectHandler(subject.id)">Delete</button>
      </li>
    </ul>
    <button @click="showAddSubject = true">+ Subject</button>
    <div v-if="showAddSubject" class="modal">
      <div class="modal-content">
        <h3>New Subject</h3>
        <input v-model="newSubject.name" placeholder="Name" />
        <input v-model="newSubject.description" placeholder="Description" />
        <button @click="addSubject">Save</button>
        <button @click="showAddSubject = false">Cancel</button>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import { fetchSubjects, createSubject, updateSubject, deleteSubject } from '../services/subjectService';
const subjects = ref([]);
const showAddSubject = ref(false);
const newSubject = ref({ name: '', description: '' });
const loadSubjects = async () => {
  try {
    subjects.value = await fetchSubjects();
  } catch (e) {
    alert('Failed to load subjects');
  }
};
const addSubject = async () => {
  if (newSubject.value.name) {
    await createSubject(newSubject.value);
    newSubject.value = { name: '', description: '' };
    showAddSubject.value = false;
    loadSubjects();
  }
};
const editSubject = (subject) => {
  // Implement edit modal if needed
  alert('Edit subject: ' + subject.name);
};
const deleteSubjectHandler = async (id) => {
  await deleteSubject(id);
  loadSubjects();
};
onMounted(loadSubjects);
</script>
<style scoped>
.subject-management { max-width: 600px; margin: 2rem auto; background: #fff; padding: 2rem; border-radius: 8px; }
ul { list-style: none; padding: 0; }
li { margin-bottom: 0.5rem; display: flex; align-items: center; gap: 1rem; }
button { margin-right: 0.5rem; }
.modal { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; }
.modal-content { background: #fff; padding: 2rem; border-radius: 8px; min-width: 300px; display: flex; flex-direction: column; gap: 1rem; }
</style>