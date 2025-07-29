<template>
  <div class="modal-bg">
    <div class="modal-card">
      <h2>Edit Chapter</h2>
      <form @submit.prevent="onSave">
        <label for="chapter-name">Name</label>
        <input id="chapter-name" v-model="chapter.name" required placeholder="Enter chapter name" />
        <span v-if="submitted && !chapter.name" class="error">Name is required.</span>
        <label for="chapter-desc">Description</label>
        <textarea id="chapter-desc" v-model="chapter.description" required placeholder="Enter chapter description"></textarea>
        <span v-if="submitted && !chapter.description" class="error">Description is required.</span>
        <label for="chapter-seq">Sequence</label>
        <input id="chapter-seq" v-model.number="chapter.sequence" type="number" placeholder="Enter sequence number" min="0" />
        <span v-if="submitted && (chapter.sequence === '' || chapter.sequence === null || isNaN(chapter.sequence))" class="error">Sequence must be a number.</span>
        <div class="modal-actions">
          <button type="submit" :disabled="!chapter.name || !chapter.description || chapter.sequence === '' || chapter.sequence === null || isNaN(chapter.sequence)">Save</button>
          <button type="button" class="cancel-btn" @click="$emit('cancel')">Cancel</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';

const props = defineProps({
  modelValue: { type: Object, default: () => ({ name: '', description: '', sequence: 0 }) }
});

const emit = defineEmits(['save', 'cancel']);

const chapter = reactive({ ...props.modelValue });
const submitted = ref(false);

function onSave() {
  submitted.value = true;
  if (!chapter.name || !chapter.description || chapter.sequence === '' || chapter.sequence === null || isNaN(chapter.sequence)) return;
  emit('save', { ...chapter });
}
</script>

<style scoped>
.modal-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0,0,0,0.18);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-card {
  background: #fff;
  padding: 2.5rem 2.5rem 2rem 2.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(44, 62, 80, 0.10);
  min-width: 340px;
  max-width: 95vw;
  width: 100%;
  text-align: center;
}
.modal-card h2 {
  margin-bottom: 1.5rem;
  color: #2c3e50;
  font-size: 1.4rem;
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
input, textarea {
  padding: 0.7rem 1rem;
  border: 1px solid #cfd8dc;
  border-radius: 8px;
  font-size: 1rem;
  transition: border 0.2s, box-shadow 0.2s;
  outline: none;
  font-family: inherit;
}
input:focus, textarea:focus {
  border: 1.5px solid #42b983;
  box-shadow: 0 0 0 2px #e0f7fa;
}
textarea {
  height: 100px;
  resize: vertical;
}
button[type="submit"] {
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
button[type="submit"]:hover {
  background: linear-gradient(90deg, #4f8cff 60%, #42b983 100%);
  box-shadow: 0 4px 16px rgba(66, 185, 131, 0.18);
}
.cancel-btn {
  background: #e0e0e0;
  color: #333;
  font-weight: 500;
  border: none;
  border-radius: 8px;
  padding: 0.8rem 0;
  font-size: 1.1rem;
  margin-top: 0.5rem;
  margin-left: 0.5rem;
  cursor: pointer;
  transition: background 0.2s;
}
.cancel-btn:hover {
  background: #bdbdbd;
}
.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1rem;
}
.error {
  color: #d00;
  font-size: 0.95em;
  margin-bottom: 0.5em;
  text-align: left;
  margin-left: 2px;
}
</style> 