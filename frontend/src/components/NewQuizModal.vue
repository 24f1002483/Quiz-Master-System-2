<template>
  <div class="modal-bg">
    <div class="modal-card">
      <h2>Add New Quiz</h2>
             <form @submit.prevent="onSave">

                  <label for="quiz-title">Title</label>
         <input id="quiz-title" v-model="quiz.title" required placeholder="Enter quiz title" />
         <span v-if="submitted && !quiz.title" class="error">Title is required.</span>
         
         <label for="quiz-chapter">Chapter</label>
         <select id="quiz-chapter" v-model="quiz.chapterId" required>
           <option disabled value="">Select Chapter</option>
           <option v-for="chapter in chapters" :key="chapter.id" :value="chapter.id">
             {{ chapter.name }}
           </option>
         </select>
         <span v-if="submitted && !quiz.chapterId" class="error">Chapter is required.</span>
         
         <label for="quiz-description">Description</label>
         <textarea id="quiz-description" v-model="quiz.description" placeholder="Enter quiz description" rows="3"></textarea>
         
         <label for="quiz-start-date">Start Date & Time</label>
         <input 
           id="quiz-start-date" 
           v-model="quiz.startDate" 
           type="datetime-local" 
           required 
           :min="minDateTime"
         />
         <span v-if="submitted && !quiz.startDate" class="error">Start date is required.</span>
         
         <label for="quiz-end-date">End Date & Time</label>
         <input 
           id="quiz-end-date" 
           v-model="quiz.endDate" 
           type="datetime-local" 
           required 
           :min="quiz.startDate || minDateTime"
           placeholder="Select end date and time"
         />
         <span v-if="submitted && !quiz.endDate" class="error">End date is required.</span>
         <span v-if="submitted && quiz.startDate && quiz.endDate && quiz.startDate >= quiz.endDate" class="error">End date must be after start date.</span>
         <small class="help-text">The quiz will be available between the start and end dates. Students can only take the quiz during this time period.</small>
        <label for="quiz-duration">Duration (minutes)</label>
        <input id="quiz-duration" v-model="quiz.duration" placeholder="Enter duration in minutes" type="number" min="1" required />
        <span v-if="submitted && (!quiz.duration || isNaN(quiz.duration) || quiz.duration <= 0)" class="error">Duration must be a positive number.</span>
        <div class="modal-actions">
          <button type="submit" :disabled="!quiz.title || !quiz.chapterId || !quiz.startDate || !quiz.endDate || !quiz.duration || isNaN(quiz.duration) || quiz.duration <= 0 || (quiz.startDate && quiz.endDate && quiz.startDate >= quiz.endDate)">Save</button>
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
    default: () => ({ title: '', chapterId: '', description: '', startDate: '', endDate: '', duration: '' })
  },
  chapters: {
    type: Array,
    default: () => []
  }
});
const emit = defineEmits(['save', 'cancel']);
const quiz = reactive({ ...props.modelValue });
const submitted = ref(false);

// Get current date and time for minimum datetime input
const minDateTime = new Date().toISOString().slice(0, 16);

function onSave() {
  submitted.value = true;
  if (!quiz.title || !quiz.chapterId || !quiz.startDate || !quiz.endDate || !quiz.duration || isNaN(quiz.duration) || quiz.duration <= 0 || quiz.startDate >= quiz.endDate) return;
  
  // Convert datetime-local values to ISO strings for backend
  const quizData = {
    ...quiz,
    start_date: new Date(quiz.startDate).toISOString(),
    end_date: new Date(quiz.endDate).toISOString()
  };
  
  emit('save', quizData);
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
  min-width: 500px;
  max-width: 90vw;
  max-height: 90vh;
  width: 100%;
  text-align: center;
  overflow-y: auto;
  overflow-x: hidden;
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
  gap: 1.2rem;
  padding-bottom: 1rem;
}
label {
  text-align: left;
  color: #555;
  font-size: 1rem;
  margin-bottom: 0.2rem;
}
input, select, textarea {
  padding: 0.7rem 1rem;
  border: 1px solid #cfd8dc;
  border-radius: 8px;
  font-size: 1rem;
  transition: border 0.2s, box-shadow 0.2s;
  outline: none;
  font-family: inherit;
  resize: vertical;
}

textarea {
  min-height: 80px;
  line-height: 1.4;
}
input:focus, select:focus, textarea:focus {
  border: 1.5px solid #42b983;
  box-shadow: 0 0 0 2px #e0f7fa;
}

/* Style for datetime-local inputs */
input[type="datetime-local"] {
  cursor: pointer;
  background: #fff;
}

input[type="datetime-local"]::-webkit-calendar-picker-indicator {
  cursor: pointer;
  filter: invert(0.5);
}

input[type="datetime-local"]::-webkit-calendar-picker-indicator:hover {
  filter: invert(0.3);
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

.help-text {
  color: #666;
  font-size: 0.9em;
  margin-top: -0.5rem;
  margin-bottom: 0.5rem;
  text-align: left;
  font-style: italic;
}
</style> 