<template>
  <div class="chapter-management">
    <h2>Chapter Management</h2>
    <ul>
      <li v-for="chapter in chapters" :key="chapter.id">
        <span>{{ chapter.name }} - {{ chapter.description }}</span>
        <button @click="editChapter(chapter)">Edit</button>
        <button @click="deleteChapterHandler(chapter.id)">Delete</button>
      </li>
    </ul>
    <button @click="showAddChapter = true">+ Chapter</button>
    <div v-if="showAddChapter" class="modal">
      <div class="modal-content">
        <h3>New Chapter</h3>
        <input v-model="newChapter.name" placeholder="Name" />
        <input v-model="newChapter.description" placeholder="Description" />
        <select v-model="newChapter.subject_id">
          <option disabled value="">Select Subject</option>
          <option v-for="subject in subjects" :key="subject.id" :value="subject.id">{{ subject.name }}</option>
        </select>
        <button @click="addChapter">Save</button>
        <button @click="showAddChapter = false">Cancel</button>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { fetchSubjects } from '../services/subjectService.js';
const chapters = ref([]);
const showAddChapter = ref(false);
const newChapter = ref({ name: '', description: '', subject_id: '' });
const subjects = ref([]);
const loadChapters = async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/chapters');
    chapters.value = res.data;
  } catch (e) {
    alert('Failed to load chapters');
  }
};
const loadSubjects = async () => {
  try {
    subjects.value = await fetchSubjects();
  } catch (e) {
    alert('Failed to load subjects');
  }
};
const addChapter = async () => {
  if (newChapter.value.name && newChapter.value.subject_id) {
    await axios.post('http://localhost:5000/api/chapters', newChapter.value);
    newChapter.value = { name: '', description: '', subject_id: '' };
    showAddChapter.value = false;
    loadChapters();
  } else {
    alert('Please enter all fields and select a subject.');
  }
};
const editChapter = (chapter) => {
  // Implement edit modal if needed
  alert('Edit chapter: ' + chapter.name);
};
const deleteChapterHandler = async (id) => {
  await axios.delete(`http://localhost:5000/api/chapters/${id}`);
  loadChapters();
};
onMounted(() => {
  loadChapters();
  loadSubjects();
});
</script>
<style scoped>
.chapter-management { max-width: 600px; margin: 2rem auto; background: #fff; padding: 2rem; border-radius: 8px; }
ul { list-style: none; padding: 0; }
li { margin-bottom: 0.5rem; display: flex; align-items: center; gap: 1rem; }
button { margin-right: 0.5rem; }
.modal { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; }
.modal-content { background: #fff; padding: 2rem; border-radius: 8px; min-width: 300px; display: flex; flex-direction: column; gap: 1rem; }
</style>