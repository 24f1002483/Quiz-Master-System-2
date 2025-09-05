<template>
  <div class="quiz-summary">
    <main class="summary-content">
      <section class="summary-section">
        <h2>Quiz Summary & Analytics</h2>
        <p class="section-description">Overview of quiz performance and statistics</p>
        
        <div class="summary-grid">
          <!-- Quiz Statistics -->
          <div class="summary-card">
            <h3>Quiz Statistics</h3>
            <div class="stats-grid">
              <div class="stat-item">
                <span class="stat-number">{{ quizStats.totalQuizzes }}</span>
                <span class="stat-label">Total Quizzes</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">{{ quizStats.activeQuizzes }}</span>
                <span class="stat-label">Active Quizzes</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">{{ quizStats.totalAttempts }}</span>
                <span class="stat-label">Total Attempts</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">{{ quizStats.avgScore }}%</span>
                <span class="stat-label">Average Score</span>
              </div>
            </div>
          </div>

          <!-- Recent Quiz Activity -->
          <div class="summary-card">
            <h3>🕒 Recent Activity</h3>
            <div v-if="recentActivity.length === 0" class="no-activity">
              No recent quiz activity
            </div>
            <div v-else class="activity-list">
              <div 
                v-for="activity in recentActivity" 
                :key="activity.id" 
                class="activity-item"
              >
                <div class="activity-info">
                  <span class="activity-user">{{ activity.user_name }}</span>
                  <span class="activity-quiz">{{ activity.quiz_title }}</span>
                  <span class="activity-score">{{ activity.score }}%</span>
                </div>
                <span class="activity-time">{{ formatDate(activity.completed_at) }}</span>
              </div>
            </div>
          </div>

          <!-- Top Performers -->
          <div class="summary-card">
            <h3>🏆 Top Performers</h3>
            <div v-if="topPerformers.length === 0" class="no-performers">
              No performance data available
            </div>
            <div v-else class="performers-list">
              <div 
                v-for="(performer, index) in topPerformers" 
                :key="performer.user_id" 
                class="performer-item"
              >
                <span class="performer-rank">#{{ index + 1 }}</span>
                <span class="performer-name">{{ performer.user_name }}</span>
                <span class="performer-score">{{ performer.avg_score }}%</span>
              </div>
            </div>
          </div>

          <!-- Quiz Performance Chart -->
          <div class="summary-card">
            <h3>📊 Quiz Performance</h3>
            <div class="chart-container">
              <canvas ref="performanceChart" width="400" height="200"></canvas>
            </div>
          </div>

          <!-- Subject Performance Chart -->
          <div class="summary-card">
            <h3>📚 Subject Performance</h3>
            <div class="chart-container">
              <canvas ref="subjectChart" width="400" height="200"></canvas>
            </div>
          </div>

          <!-- Daily Activity Chart -->
          <div class="summary-card">
            <h3>📅 Daily Activity</h3>
            <div class="chart-container">
              <canvas ref="dailyChart" width="400" height="200"></canvas>
            </div>
          </div>
        </div>

        <!-- Quiz List -->
        <div class="quiz-list-section">
          <h3>📝 All Quizzes</h3>
          <div class="quiz-filters">
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="Search quizzes..." 
              class="search-input"
            >
            <select v-model="statusFilter" class="status-filter">
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
          
          <div v-if="filteredQuizzes.length === 0" class="no-quizzes">
            No quizzes found
          </div>
          <div v-else class="quiz-list">
            <div 
              v-for="quiz in filteredQuizzes" 
              :key="quiz.id" 
              class="quiz-item"
            >
              <div class="quiz-info">
                <h4 class="quiz-title">{{ quiz.title }}</h4>
                <p class="quiz-subject">{{ quiz.subject_name }}</p>
                <p class="quiz-chapter">{{ quiz.chapter_name }}</p>
              </div>
              <div class="quiz-stats">
                <span class="quiz-attempts">{{ quiz.attempt_count }} attempts</span>
                <span class="quiz-avg-score">{{ quiz.avg_score }}% avg</span>
                <span class="quiz-status" :class="quiz.status">{{ quiz.status }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import { Chart } from 'chart.js/auto';
import api from '../services/axiosConfig.js';

// Reactive data
const quizStats = ref({
  totalQuizzes: 0,
  activeQuizzes: 0,
  totalAttempts: 0,
  avgScore: 0
});

const recentActivity = ref([]);
const topPerformers = ref([]);
const allQuizzes = ref([]);
const searchQuery = ref('');
const statusFilter = ref('');
const performanceChart = ref(null);
const subjectChart = ref(null);
const dailyChart = ref(null);

// Chart instances
let performanceChartInstance = null;
let subjectChartInstance = null;
let dailyChartInstance = null;

// Computed properties
const filteredQuizzes = computed(() => {
  let filtered = allQuizzes.value;
  
  if (searchQuery.value) {
    filtered = filtered.filter(quiz => 
      quiz.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      quiz.subject_name.toLowerCase().includes(searchQuery.value.toLowerCase())
    );
  }
  
  if (statusFilter.value) {
    filtered = filtered.filter(quiz => quiz.status === statusFilter.value);
  }
  
  return filtered;
});

// Functions
const loadQuizStats = async () => {
  try {
    const response = await api.get('/api/quiz-stats');
    quizStats.value = response.data;
  } catch (error) {
    console.error('Failed to load quiz stats:', error);
  }
};

const loadRecentActivity = async () => {
  try {
    const response = await api.get('/api/recent-activity');
    recentActivity.value = response.data;
  } catch (error) {
    console.error('Failed to load recent activity:', error);
  }
};

const loadTopPerformers = async () => {
  try {
    const response = await api.get('/api/top-performers');
    topPerformers.value = response.data;
  } catch (error) {
    console.error('Failed to load top performers:', error);
  }
};

const loadAllQuizzes = async () => {
  try {
    const response = await api.get('/api/quizzes');
    allQuizzes.value = response.data;
  } catch (error) {
    console.error('Failed to load quizzes:', error);
  }
};

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return 'Invalid Date';
    return date.toLocaleString();
  } catch (error) {
    return 'Invalid Date';
  }
};

const createPerformanceChart = async () => {
  try {
    const response = await api.get('/api/quiz-performance-data');
    const data = response.data;
    
    await nextTick();
    
    if (performanceChart.value) {
      // Destroy existing chart if it exists
      if (performanceChartInstance) {
        performanceChartInstance.destroy();
      }
      
      const ctx = performanceChart.value.getContext('2d');
      
      // Prepare chart data
      const chartData = data.slice(0, 10); // Show top 10 quizzes
      const labels = chartData.map(d => d.title.substring(0, 15) + (d.title.length > 15 ? '...' : ''));
      const scores = chartData.map(d => d.avg_score);
      
      if (labels.length === 0) {
        // Create empty chart with axes
        performanceChartInstance = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: ['No Data'],
            datasets: [{
              label: 'Average Score (%)',
              data: [0],
              backgroundColor: 'rgba(200, 200, 200, 0.5)',
              borderColor: 'rgba(200, 200, 200, 1)',
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true,
                max: 100,
                title: {
                  display: true,
                  text: 'Score (%)'
                }
              },
              x: {
                title: {
                  display: true,
                  text: 'Quiz'
                }
              }
            },
            plugins: {
              legend: {
                display: false
              }
            }
          }
        });
      } else {
        // Create chart with data
        performanceChartInstance = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: labels,
            datasets: [{
              label: 'Average Score (%)',
              data: scores,
              backgroundColor: 'rgba(54, 162, 235, 0.8)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true,
                max: 100,
                title: {
                  display: true,
                  text: 'Score (%)'
                }
              },
              x: {
                title: {
                  display: true,
                  text: 'Quiz'
                }
              }
            },
            plugins: {
              legend: {
                display: false
              }
            }
          }
        });
      }
    }
  } catch (error) {
    console.error('Failed to create performance chart:', error);
    // Create empty chart with axes
    if (performanceChart.value) {
      const ctx = performanceChart.value.getContext('2d');
      performanceChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['No Data'],
          datasets: [{
            label: 'Average Score (%)',
            data: [0],
            backgroundColor: 'rgba(200, 200, 200, 0.5)',
            borderColor: 'rgba(200, 200, 200, 1)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              max: 100,
              title: {
                display: true,
                text: 'Score (%)'
              }
            },
            x: {
              title: {
                display: true,
                text: 'Quiz'
              }
            }
          },
          plugins: {
            legend: {
              display: false
            }
          }
        }
      });
    }
  }
};

const createSubjectChart = async () => {
  try {
    const response = await api.get('/api/subject-performance');
    const data = response.data;
    
    await nextTick();
    
    if (subjectChart.value) {
      // Destroy existing chart if it exists
      if (subjectChartInstance) {
        subjectChartInstance.destroy();
      }
      
      const ctx = subjectChart.value.getContext('2d');
      
      // Prepare chart data
      const labels = data.map(d => d.name);
      const scores = data.map(d => d.avg_score);
      
      if (labels.length === 0) {
        // Create empty chart
        subjectChartInstance = new Chart(ctx, {
          type: 'doughnut',
          data: {
            labels: ['No Data'],
            datasets: [{
              data: [1],
              backgroundColor: ['rgba(200, 200, 200, 0.5)'],
              borderWidth: 2,
              borderColor: '#fff'
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'bottom'
              }
            }
          }
        });
      } else {
        // Create chart with data
        const colors = [
          'rgba(255, 99, 132, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 205, 86, 0.8)',
          'rgba(75, 192, 192, 0.8)',
          'rgba(153, 102, 255, 0.8)'
        ];
        
        subjectChartInstance = new Chart(ctx, {
          type: 'doughnut',
          data: {
            labels: labels,
            datasets: [{
              data: scores,
              backgroundColor: colors.slice(0, labels.length),
              borderWidth: 2,
              borderColor: '#fff'
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'bottom'
              },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    return context.label + ': ' + context.parsed + '%';
                  }
                }
              }
            }
          }
        });
      }
    }
  } catch (error) {
    console.error('Failed to create subject chart:', error);
    // Create empty chart
    if (subjectChart.value) {
      const ctx = subjectChart.value.getContext('2d');
      subjectChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['No Data'],
          datasets: [{
            data: [1],
            backgroundColor: ['rgba(200, 200, 200, 0.5)'],
            borderWidth: 2,
            borderColor: '#fff'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom'
            }
          }
        }
      });
    }
  }
};

const createDailyChart = async () => {
  try {
    const response = await api.get('/api/daily-activity');
    const data = response.data;
    
    await nextTick();
    
    if (dailyChart.value) {
      // Destroy existing chart if it exists
      if (dailyChartInstance) {
        dailyChartInstance.destroy();
      }
      
      const ctx = dailyChart.value.getContext('2d');
      
      // Prepare chart data
      const labels = data.map(d => {
        const date = new Date(d.date);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      });
      const counts = data.map(d => d.count);
      
      if (labels.length === 0 || counts.every(count => count === 0)) {
        // Create empty chart with axes
        dailyChartInstance = new Chart(ctx, {
          type: 'line',
          data: {
            labels: ['No Data'],
            datasets: [{
              label: 'Quiz Completions',
              data: [0],
              borderColor: 'rgba(200, 200, 200, 1)',
              backgroundColor: 'rgba(200, 200, 200, 0.2)',
              borderWidth: 2,
              fill: true,
              tension: 0.4
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Completions'
                }
              },
              x: {
                title: {
                  display: true,
                  text: 'Date'
                }
              }
            },
            plugins: {
              legend: {
                display: false
              }
            }
          }
        });
      } else {
        // Create chart with data
        dailyChartInstance = new Chart(ctx, {
          type: 'line',
          data: {
            labels: labels,
            datasets: [{
              label: 'Quiz Completions',
              data: counts,
              borderColor: 'rgba(75, 192, 192, 1)',
              backgroundColor: 'rgba(75, 192, 192, 0.2)',
              borderWidth: 2,
              fill: true,
              tension: 0.4
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Completions'
                }
              },
              x: {
                title: {
                  display: true,
                  text: 'Date'
                }
              }
            },
            plugins: {
              legend: {
                display: false
              }
            }
          }
        });
      }
    }
  } catch (error) {
    console.error('Failed to create daily chart:', error);
    // Create empty chart with axes
    if (dailyChart.value) {
      const ctx = dailyChart.value.getContext('2d');
      dailyChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: ['No Data'],
          datasets: [{
            label: 'Quiz Completions',
            data: [0],
            borderColor: 'rgba(200, 200, 200, 1)',
            backgroundColor: 'rgba(200, 200, 200, 0.2)',
            borderWidth: 2,
            fill: true,
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: 'Completions'
              }
            },
            x: {
              title: {
                display: true,
                text: 'Date'
              }
            }
          },
          plugins: {
            legend: {
              display: false
            }
          }
        }
      });
    }
  }
};

// Load data on mount
onMounted(async () => {
  await Promise.all([
    loadQuizStats(),
    loadRecentActivity(),
    loadTopPerformers(),
    loadAllQuizzes()
  ]);
  
  await Promise.all([
    createPerformanceChart(),
    createSubjectChart(),
    createDailyChart()
  ]);
});
</script>

<style scoped>
.quiz-summary {
  min-height: 100vh;
  background: linear-gradient(135deg, #e3f0ff 0%, #f9f9ff 100%);
  padding: 2rem 0;
}

.summary-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  padding: 2rem;
}

.summary-section {
  background: #fff;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(44, 62, 80, 0.06);
}

.section-description {
  color: #666;
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.summary-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
}

.summary-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.summary-card h3 {
  color: #333;
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.stat-item {
  text-align: center;
  padding: 1rem;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.stat-number {
  display: block;
  font-size: 2rem;
  font-weight: bold;
  color: #007bff;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
}

.activity-list, .performers-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.activity-item, .performer-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #fff;
  border-radius: 6px;
  border: 1px solid #dee2e6;
}

.activity-info, .performer-item {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.activity-user, .performer-name {
  font-weight: 500;
  color: #333;
}

.activity-quiz {
  color: #666;
  font-size: 0.9rem;
}

.activity-score, .performer-score {
  font-weight: bold;
  color: #28a745;
}

.activity-time {
  font-size: 0.8rem;
  color: #666;
}

.performer-rank {
  background: #007bff;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
}

.no-activity, .no-performers {
  text-align: center;
  color: #666;
  font-style: italic;
  padding: 1rem;
}

.chart-container {
  background: #fff;
  border-radius: 8px;
  padding: 1rem;
  border: 1px solid #dee2e6;
  text-align: center;
}

.quiz-list-section {
  margin-top: 2rem;
}

.quiz-filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.search-input, .status-filter {
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.9rem;
}

.search-input {
  flex: 1;
}

.quiz-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.quiz-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.quiz-info h4 {
  margin: 0 0 0.25rem 0;
  color: #333;
}

.quiz-subject, .quiz-chapter {
  margin: 0;
  font-size: 0.9rem;
  color: #666;
}

.quiz-stats {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.quiz-attempts, .quiz-avg-score {
  font-size: 0.9rem;
  color: #666;
}

.quiz-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.quiz-status.active {
  background: #d4edda;
  color: #155724;
}

.quiz-status.inactive {
  background: #f8d7da;
  color: #721c24;
}

.no-quizzes {
  text-align: center;
  color: #666;
  font-style: italic;
  padding: 2rem;
}

@media (max-width: 768px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .quiz-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .quiz-stats {
    width: 100%;
    justify-content: space-between;
  }
}
</style> 