<template>
  <div class="available-quizzes">
    <h2>Available Quizzes</h2>
    <p>Choose a quiz below to test your knowledge!</p>
    
    <!-- Loading state -->
    <div v-if="loading" class="loading">
      <p>Loading quizzes...</p>
    </div>
    
    <!-- Error state -->
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="fetchQuizzes" class="retry-btn">Retry</button>
    </div>
    
    <!-- Quiz list -->
    <div v-else-if="quizzes.length > 0" class="quiz-list">
      <div v-for="quiz in quizzes" :key="quiz.id" class="quiz-card">
        <h3>{{ quiz.title }}</h3>
        <p>{{ quiz.description || 'No description available' }}</p>
        <div class="quiz-info">
          <span class="duration">Duration: {{ quiz.time_duration }} minutes</span>
          <span class="dates">
            <span>Start: {{ new Date(quiz.start_date).toLocaleString() }}</span><br>
            <span>End: {{ new Date(quiz.end_date).toLocaleString() }}</span>
          </span>
          <span class="status" :class="{ 'available': quiz.is_available }">
            {{ quiz.is_available ? 'Available' : 'Not Available' }}
          </span>
        </div>
        <router-link 
          :to="`/quiz/${quiz.id}`" 
          class="start-btn"
          :class="{ 'disabled': !quiz.is_available }"
          :disabled="!quiz.is_available"
        >
          {{ quiz.is_available ? 'Start Quiz' : 'Not Available' }}
        </router-link>
      </div>
    </div>
    
    <!-- Empty state -->
    <div v-else class="empty">
      <p>No quizzes available at the moment.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const quizzes = ref([])
const loading = ref(true)
const error = ref(null)

const fetchQuizzes = async () => {
  try {
    loading.value = true
    const token = localStorage.getItem('token')
    console.log('About to fetch quizzes from AvailableQuizzes...');
    const response = await axios.get('http://localhost:5000/api/quiz/quizzes', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    console.log('AvailableQuizzes response:', response.data);
    quizzes.value = response.data
  } catch (err) {
    error.value = 'Failed to load quizzes'
    console.error('Error fetching quizzes:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchQuizzes()
})
</script>

<style scoped>
.available-quizzes {
  padding: 2rem;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(44, 62, 80, 0.08);
  max-width: 800px;
  margin: 2rem auto;
}
.available-quizzes h2 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
}
.available-quizzes p {
  color: #555;
  margin-bottom: 2rem;
}
.quiz-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.5rem;
}
.quiz-card {
  background: #f8fafc;
  border-radius: 10px;
  box-shadow: 0 1px 4px rgba(44, 62, 80, 0.06);
  padding: 1.5rem 1.2rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  transition: box-shadow 0.2s;
}
.quiz-card:hover {
  box-shadow: 0 4px 16px rgba(66, 185, 131, 0.13);
}
.quiz-card h3 {
  margin: 0 0 0.5rem 0;
  color: #42b983;
  font-size: 1.3rem;
}
.quiz-card p {
  flex: 1;
  color: #444;
  margin-bottom: 1.2rem;
}
.start-btn {
  display: inline-block;
  background: linear-gradient(90deg, #42b983 60%, #4f8cff 100%);
  color: #fff;
  font-weight: 600;
  padding: 0.5rem 1.5rem;
  border-radius: 20px;
  font-size: 1rem;
  text-decoration: none;
  box-shadow: 0 1px 4px rgba(79, 140, 255, 0.13);
  transition: background 0.2s, box-shadow 0.2s;
}
.start-btn:hover {
  background: linear-gradient(90deg, #4f8cff 60%, #42b983 100%);
  box-shadow: 0 4px 12px rgba(66, 185, 131, 0.18);
}

.start-btn.disabled {
  background: #ccc;
  cursor: not-allowed;
  opacity: 0.6;
}

.start-btn.disabled:hover {
  background: #ccc;
  box-shadow: 0 1px 4px rgba(79, 140, 255, 0.13);
}

.quiz-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.duration {
  color: #666;
}

.dates {
  color: #666;
  font-size: 0.8rem;
}

.status {
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  background: #ffebee;
  color: #c62828;
}

.status.available {
  background: #e8f5e8;
  color: #2e7d32;
}

.loading, .error, .empty {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.retry-btn {
  background: #42b983;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 1rem;
}

.retry-btn:hover {
  background: #3aa876;
}
</style>
