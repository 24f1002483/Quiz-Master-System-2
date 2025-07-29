<template>
  <div class="chapter-card">
    <div><strong>{{ chapter.name }}</strong></div>
    <div>{{ chapter.description }}</div>
    <div class="card-actions">
      <button @click="$emit('edit', chapter)" class="edit-btn">Edit</button>
      <button @click="$emit('delete', chapter.id)" class="delete-btn">Delete</button>
    </div>
  </div>
</template>
<script setup>
const props = defineProps({
  chapter: {
    type: Object,
    required: true
  }
});
</script>
<style scoped>
.chapter-card { border: 1px solid #ddd; border-radius: 4px; padding: 0.5rem; margin-bottom: 0.5rem; display: flex; flex-direction: column; gap: 0.25rem; background: #fff; }
.card-actions { display: flex; gap: 0.5rem; margin-top: 0.5rem; }
.edit-btn, .delete-btn { padding: 0.5rem 1rem; border-radius: 4px; border: none; cursor: pointer; }
.edit-btn { background-color: #3498db; color: white; }
.delete-btn { background-color: #c0392b; color: white; }
</style> 