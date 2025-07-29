<template>
  <div class="modal-bg">
    <div class="modal-card">
      <h2>Add New Subject</h2>
      <form @submit.prevent="onSave">
        <label for="subject-name">Name</label>
        <input id="subject-name" v-model="subject.name" required placeholder="Enter subject name" />
        <span v-if="submitted && !subject.name" class="error">Name is required.</span>
        <label for="subject-desc">Description</label>
        <input id="subject-desc" v-model="subject.description" required placeholder="Enter subject description" />
        <span v-if="submitted && !subject.description" class="error">Description is required.</span>
        <div class="modal-actions">
          <button type="submit" :disabled="!subject.name || !subject.description">Save</button>
          <button type="button" class="cancel-btn" @click="$emit('cancel')">Cancel</button>
        </div>
      </form>
    </div>
  </div>
</template>
<script setup>
import { reactive, ref } from 'vue';
const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({ name: '', description: '' })
  }
});
const emit = defineEmits(['save', 'cancel']);
const subject = reactive({ ...props.modelValue });
const submitted = ref(false);
function onSave() {
  submitted.value = true;
  if (!subject.name || !subject.description) return;
  emit('save', { ...subject });
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