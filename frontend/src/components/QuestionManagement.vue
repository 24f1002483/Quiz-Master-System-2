<template>
  <div class="question-management">
    <h2>Question Management</h2>
    <ul>
      <li v-for="question in questions" :key="question.id">
        <span>{{ question.title }} (Correct: {{ question.correctOption }})</span>
        <button @click="editQuestion(question)">Edit</button>
        <button @click="deleteQuestionHandler(question.id)">Delete</button>
      </li>
    </ul>
    <button @click="showAddQuestion = true">+ Question</button>
    <div v-if="showAddQuestion" class="modal">
      <div class="modal-content">
        <h3>New Question</h3>
        <input v-model="newQuestion.title" placeholder="Question Title" />
        <textarea v-model="newQuestion.statement" placeholder="Question Statement"></textarea>
        <div v-for="n in 4" :key="n">
          <input v-model="newQuestion.options[n-1]" :placeholder="'Option ' + n" />
        </div>
        <input v-model.number="newQuestion.correctOption" type="number" min="1" max="4" placeholder="Correct Option (1-4)" />
        <select v-model="newQuestion.quiz_id">
          <option disabled value="">Select Quiz</option>
          <option v-for="quiz in quizzesList" :key="quiz.id" :value="quiz.id">{{ quiz.title }}</option>
        </select>
        <button @click="addQuestion">Save</button>
        <button @click="showAddQuestion = false">Cancel</button>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
const questions = ref([]);
const showAddQuestion = ref(false);
const newQuestion = ref({ title: '', statement: '', options: ['', '', '', ''], correctOption: 1, quiz_id: '' });
const quizzesList = ref([]);
const loadQuestions = async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/questions');
    questions.value = res.data;
  } catch (e) {
    alert('Failed to load questions');
  }
};
const loadQuizzes = async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/quizzes');
    quizzesList.value = res.data;
  } catch (e) {
    alert('Failed to load quizzes');
  }
};
const addQuestion = async () => {
  if (newQuestion.value.title && newQuestion.value.quiz_id) {
    const questionData = {
      quiz_id: newQuestion.value.quiz_id,  // quiz_id is now required
      question_title: newQuestion.value.title,
      question_statement: newQuestion.value.statement || newQuestion.value.title, // Use statement if provided, otherwise use title
      option1: newQuestion.value.options[0],
      option2: newQuestion.value.options[1],
      option3: newQuestion.value.options[2],
      option4: newQuestion.value.options[3],
      correct_answer: parseInt(newQuestion.value.correctOption),
      explanation: '',
      difficulty: 3
    };
    await axios.post('http://localhost:5000/api/questions', questionData);
    newQuestion.value = { title: '', statement: '', options: ['', '', '', ''], correctOption: 1, quiz_id: '' };
    showAddQuestion.value = false;
    loadQuestions();
  } else {
    alert('Please enter all fields and select a quiz.');
  }
};
const editQuestion = (question) => {
  // Implement edit modal if needed
  alert('Edit question: ' + question.title);
};
const deleteQuestionHandler = async (id) => {
  await axios.delete(`http://localhost:5000/api/questions/${id}`);
  loadQuestions();
};
onMounted(() => {
  loadQuestions();
  loadQuizzes();
});
</script>
<style scoped>
.question-management { max-width: 600px; margin: 2rem auto; background: #fff; padding: 2rem; border-radius: 8px; }
ul { list-style: none; padding: 0; }
li { margin-bottom: 0.5rem; display: flex; align-items: center; gap: 1rem; }
button { margin-right: 0.5rem; }
.modal { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; }
.modal-content { background: #fff; padding: 2rem; border-radius: 8px; min-width: 300px; display: flex; flex-direction: column; gap: 1rem; }
</style> 