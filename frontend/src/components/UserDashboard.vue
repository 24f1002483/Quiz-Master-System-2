<template>
  <div class="user-dashboard">
    <header class="user-header">
      <nav class="main-nav">
        <router-link to="/user">Home</router-link>
        <router-link to="/user/scores">Scores</router-link>
        <router-link to="/user/summary">Summary</router-link>
        <button @click="logout" class="logout-btn">Logout</button>
      </nav>
      <div class="user-search">
        <input type="text" placeholder="Search quizzes, scores, subjects, chapters, questions..." v-model="searchQuery">
        <button @click="search">Search</button>
        <button v-if="isSearching" @click="clearSearch" class="clear-btn">Clear</button>
      </div>
      <div class="welcome-message">Welcome User</div>
    </header>
    <main class="dashboard-content">
      <section class="upcoming-quizzes">
        <h2>Available Quizzes</h2>
        <div v-if="loading" class="loading">Loading quizzes...</div>
        <div v-else-if="quizzes.length > 0">
          <table>
            <thead>
              <tr><th>ID</th><th>Quiz</th><th>Start Date</th><th>End Date</th><th>Duration</th><th>Status</th><th>Action</th></tr>
            </thead>
            <tbody>
              <tr v-for="quiz in quizzes" :key="quiz.id">
                <td>{{ quiz.id }}</td>
                <td>{{ quiz.title }}</td>
                <td>{{ new Date(quiz.start_date).toLocaleString() }}</td>
                <td>{{ new Date(quiz.end_date).toLocaleString() }}</td>
                <td>{{ quiz.time_duration }} minutes</td>
                <td>
                  <span :class="{ 'available': quiz.is_available, 'unavailable': !quiz.is_available }">
                    {{ quiz.is_available ? 'Available' : 'Not Available' }}
                  </span>
                </td>
                <td>
                  <button 
                    @click="startQuiz(quiz)" 
                    :disabled="!quiz.is_available"
                    :class="{ 'disabled': !quiz.is_available }"
                  >
                    {{ quiz.is_available ? 'Start Quiz' : 'Not Available' }}
                  </button>
                  <button 
                    v-if="quiz.is_available"
                    @click="viewAttemptHistory(quiz.id)"
                    class="history-btn"
                  >
                    History
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="empty">No quizzes available at the moment.</div>
      </section>
      <section class="scores">
        <h2>Recent Scores</h2>
        <div v-if="loading" class="loading">Loading scores...</div>
        <div v-else-if="scores.length > 0">
          <table>
            <thead>
              <tr><th>Quiz</th><th>Date</th><th>Score</th><th>Percentage</th></tr>
            </thead>
            <tbody>
              <tr v-for="score in scores" :key="score.id">
                <td>{{ score.quiz_title || 'Quiz' }}</td>
                <td>{{ new Date(score.timestamp).toLocaleDateString() }}</td>
                <td>{{ score.score }}/{{ score.total_questions }}</td>
                <td>{{ score.percentage }}%</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="empty">No scores available yet.</div>
      </section>
      <section class="summary-charts">
        <h2>Summary Charts</h2>
        <div class="charts">
          <div class="bar-chart">[Bar Chart Placeholder]</div>
          <div class="pie-chart">[Pie Chart Placeholder]</div>
        </div>
      </section>
    </main>
    
    <!-- Search Results Component -->
    <SearchResults
      :is-visible="showSearchResults"
      :search-query="searchQuery"
      :quizzes="searchResults.quizzes"
      :scores="searchResults.scores"
      :users="searchResults.users"
      :subjects="searchResults.subjects"
      :chapters="searchResults.chapters"
      :questions="searchResults.questions"
      :is-admin="false"
      @close="closeSearchResults"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { logoutUser } from '../services/authService.js';
import { useRouter } from 'vue-router';
import axios from 'axios';
import SearchResults from './SearchResults.vue';

const router = useRouter();
const searchQuery = ref('');
const quizzes = ref([]);
const scores = ref([]);
const loading = ref(true);
const originalQuizzes = ref([]);
const originalScores = ref([]);
const isSearching = ref(false);
const showSearchResults = ref(false);
const searchResults = ref({
  quizzes: [],
  scores: [],
  users: [],
  subjects: [],
  chapters: [],
  questions: []
});

const fetchUserData = async () => {
  try {
    loading.value = true;
    
    console.log('About to fetch quizzes...');
    // Fetch available quizzes - use cookie-based authentication
    const quizzesResponse = await axios.get('http://localhost:5000/api/user/quiz/available', {
      withCredentials: true
    });
    console.log('Quizzes response:', quizzesResponse.data);
    quizzes.value = quizzesResponse.data;
    originalQuizzes.value = quizzesResponse.data; // Store original data
    
    // Fetch user scores - use cookie-based authentication
    const scoresResponse = await axios.get('http://localhost:5000/api/user/quizzes/scores', {
      withCredentials: true
    });
    scores.value = scoresResponse.data;
    originalScores.value = scoresResponse.data; // Store original data
  } catch (error) {
    console.error('Error fetching user data:', error);
  } finally {
    loading.value = false;
  }
};

const logout = async () => {
  await logoutUser();
  router.push('/');
};

const search = async () => { 
  console.log('Searching for:', searchQuery.value);
  
  if (!searchQuery.value.trim()) {
    // If search is empty, show all data
    quizzes.value = originalQuizzes.value;
    scores.value = originalScores.value;
    isSearching.value = false;
    return;
  }
  
  isSearching.value = true;
  const query = searchQuery.value.toLowerCase().trim();
  
  try {
    // Search through quizzes
    const filteredQuizzes = originalQuizzes.value.filter(quiz => 
      quiz.title.toLowerCase().includes(query) ||
      quiz.id.toString().includes(query)
    );
    
    // Search through scores
    const filteredScores = originalScores.value.filter(score => 
      (score.quiz_title && score.quiz_title.toLowerCase().includes(query)) ||
      score.id.toString().includes(query) ||
      score.score.toString().includes(query) ||
      score.total_questions.toString().includes(query)
    );
    
    // Fetch additional search data (subjects, chapters, questions)
    const [subjectsResponse, chaptersResponse, questionsResponse] = await Promise.allSettled([
      axios.get(`http://localhost:5000/api/search/subjects?q=${encodeURIComponent(query)}`, { withCredentials: true }),
      axios.get(`http://localhost:5000/api/search/chapters?q=${encodeURIComponent(query)}`, { withCredentials: true }),
      axios.get(`http://localhost:5000/api/search/questions?q=${encodeURIComponent(query)}`, { withCredentials: true })
    ]);
    
    // Update search results
    searchResults.value = {
      quizzes: filteredQuizzes,
      scores: filteredScores,
      users: [], // Users not available for regular users
      subjects: subjectsResponse.status === 'fulfilled' ? subjectsResponse.value.data : [],
      chapters: chaptersResponse.status === 'fulfilled' ? chaptersResponse.value.data : [],
      questions: questionsResponse.status === 'fulfilled' ? questionsResponse.value.data : []
    };
    
    // Show search results modal
    showSearchResults.value = true;
    
  } catch (error) {
    console.error('Error during search:', error);
    alert('Search failed. Please try again.');
  }
};

const closeSearchResults = () => {
  showSearchResults.value = false;
};

const clearSearch = () => {
  searchQuery.value = '';
  quizzes.value = originalQuizzes.value;
  scores.value = originalScores.value;
  isSearching.value = false;
  showSearchResults.value = false;
};

const startQuiz = (quiz) => { 
  router.push(`/quiz/${quiz.id}`);
};

const viewAttemptHistory = async (quizId) => {
  try {
    const response = await axios.get(`http://localhost:5000/api/user/quiz/${quizId}/attempts`, {
      withCredentials: true
    });
    
    if (response.data.length > 0) {
      const historyText = response.data.map(attempt => 
        `Attempt ${attempt.attempt_id}: ${attempt.score}/${attempt.total_questions} (${attempt.percentage}%) - ${attempt.status}`
      ).join('\n');
      alert(`Quiz Attempt History:\n\n${historyText}`);
    } else {
      alert('No previous attempts for this quiz.');
    }
  } catch (error) {
    console.error('Error fetching attempt history:', error);
    alert('Failed to load attempt history.');
  }
};

onMounted(() => {
  fetchUserData();
});
</script>
<style scoped>
.user-dashboard { min-height: 100vh; background: #f5f5f5; }
.user-header { display: flex; justify-content: space-between; align-items: center; padding: 1rem 2rem; background-color: #2c3e50; color: white; }
.main-nav { display: flex; gap: 1.5rem; }
.main-nav a { color: white; text-decoration: none; font-weight: 500; }
.main-nav a.router-link-exact-active { color: #42b983; }
.logout-btn { background-color: #e74c3c; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; margin-left: 1rem; }
.user-search { display: flex; gap: 0.5rem; }
.user-search input { padding: 0.5rem; border-radius: 4px; border: 1px solid #ddd; }
.user-search button { padding: 0.5rem 1rem; border-radius: 4px; border: 1px solid #ddd; background: #007bff; color: white; cursor: pointer; }
.user-search .clear-btn { background: #6c757d; }
.user-search button:hover { opacity: 0.8; }
.welcome-message { font-weight: bold; }
.dashboard-content { display: flex; flex-direction: column; gap: 2rem; padding: 2rem; }
section { background: #fff; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; }
table { width: 100%; border-collapse: collapse; margin-bottom: 1rem; }
th, td { border: 1px solid #ddd; padding: 0.5rem; text-align: left; }
.charts { display: flex; gap: 2rem; }
.bar-chart, .pie-chart { flex: 1; background: #f0f0f0; border-radius: 8px; padding: 1rem; text-align: center; }

.loading, .empty {
  text-align: center;
  padding: 2rem;
  color: #666;
  font-style: italic;
}

.available {
  color: #2e7d32;
  font-weight: 500;
}

.unavailable {
  color: #c62828;
  font-weight: 500;
}

button.disabled {
  background: #ccc;
  cursor: not-allowed;
  opacity: 0.6;
}

button.disabled:hover {
  background: #ccc;
}

.history-btn {
  background: #17a2b8;
  color: white;
  border: none;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 0.5rem;
  font-size: 0.8rem;
}

.history-btn:hover {
  background: #138496;
}
</style>