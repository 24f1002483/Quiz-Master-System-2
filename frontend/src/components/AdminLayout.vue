<template>
  <div class="admin-layout">
    <NavBarDashboard 
      userType="admin" 
      :welcomeName="welcomeName" 
      :onLogout="logout" 
      :onSearch="search" 
    />
    <main class="admin-content">
      <router-view />
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
      :is-admin="true"
      @close="closeSearchResults"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import NavBarDashboard from './NavBarDashboard.vue';
import SearchResults from './SearchResults.vue';
import axios from 'axios';
import { logoutUser } from '../services/authService.js';

const router = useRouter();
const searchQuery = ref('');
const showSearchResults = ref(false);
const welcomeName = ref('Admin');
const searchResults = ref({
  quizzes: [],
  scores: [],
  users: [],
  subjects: [],
  chapters: [],
  questions: []
});

// Get user info on mount
onMounted(async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/auth/me', { withCredentials: true });
    if (response.data.user) {
      welcomeName.value = response.data.user.full_name || response.data.user.username || 'Admin';
      console.log('Admin user info loaded:', response.data.user);
    }
  } catch (error) {
    console.error('Error fetching user info:', error);
  }
});

const logout = async () => {
  try {
    await logoutUser();
    router.push('/login');
  } catch (error) {
    console.error('Logout error:', error);
    router.push('/login');
  }
};

const search = async () => {
  const query = prompt('Enter search term for quizzes, users, questions, scores, subjects, or chapters:');
  if (!query || !query.trim()) return;
  
  searchQuery.value = query.trim();
  const searchTerm = query.toLowerCase().trim();
  
  try {
    // Perform comprehensive search across all data types
    const [quizzesResponse, scoresResponse, usersResponse, subjectsResponse, chaptersResponse, questionsResponse] = await Promise.allSettled([
      axios.get(`http://localhost:5000/api/search/quizzes?q=${encodeURIComponent(searchTerm)}`, { withCredentials: true }),
      axios.get(`http://localhost:5000/api/search/scores?q=${encodeURIComponent(searchTerm)}`, { withCredentials: true }),
      axios.get(`http://localhost:5000/api/search/users?q=${encodeURIComponent(searchTerm)}`, { withCredentials: true }),
      axios.get(`http://localhost:5000/api/search/subjects?q=${encodeURIComponent(searchTerm)}`, { withCredentials: true }),
      axios.get(`http://localhost:5000/api/search/chapters?q=${encodeURIComponent(searchTerm)}`, { withCredentials: true }),
      axios.get(`http://localhost:5000/api/search/questions?q=${encodeURIComponent(searchTerm)}`, { withCredentials: true })
    ]);
    
    // Update search results
    searchResults.value = {
      quizzes: quizzesResponse.status === 'fulfilled' ? quizzesResponse.value.data : [],
      scores: scoresResponse.status === 'fulfilled' ? scoresResponse.value.data : [],
      users: usersResponse.status === 'fulfilled' ? usersResponse.value.data : [],
      subjects: subjectsResponse.status === 'fulfilled' ? subjectsResponse.value.data : [],
      chapters: chaptersResponse.status === 'fulfilled' ? chaptersResponse.value.data : [],
      questions: questionsResponse.status === 'fulfilled' ? questionsResponse.value.data : []
    };
    
    // Show search results modal
    showSearchResults.value = true;
    
  } catch (error) {
    console.error('Error during admin search:', error);
    alert('Search failed. Please try again.');
  }
};

const closeSearchResults = () => {
  showSearchResults.value = false;
};
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #e3f0ff 0%, #f9f9ff 100%);
}

.admin-content {
  padding: 20px;
  margin-top: 60px;
}
</style>