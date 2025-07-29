<template>
  <div class="quiz-taking">
    <div v-if="loading" class="loading">Loading quiz...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="quizData" class="quiz-content">
      <div class="quiz-header">
        <h2>{{ quizData.title }}</h2>
        <span>Q: {{ currentQuestionNumber }}/{{ totalQuestions }}</span>
        <span class="timer">{{ timer }}</span>
      </div>
      
      <div v-if="currentQuestion" class="question-statement">
        <h3>{{ currentQuestion.question_statement }}</h3>
        <div class="options">
          <label v-for="(option, idx) in currentQuestion.options" :key="idx" class="option">
            <input 
              type="radio" 
              :value="idx + 1" 
              v-model="selectedOption"
              :name="'question-' + currentQuestion.id"
            />
            <span>{{ option }}</span>
          </label>
        </div>
      </div>
      
      <div class="actions">
        <button @click="previousQuestion" :disabled="currentQuestionNumber <= 1">Previous</button>
        <button @click="saveAnswer">Save Answer</button>
        <button @click="nextQuestion" :disabled="currentQuestionNumber >= totalQuestions">Next</button>
        <button @click="submitQuiz" class="submit-btn">Submit Quiz</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../services/axiosConfig.js';
import sessionService from '../services/sessionService.js';
import { fetchQuizById, fetchQuizQuestions } from '../services/quizService.js';

const route = useRoute();
const router = useRouter();

const loading = ref(true);
const error = ref(null);
const quizData = ref(null);
const questions = ref([]);
const currentQuestionIndex = ref(0);
const selectedOption = ref(null);
const timer = ref('00:00:00');
const timeRemaining = ref(0); // in seconds
const attemptId = ref(null);
const timerInterval = ref(null);

const currentQuestionNumber = computed(() => currentQuestionIndex.value + 1);
const totalQuestions = computed(() => questions.value.length);
const currentQuestion = computed(() => questions.value[currentQuestionIndex.value] || null);

const formatTime = (seconds) => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

const startTimer = () => {
  if (timerInterval.value) clearInterval(timerInterval.value);
  
  timerInterval.value = setInterval(() => {
    if (timeRemaining.value > 0) {
      timeRemaining.value--;
      timer.value = formatTime(timeRemaining.value);
    } else {
      clearInterval(timerInterval.value);
      alert('Time is up! Quiz will be submitted automatically.');
      submitQuiz();
    }
  }, 1000);
};

const fetchQuizData = async () => {
  try {
    loading.value = true;
    const quizId = route.params.id;
    console.log('Starting quiz with ID:', quizId);
    
    // Pause session monitoring during quiz taking
    sessionService.pauseSessionMonitoring();
    
    // Start the quiz attempt
    const startResponse = await api.post(`/api/user/quiz/start/${quizId}`, {});
    
    console.log('Start response:', startResponse.data);
    attemptId.value = startResponse.data.attempt_id;
    console.log('Attempt ID set to:', attemptId.value);
    
    // Fetch quiz details using service
    quizData.value = await fetchQuizById(quizId);
    
    // Set timer based on quiz duration from database (time_duration is in minutes, convert to seconds)
    console.log('Quiz data:', quizData.value);
    console.log('Time duration from DB:', quizData.value.time_duration);
    
    if (!quizData.value.time_duration) {
      error.value = 'Quiz duration not found. Please contact administrator.';
      return;
    }
    
    timeRemaining.value = quizData.value.time_duration * 60; // Convert minutes to seconds
    timer.value = formatTime(timeRemaining.value);
    
    // Start the countdown timer
    startTimer();
    
    // Fetch all questions for this quiz using service
    const questionsData = await fetchQuizQuestions(quizId);
    
    questions.value = questionsData.map(q => ({
      ...q,
      options: [q.option1, q.option2, q.option3, q.option4].filter(Boolean)
    }));
    
  } catch (err) {
    console.error('Error fetching quiz data:', err);
    error.value = 'Failed to load quiz. Please try again.';
  } finally {
    loading.value = false;
  }
};

const saveAnswer = async () => {
  if (!selectedOption.value || !currentQuestion.value) return;
  
  try {
    console.log('Saving answer with attempt ID:', attemptId.value);
    await api.post('/api/user/quiz/answer', {
      attempt_id: attemptId.value,
      question_id: currentQuestion.value.id,
      selected_option: selectedOption.value
    });
  } catch (err) {
    console.error('Error saving answer:', err);
  }
};

const nextQuestion = async () => {
  if (currentQuestionIndex.value < questions.value.length - 1) {
    await saveAnswer();
    currentQuestionIndex.value++;
    selectedOption.value = null;
  }
};

const previousQuestion = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--;
    selectedOption.value = null;
  }
};

const submitQuiz = async () => {
  try {
    console.log('Submitting quiz with attempt ID:', attemptId.value);
    
    if (!attemptId.value) {
      console.error('Attempt ID is undefined!');
      alert('Error: Attempt ID is missing. Please try starting the quiz again.');
      return;
    }
    
    await saveAnswer();
    await api.post(`/api/user/quiz/complete/${attemptId.value}`, {});
    
    // Resume session monitoring after quiz completion
    sessionService.resumeSessionMonitoring();
    
    alert('Quiz submitted successfully!');
    router.push('/user/scores');
  } catch (err) {
    console.error('Error submitting quiz:', err);
    alert('Error submitting quiz. Please try again.');
  }
};

onMounted(() => {
  fetchQuizData();
});

onUnmounted(() => {
  if (timerInterval.value) {
    clearInterval(timerInterval.value);
  }
  // Resume session monitoring if user navigates away from quiz
  sessionService.resumeSessionMonitoring();
});
</script>

<style scoped>
.quiz-taking {
  max-width: 800px;
  margin: 2rem auto;
  background: #fff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #eee;
}

.quiz-header h2 {
  margin: 0;
  color: #333;
}

.timer {
  font-weight: bold;
  color: #e67e22;
  font-size: 1.2rem;
}

.question-statement {
  margin-bottom: 2rem;
}

.question-statement h3 {
  margin-bottom: 1.5rem;
  color: #333;
  font-size: 1.3rem;
}

.options {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  border: 2px solid #eee;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.option:hover {
  border-color: #42b983;
  background-color: #f8f9fa;
}

.option input[type="radio"] {
  margin: 0;
}

.option span {
  font-size: 1.1rem;
  color: #333;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 2px solid #eee;
}

.actions button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.actions button:not(:disabled) {
  background-color: #42b983;
  color: white;
}

.actions button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.actions button:hover:not(:disabled) {
  background-color: #3aa876;
}

.submit-btn {
  background-color: #e74c3c !important;
}

.submit-btn:hover:not(:disabled) {
  background-color: #c0392b !important;
}

.loading, .error {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
}

.error {
  color: #e74c3c;
}
</style> 