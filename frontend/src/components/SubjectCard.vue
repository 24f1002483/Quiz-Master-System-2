<template>
  <div class="subject-card">
    <h3>{{ subject.name }}</h3>
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Chapter name</th>
            <th>No. of Questions</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="chapter in subject.chapters" :key="chapter.id">
            <td>{{ chapter.name }}</td>
            <td>{{ chapter.questionCount }}</td>
            <td class="action-buttons">
              <button class="edit-btn" @click="handleEditChapter(chapter)">Edit</button>
              <button class="delete-btn" @click="$emit('delete-chapter', chapter.id)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <button class="add-chapter-btn" @click="$emit('add-chapter', subject)">+ Chapter</button>
  </div>
</template>
<script setup>
defineProps(['subject']);
const emit = defineEmits(['edit-chapter', 'delete-chapter', 'add-chapter']);

const handleEditChapter = (chapter) => {
  console.log('Edit button clicked for chapter:', chapter);
  emit('edit-chapter', chapter);
};
</script>
<style scoped>
.subject-card {
  background: #fff;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 24px rgba(44, 62, 80, 0.10);
  min-width: 300px;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  border: 1px solid #e0e7ff;
}

.subject-card h3 {
  color: #2c3e50;
  font-size: 1.4rem;
  font-weight: 700;
  margin: 0;
  text-align: center;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e0e7ff;
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
}

th, td {
  padding: 0.8rem;
  text-align: left;
  border-bottom: 1px solid #e0e7ff;
}

th {
  background: linear-gradient(90deg, #e0e7ff 0%, #f5f5f5 100%);
  color: #2c3e50;
  font-weight: 600;
  font-size: 0.9rem;
}

td {
  color: #555;
  font-size: 0.9rem;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.edit-btn, .delete-btn {
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.edit-btn {
  background: linear-gradient(90deg, #42b983 60%, #4f8cff 100%);
  color: white;
}

.edit-btn:hover {
  background: linear-gradient(90deg, #4f8cff 60%, #42b983 100%);
  box-shadow: 0 2px 8px rgba(66, 185, 131, 0.3);
}

.delete-btn {
  background: #e74c3c;
  color: white;
}

.delete-btn:hover {
  background: #c0392b;
  box-shadow: 0 2px 8px rgba(231, 76, 60, 0.3);
}

.add-chapter-btn {
  background: linear-gradient(90deg, #42b983 60%, #4f8cff 100%);
  color: #fff;
  font-weight: 600;
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(79, 140, 255, 0.13);
  transition: background 0.2s, box-shadow 0.2s;
  align-self: center;
  margin-top: auto;
}

.add-chapter-btn:hover {
  background: linear-gradient(90deg, #4f8cff 60%, #42b983 100%);
  box-shadow: 0 4px 16px rgba(66, 185, 131, 0.18);
}
</style>