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
      <!-- User Performance Overview -->
      <section class="performance-overview">
        <h2>Your Performance Overview</h2>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">Target</div>
            <div class="stat-content">
              <div class="stat-number">{{ userStats.totalQuizzesTaken }}</div>
              <div class="stat-label">Quizzes Taken</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">Chart</div>
            <div class="stat-content">
              <div class="stat-number">{{ userStats.averageScore }}%</div>
              <div class="stat-label">Average Score</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">Trophy</div>
            <div class="stat-content">
              <div class="stat-number">{{ userStats.bestScore }}%</div>
              <div class="stat-label">Best Score</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">Books</div>
            <div class="stat-content">
              <div class="stat-number">{{ userStats.subjectsCovered }}</div>
              <div class="stat-label">Subjects Covered</div>
            </div>
          </div>
        </div>
      </section>

      <!-- Charts Section -->
      <section class="charts-section">
        <h2>📈 Performance Charts</h2>
        <div class="charts-grid">
          <!-- Score Progress Chart -->
          <div class="chart-card">
            <h3>📊 Score Progress Over Time</h3>
            <div class="chart-container">
              <canvas ref="scoreProgressChart" width="400" height="200"></canvas>
            </div>
          </div>

          <!-- Subject Performance Chart -->
          <div class="chart-card">
            <h3>📚 Performance by Subject</h3>
            <div class="chart-container">
              <canvas ref="subjectPerformanceChart" width="400" height="200"></canvas>
            </div>
          </div>

          <!-- Quiz Attempts Distribution -->
          <div class="chart-card">
            <h3>🎯 Quiz Attempts Distribution</h3>
            <div class="chart-container">
              <canvas ref="attemptsDistributionChart" width="400" height="200"></canvas>
            </div>
          </div>

          <!-- Score Range Analysis -->
          <div class="chart-card">
            <h3>📊 Score Range Analysis</h3>
            <div class="chart-container">
              <canvas ref="scoreRangeChart" width="400" height="200"></canvas>
            </div>
          </div>
        </div>
      </section>

      <!-- Recent Activity -->
      <section class="recent-activity">
        <h2>🕒 Recent Activity</h2>
        <div class="activity-timeline">
          <div v-for="activity in recentActivity" :key="activity.id" class="activity-item">
            <div class="activity-icon">{{ activity.icon }}</div>
            <div class="activity-content">
              <div class="activity-title">{{ activity.title }}</div>
              <div class="activity-time">{{ formatTime(activity.timestamp) }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- Available Quizzes -->
      <section class="upcoming-quizzes">
        <h2>📝 Available Quizzes</h2>
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
                <td>{{ formatDate(quiz.start_date) }}</td>
                <td>{{ formatDate(quiz.end_date) }}</td>
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

      <!-- Recent Scores -->
      <section class="scores">
        <h2>📋 Recent Scores</h2>
        <div v-if="loading" class="loading">Loading scores...</div>
        <div v-else-if="scores.length > 0">
          <table>
            <thead>
              <tr><th>Quiz</th><th>Date</th><th>Score</th><th>Percentage</th><th>Performance</th></tr>
            </thead>
            <tbody>
              <tr v-for="score in scores" :key="score.id">
                <td>{{ score.quiz_title || 'Quiz' }}</td>
                <td>{{ formatDate(score.timestamp) }}</td>
                <td>{{ score.score }}/{{ score.total_questions }}</td>
                <td>{{ score.percentage }}%</td>
                <td>
                  <span :class="getPerformanceClass(score.percentage)">
                    {{ getPerformanceLabel(score.percentage) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="empty">No scores available yet.</div>
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
import { ref, onMounted, nextTick } from 'vue';
import { logoutUser } from '../services/authService.js';
import { useRouter } from 'vue-router';
import axios from 'axios';
import SearchResults from './SearchResults.vue';
import Chart from 'chart.js/auto';
import { formatDateTime, formatRelativeTime } from '../utils/dateUtils.js';

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

// Chart references
const scoreProgressChart = ref(null);
const subjectPerformanceChart = ref(null);
const attemptsDistributionChart = ref(null);
const scoreRangeChart = ref(null);

// User statistics
const userStats = ref({
  totalQuizzesTaken: 0,
  averageScore: 0,
  bestScore: 0,
  subjectsCovered: 0
});

// Recent activity
const recentActivity = ref([]);

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

    // Calculate user statistics
    calculateUserStats();
    
    // Generate recent activity
    generateRecentActivity();
    
    // Initialize charts after data is loaded
    await nextTick();
    initializeCharts();
    
  } catch (error) {
    console.error('Error fetching user data:', error);
  } finally {
    loading.value = false;
  }
};

const calculateUserStats = () => {
  const scoreData = scores.value;
  
  if (scoreData.length === 0) {
    userStats.value = {
      totalQuizzesTaken: 0,
      averageScore: 0,
      bestScore: 0,
      subjectsCovered: 0
    };
    return;
  }

  const totalQuizzes = scoreData.length;
  const totalScore = scoreData.reduce((sum, score) => sum + score.percentage, 0);
  const averageScore = Math.round(totalScore / totalQuizzes);
  const bestScore = Math.max(...scoreData.map(score => score.percentage));
  
  // Count unique subjects (assuming quiz_title contains subject info)
  const subjects = new Set(scoreData.map(score => {
    const title = score.quiz_title || '';
    return title.split(' - ')[0] || 'Unknown';
  }));

  userStats.value = {
    totalQuizzesTaken: totalQuizzes,
    averageScore: averageScore,
    bestScore: bestScore,
    subjectsCovered: subjects.size
  };
};

const generateRecentActivity = () => {
  const activities = [];
  
  // Add recent quiz attempts
  scores.value.slice(0, 5).forEach(score => {
    const timestamp = score.timestamp ? new Date(score.timestamp) : new Date();
    activities.push({
      id: `score-${score.id}`,
      icon: '📝',
      title: `Completed ${score.quiz_title || 'Quiz'} with ${score.percentage}%`,
      timestamp: isNaN(timestamp.getTime()) ? new Date() : timestamp
    });
  });

  // Sort by timestamp (most recent first)
  activities.sort((a, b) => b.timestamp - a.timestamp);
  
  recentActivity.value = activities.slice(0, 10);
};

const initializeCharts = () => {
  // Score Progress Chart
  if (scoreProgressChart.value && scores.value.length > 0) {
    const ctx = scoreProgressChart.value.getContext('2d');
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: scores.value.map((_, index) => `Quiz ${index + 1}`),
        datasets: [{
          label: 'Score %',
          data: scores.value.map(score => score.percentage),
          borderColor: '#42b983',
          backgroundColor: 'rgba(66, 185, 131, 0.1)',
          tension: 0.4,
          fill: true
        }]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Your Score Progress'
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 100
          }
        }
      }
    });
  }

  // Subject Performance Chart
  if (subjectPerformanceChart.value && scores.value.length > 0) {
    const subjectData = {};
    scores.value.forEach(score => {
      const subject = score.quiz_title?.split(' - ')[0] || 'Unknown';
      if (!subjectData[subject]) {
        subjectData[subject] = { total: 0, count: 0 };
      }
      subjectData[subject].total += score.percentage;
      subjectData[subject].count += 1;
    });

    const subjects = Object.keys(subjectData);
    const averages = subjects.map(subject => 
      Math.round(subjectData[subject].total / subjectData[subject].count)
    );

    const ctx = subjectPerformanceChart.value.getContext('2d');
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: subjects,
        datasets: [{
          label: 'Average Score %',
          data: averages,
          backgroundColor: [
            '#FF6384',
            '#36A2EB',
            '#FFCE56',
            '#4BC0C0',
            '#9966FF'
          ]
        }]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Performance by Subject'
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 100
          }
        }
      }
    });
  }

  // Attempts Distribution Chart
  if (attemptsDistributionChart.value && scores.value.length > 0) {
    const scoreRanges = {
      '90-100%': 0,
      '80-89%': 0,
      '70-79%': 0,
      '60-69%': 0,
      '50-59%': 0,
      'Below 50%': 0
    };

    scores.value.forEach(score => {
      if (score.percentage >= 90) scoreRanges['90-100%']++;
      else if (score.percentage >= 80) scoreRanges['80-89%']++;
      else if (score.percentage >= 70) scoreRanges['70-79%']++;
      else if (score.percentage >= 60) scoreRanges['60-69%']++;
      else if (score.percentage >= 50) scoreRanges['50-59%']++;
      else scoreRanges['Below 50%']++;
    });

    const ctx = attemptsDistributionChart.value.getContext('2d');
    new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: Object.keys(scoreRanges),
        datasets: [{
          data: Object.values(scoreRanges),
          backgroundColor: [
            '#4CAF50',
            '#8BC34A',
            '#FFC107',
            '#FF9800',
            '#F44336',
            '#9C27B0'
          ]
        }]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Score Distribution'
          }
        }
      }
    });
  }

  // Score Range Analysis Chart
  if (scoreRangeChart.value && scores.value.length > 0) {
    const recentScores = scores.value.slice(-10); // Last 10 scores
    const ctx = scoreRangeChart.value.getContext('2d');
    new Chart(ctx, {
      type: 'radar',
      data: {
        labels: recentScores.map((_, index) => `Quiz ${index + 1}`),
        datasets: [{
          label: 'Score %',
          data: recentScores.map(score => score.percentage),
          borderColor: '#42b983',
          backgroundColor: 'rgba(66, 185, 131, 0.2)',
          pointBackgroundColor: '#42b983'
        }]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Recent Performance Analysis'
          }
        },
        scales: {
          r: {
            beginAtZero: true,
            max: 100
          }
        }
      }
    });
  }
};

const getPerformanceClass = (percentage) => {
  if (percentage >= 90) return 'excellent';
  if (percentage >= 80) return 'good';
  if (percentage >= 70) return 'average';
  if (percentage >= 60) return 'below-average';
  return 'poor';
};

const getPerformanceLabel = (percentage) => {
  if (percentage >= 90) return 'Excellent';
  if (percentage >= 80) return 'Good';
  if (percentage >= 70) return 'Average';
  if (percentage >= 60) return 'Below Average';
  return 'Poor';
};

// Use utility functions for date formatting
const formatDate = formatDateTime;
const formatTime = formatRelativeTime;

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
.user-dashboard { 
  min-height: 100vh; 
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #333;
}

.user-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  padding: 1rem 2rem; 
  background-color: rgba(44, 62, 80, 0.95); 
  color: white; 
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.main-nav { display: flex; gap: 1.5rem; }
.main-nav a { 
  color: white; 
  text-decoration: none; 
  font-weight: 500; 
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.3s;
}
.main-nav a:hover { background-color: rgba(255,255,255,0.1); }
.main-nav a.router-link-exact-active { 
  color: #42b983; 
  background-color: rgba(66, 185, 131, 0.1);
}

.logout-btn { 
  background-color: #e74c3c; 
  color: white; 
  border: none; 
  padding: 0.5rem 1rem; 
  border-radius: 4px; 
  cursor: pointer; 
  margin-left: 1rem;
  transition: background-color 0.3s;
}
.logout-btn:hover { background-color: #c0392b; }

.user-search { display: flex; gap: 0.5rem; }
.user-search input { 
  padding: 0.5rem; 
  border-radius: 4px; 
  border: 1px solid #ddd; 
  background: rgba(255,255,255,0.9);
}
.user-search button { 
  padding: 0.5rem 1rem; 
  border-radius: 4px; 
  border: 1px solid #ddd; 
  background: #007bff; 
  color: white; 
  cursor: pointer;
  transition: background-color 0.3s;
}
.user-search .clear-btn { background: #6c757d; }
.user-search button:hover { opacity: 0.8; }
.welcome-message { font-weight: bold; }

.dashboard-content { 
  display: flex; 
  flex-direction: column; 
  gap: 2rem; 
  padding: 2rem; 
  max-width: 1400px;
  margin: 0 auto;
}

/* Performance Overview */
.performance-overview {
  background: rgba(255,255,255,0.95);
  padding: 2rem;
  border-radius: 15px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-icon {
  font-size: 2.5rem;
  margin-right: 1rem;
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.9;
}

/* Charts Section */
.charts-section {
  background: rgba(255,255,255,0.95);
  padding: 2rem;
  border-radius: 15px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
  margin-top: 1rem;
}

.chart-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  transition: transform 0.3s;
}

.chart-card:hover {
  transform: translateY(-2px);
}

.chart-card h3 {
  margin-bottom: 1rem;
  color: #2c3e50;
  font-size: 1.2rem;
}

.chart-container {
  position: relative;
  height: 300px;
}

/* Recent Activity */
.recent-activity {
  background: rgba(255,255,255,0.95);
  padding: 2rem;
  border-radius: 15px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
}

.activity-timeline {
  margin-top: 1rem;
}

.activity-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  margin-bottom: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.3s;
}

.activity-item:hover {
  transform: translateX(5px);
}

.activity-icon {
  font-size: 1.5rem;
  margin-right: 1rem;
}

.activity-title {
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.activity-time {
  font-size: 0.8rem;
  color: #666;
}

/* Existing sections */
section { 
  background: rgba(255,255,255,0.95); 
  padding: 2rem; 
  border-radius: 15px; 
  margin-bottom: 1rem;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
}

section h2 {
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

table { 
  width: 100%; 
  border-collapse: collapse; 
  margin-bottom: 1rem;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

th, td { 
  border: 1px solid #ddd; 
  padding: 0.75rem; 
  text-align: left; 
}

th {
  background: #f8f9fa;
  font-weight: 600;
  color: #2c3e50;
}

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
  transition: background-color 0.3s;
}

.history-btn:hover {
  background: #138496;
}

/* Performance indicators */
.excellent { color: #2e7d32; font-weight: 600; }
.good { color: #1976d2; font-weight: 600; }
.average { color: #f57c00; font-weight: 600; }
.below-average { color: #d32f2f; font-weight: 600; }
.poor { color: #c62828; font-weight: 600; }

/* Responsive design */
@media (max-width: 768px) {
  .user-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .dashboard-content {
    padding: 1rem;
  }
}
</style>