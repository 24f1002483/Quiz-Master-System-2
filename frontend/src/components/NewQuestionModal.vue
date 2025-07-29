<template>
  <div class="modal-bg">
    <div class="modal-card">
      <h2>Add New Question</h2>
      <form @submit.prevent="onSave">
        <label for="question-chapter">Chapter</label>
        <select id="question-chapter" v-model="question.chapterId" required>
          <option disabled value="">Select Chapter</option>
          <option v-for="chapter in chapters" :key="chapter.id" :value="chapter.id">
            {{ chapter.name }}
          </option>
        </select>
        <span v-if="submitted && !question.chapterId" class="error">Chapter is required.</span>
        <label for="question-title">Question Title</label>
        <input id="question-title" v-model="question.title" required placeholder="Enter question title" />
        <span v-if="submitted && !question.title" class="error">Question title is required.</span>
        <label for="question-statement">Question Statement</label>
        <textarea id="question-statement" v-model="question.statement" required placeholder="Enter question statement"></textarea>
        <span v-if="submitted && !question.statement" class="error">Statement is required.</span>
        <div class="options-section">
          <label>Options</label>
          <input v-model="question.options[0]" placeholder="Option 1" required />
          <input v-model="question.options[1]" placeholder="Option 2" required />
          <input v-model="question.options[2]" placeholder="Option 3" required />
          <input v-model="question.options[3]" placeholder="Option 4" required />
          <span v-if="submitted && question.options.some(opt => !opt)" class="error">All options are required.</span>
        </div>
        <label for="question-correct">Correct Option</label>
        <input id="question-correct" v-model.number="question.correctOption" placeholder="Enter correct option (1-4)" type="number" min="1" max="4" required />
        <span v-if="submitted && (!question.correctOption || isNaN(question.correctOption) || question.correctOption < 1 || question.correctOption > 4)" class="error">Correct option must be 1-4.</span>
        <div class="modal-actions">
          <button type="submit" :disabled="!isValid">Save and Next</button>
          <button type="button" class="cancel-btn" @click="$emit('cancel')">Close</button>
        </div>
      </form>
    </div>
  </div>
</template>
<script setup>
import { reactive, ref, computed } from 'vue';
const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({ chapterId: '', title: '', statement: '', options: ['', '', '', ''], correctOption: 1 })
  },
  chapters: {
    type: Array,
    default: () => []
  }
});
const emit = defineEmits(['save', 'cancel']);
const question = reactive({ ...props.modelValue });
if (!question.options) question.options = ['', '', '', ''];
const submitted = ref(false);
const isValid = computed(() =>
  question.chapterId &&
  question.title &&
  question.statement &&
  question.options.every(opt => !!opt) &&
  question.correctOption &&
  !isNaN(question.correctOption) &&
  question.correctOption >= 1 &&
  question.correctOption <= 4
);
function onSave() {
  submitted.value = true;
  if (!isValid.value) return;
  emit('save', { ...question });
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
.options-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
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