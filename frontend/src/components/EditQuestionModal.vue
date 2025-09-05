<template>
  <div class="modal-bg">
    <div class="modal-card">
      <h2>Edit Question</h2>
      <form @submit.prevent="onSave">
        <label for="question-title">Question Title</label>
        <input 
          id="question-title" 
          v-model="question.title" 
          required 
          placeholder="Enter question title" 
        />
        <span v-if="submitted && !question.title" class="error">Question title is required.</span>

        <label for="question-statement">Question Statement</label>
        <textarea 
          id="question-statement" 
          v-model="question.statement" 
          required 
          placeholder="Enter question statement"
        ></textarea>
        <span v-if="submitted && !question.statement" class="error">Statement is required.</span>

        <div class="options-section">
          <label>Options</label>
          <div class="option-input" v-for="(option, index) in question.options" :key="index">
            <input 
              v-model="question.options[index]" 
              :placeholder="`Option ${index + 1}`" 
              required 
            />
            <span 
              v-if="question.correctOption === index + 1" 
              class="correct-indicator"
              title="Correct Answer"
            >
              ✓
            </span>
          </div>
          <span v-if="submitted && question.options.some(opt => !opt)" class="error">
            All options are required.
          </span>
        </div>

        <label for="question-correct">Correct Option</label>
        <select id="question-correct" v-model.number="question.correctOption" required>
          <option disabled value="">Select correct option</option>
          <option v-for="n in 4" :key="n" :value="n">
            Option {{ n }}: {{ question.options[n-1] || 'Not set' }}
          </option>
        </select>
        <span v-if="submitted && (!question.correctOption || question.correctOption < 1 || question.correctOption > 4)" class="error">
          Please select the correct option.
        </span>

        <div class="additional-fields">
          <label for="question-explanation">Explanation (Optional)</label>
          <textarea 
            id="question-explanation" 
            v-model="question.explanation" 
            placeholder="Provide an explanation for the correct answer"
            rows="3"
          ></textarea>

          <label for="question-difficulty">Difficulty Level</label>
          <select id="question-difficulty" v-model.number="question.difficulty">
            <option value="1">Easy</option>
            <option value="2">Medium</option>
            <option value="3">Hard</option>
            <option value="4">Expert</option>
          </select>
        </div>

        <div class="modal-actions">
          <button type="submit" :disabled="!isValid" class="save-btn">
            Update Question
          </button>
          <button type="button" class="cancel-btn" @click="$emit('cancel')">
            Cancel
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed, watch } from 'vue';

const props = defineProps({
  question: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['save', 'cancel']);

// Create a reactive copy of the question for editing
const question = reactive({
  id: props.question.id,
  title: props.question.question_title || '',
  statement: props.question.question_statement || '',
  options: [
    props.question.option1 || '',
    props.question.option2 || '',
    props.question.option3 || '',
    props.question.option4 || ''
  ],
  correctOption: props.question.correct_answer || 1,
  explanation: props.question.explanation || '',
  difficulty: props.question.difficulty || 3
});

const submitted = ref(false);

const isValid = computed(() =>
  question.title &&
  question.statement &&
  question.options.every(opt => !!opt.trim()) &&
  question.correctOption &&
  question.correctOption >= 1 &&
  question.correctOption <= 4
);

// Watch for changes in options to update the correct option display
watch(() => question.options, () => {
  // Force reactivity update for the select options
}, { deep: true });

function onSave() {
  submitted.value = true;
  if (!isValid.value) return;

  // Transform the data back to the API format
  const questionData = {
    question_title: question.title,
    question_statement: question.statement,
    option1: question.options[0],
    option2: question.options[1],
    option3: question.options[2],
    option4: question.options[3],
    correct_answer: question.correctOption,
    explanation: question.explanation,
    difficulty: question.difficulty
  };

  emit('save', { id: question.id, ...questionData });
}
</script>

<style scoped>
.modal-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-card {
  background: #fff;
  padding: 2.5rem;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(44, 62, 80, 0.15);
  min-width: 500px;
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
  text-align: center;
}

.modal-card h2 {
  margin-bottom: 2rem;
  color: #2c3e50;
  font-size: 1.6rem;
  font-weight: 700;
}

form {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  text-align: left;
}

label {
  color: #2c3e50;
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.3rem;
}

input, textarea, select {
  padding: 0.8rem 1rem;
  border: 2px solid #e0e7ff;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.2s ease;
  outline: none;
  font-family: inherit;
}

input:focus, textarea:focus, select:focus {
  border-color: #42b983;
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.1);
}

textarea {
  resize: vertical;
  min-height: 80px;
}

.options-section {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.option-input {
  position: relative;
  display: flex;
  align-items: center;
}

.option-input input {
  flex: 1;
  padding-right: 3rem;
}

.correct-indicator {
  position: absolute;
  right: 1rem;
  color: #42b983;
  font-weight: bold;
  font-size: 1.2rem;
  background: #e8f5e8;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.additional-fields {
  background: #f8f9ff;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #e0e7ff;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e0e7ff;
}

.save-btn {
  background: linear-gradient(90deg, #42b983 60%, #4f8cff 100%);
  color: #fff;
  font-weight: 600;
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(79, 140, 255, 0.13);
  transition: all 0.2s ease;
}

.save-btn:hover:not(:disabled) {
  background: linear-gradient(90deg, #4f8cff 60%, #42b983 100%);
  box-shadow: 0 4px 16px rgba(66, 185, 131, 0.18);
  transform: translateY(-1px);
}

.save-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.cancel-btn {
  background: #f5f5f5;
  color: #666;
  font-weight: 500;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 0.8rem 1.5rem;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-btn:hover {
  background: #e0e0e0;
  border-color: #ccc;
  transform: translateY(-1px);
}

.error {
  color: #e74c3c;
  font-size: 0.9rem;
  margin-top: 0.3rem;
  font-weight: 500;
}

/* Responsive design */
@media (max-width: 768px) {
  .modal-card {
    min-width: 90vw;
    padding: 1.5rem;
  }
  
  .modal-actions {
    flex-direction: column;
  }
  
  .save-btn, .cancel-btn {
    width: 100%;
  }
}
</style>