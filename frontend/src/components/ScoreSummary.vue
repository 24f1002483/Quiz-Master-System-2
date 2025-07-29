<template>
  <div class="score-summary">
    <header class="score-header">
      <nav class="main-nav">
        <router-link to="/user">Home</router-link>
        <router-link to="/user/scores">Scores</router-link>
        <router-link to="/user/summary">Summary</router-link>
        <button @click="logout" class="logout-btn">Logout</button>
      </nav>
      <div class="user-search">
        <input type="text" placeholder="Search scores, subjects, chapters, questions..." v-model="searchQuery">
        <button @click="search">Search</button>
        <button v-if="isSearching" @click="clearSearch" class="clear-btn">Clear</button>
      </div>
      <div class="welcome-message">Welcome User</div>
    </header>
    
    <div class="quiz-scores-container">
      <h2>Quiz Scores</h2>
      <div v-if="loading" class="loading">Loading scores...</div>
      <div v-else-if="scores.length > 0">
        <table class="scores-table">
          <thead>
            <tr>
              <th>No.of Questions</th>
              <th>Date</th>
              <th>Score</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="score in scores" :key="score.id">
              <td>{{ score.total_questions }}</td>
              <td>{{ formatDate(score.date || score.timestamp) }}</td>
              <td>{{ score.score }}/{{ score.total_questions }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="empty">No quiz scores available yet.</div>
    </div>
    
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
const scores = ref([]);
const loading = ref(true);
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

const fetchScores = async () => {
  try {
    loading.value = true;
    const response = await axios.get('http://localhost:5000/api/user/quizzes/scores', {
      withCredentials: true
    });
    scores.value = response.data;
    originalScores.value = response.data; // Store original data
  } catch (error) {
    console.error('Error fetching scores:', error);
  } finally {
    loading.value = false;
  }
};

const formatDate = (dateString) => {
  if (!dateString) return 'xx/xx/yyyy';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-GB'); // Format as dd/mm/yyyy
};

const logout = async () => {
  await logoutUser();
  router.push('/');
};

const search = async () => {
  console.log('Searching for:', searchQuery.value);
  
  if (!searchQuery.value.trim()) {
    // If search is empty, show all data
    scores.value = originalScores.value;
    isSearching.value = false;
    return;
  }
  
  isSearching.value = true;
  const query = searchQuery.value.toLowerCase().trim();
  
  try {
    // Search through scores
    const filteredScores = originalScores.value.filter(score => 
      score.id.toString().includes(query) ||
      score.total_questions.toString().includes(query) ||
      score.score.toString().includes(query) ||
      (score.quiz_title && score.quiz_title.toLowerCase().includes(query))
    );
    
    // Fetch additional search data (subjects, chapters, questions)
    const [subjectsResponse, chaptersResponse, questionsResponse] = await Promise.allSettled([
      axios.get(`http://localhost:5000/api/search/subjects?q=${encodeURIComponent(query)}`, { withCredentials: true }),
      axios.get(`http://localhost:5000/api/search/chapters?q=${encodeURIComponent(query)}`, { withCredentials: true }),
      axios.get(`http://localhost:5000/api/search/questions?q=${encodeURIComponent(query)}`, { withCredentials: true })
    ]);
    
    // Update search results
    searchResults.value = {
      quizzes: [], // No quizzes in score summary
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
  scores.value = originalScores.value;
  isSearching.value = false;
  showSearchResults.value = false;
};

onMounted(() => {
  fetchScores();
});
</script>

<style scoped>
.score-summary {
  min-height: 100vh;
  background: #f5f5f5;
}

.score-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #87CEEB;
  border: 2px solid #FFA500;
  color: white;
}

.main-nav {
  display: flex;
  gap: 1.5rem;
}

.main-nav a {
  color: white;
  text-decoration: none;
  font-weight: 500;
}

.main-nav a.router-link-exact-active {
  color: #42b983;
}

.logout-btn {
  background-color: #e74c3c;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 1rem;
}

.user-search {
  display: flex;
  gap: 0.5rem;
}

.user-search input {
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.user-search button {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  border: 1px solid #ddd;
  background: #007bff;
  color: white;
  cursor: pointer;
}

.user-search .clear-btn {
  background: #6c757d;
}

.user-search button:hover {
  opacity: 0.8;
}

.welcome-message {
  font-weight: bold;
}

.quiz-scores-container {
  max-width: 800px;
  margin: 2rem auto;
  background: #fff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.quiz-scores-container h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #333;
}

.scores-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.scores-table th,
.scores-table td {
  border: 1px solid #ddd;
  padding: 0.75rem;
  text-align: left;
}

.scores-table th {
  background-color: #f8f9fa;
  font-weight: bold;
  color: #333;
}

.scores-table tr:nth-child(even) {
  background-color: #f8f9fa;
}

.scores-table tr:hover {
  background-color: #e9ecef;
}

.loading, .empty {
  text-align: center;
  padding: 2rem;
  color: #666;
  font-style: italic;
}
</style>