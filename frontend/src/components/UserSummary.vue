<template>
  <div class="user-summary">
    <header class="summary-header">
      <h1>📊 Your Learning Summary</h1>
      <p class="summary-subtitle">Comprehensive analysis of your quiz performance and progress</p>
    </header>

    <main class="summary-content">
      <!-- Key Performance Indicators -->
      <section class="kpi-section">
        <h2>🎯 Key Performance Indicators</h2>
        <div class="kpi-grid">
          <div class="kpi-card primary">
            <div class="kpi-icon">📈</div>
            <div class="kpi-content">
              <div class="kpi-value">{{ userStats.averageScore }}%</div>
              <div class="kpi-label">Overall Average</div>
              <div class="kpi-trend" :class="getTrendClass(userStats.averageScore)">
                {{ getTrendText(userStats.averageScore) }}
              </div>
            </div>
          </div>
          
          <div class="kpi-card success">
            <div class="kpi-icon">🏆</div>
            <div class="kpi-content">
              <div class="kpi-value">{{ userStats.bestScore }}%</div>
              <div class="kpi-label">Best Score</div>
              <div class="kpi-trend positive">Personal Best</div>
            </div>
          </div>
          
          <div class="kpi-card info">
            <div class="kpi-icon">📝</div>
            <div class="kpi-content">
              <div class="kpi-value">{{ userStats.totalQuizzesTaken }}</div>
              <div class="kpi-label">Quizzes Completed</div>
              <div class="kpi-trend">Total Attempts</div>
            </div>
          </div>
          
          <div class="kpi-card warning">
            <div class="kpi-icon">📚</div>
            <div class="kpi-content">
              <div class="kpi-value">{{ userStats.subjectsCovered }}</div>
              <div class="kpi-label">Subjects Covered</div>
              <div class="kpi-trend">Diverse Learning</div>
            </div>
          </div>
        </div>
      </section>

      <!-- Advanced Analytics Charts -->
      <section class="analytics-section">
        <h2>📊 Advanced Analytics</h2>
        <div class="analytics-grid">
          <!-- Performance Trend Analysis -->
          <div class="chart-container large">
            <h3>📈 Performance Trend Analysis</h3>
            <div class="chart-wrapper">
              <canvas ref="performanceTrendChart"></canvas>
            </div>
            <div class="chart-insights">
              <div class="insight-item">
                <span class="insight-label">Trend:</span>
                <span class="insight-value" :class="getTrendClass(userStats.averageScore)">
                  {{ getTrendDescription(userStats.averageScore) }}
                </span>
              </div>
              <div class="insight-item">
                <span class="insight-label">Consistency:</span>
                <span class="insight-value">{{ getConsistencyScore() }}%</span>
              </div>
            </div>
          </div>

          <!-- Subject Mastery Chart -->
          <div class="chart-container">
            <h3>🎯 Subject Mastery</h3>
            <div class="chart-wrapper">
              <canvas ref="subjectMasteryChart"></canvas>
            </div>
          </div>

          <!-- Score Distribution -->
          <div class="chart-container">
            <h3>📊 Score Distribution</h3>
            <div class="chart-wrapper">
              <canvas ref="scoreDistributionChart"></canvas>
            </div>
          </div>

          <!-- Learning Progress Timeline -->
          <div class="chart-container large">
            <h3>⏰ Learning Progress Timeline</h3>
            <div class="chart-wrapper">
              <canvas ref="progressTimelineChart"></canvas>
            </div>
          </div>

          <!-- Performance Heatmap -->
          <div class="chart-container">
            <h3>🔥 Performance Heatmap</h3>
            <div class="chart-wrapper">
              <canvas ref="performanceHeatmapChart"></canvas>
            </div>
          </div>

          <!-- Improvement Areas -->
          <div class="chart-container">
            <h3>🎯 Areas for Improvement</h3>
            <div class="chart-wrapper">
              <canvas ref="improvementAreasChart"></canvas>
            </div>
          </div>
        </div>
      </section>

      <!-- Detailed Performance Breakdown -->
      <section class="breakdown-section">
        <h2>📋 Detailed Performance Breakdown</h2>
        <div class="breakdown-grid">
          <!-- Quiz-by-Quiz Analysis -->
          <div class="breakdown-card">
            <h3>📝 Quiz-by-Quiz Analysis</h3>
            <div class="quiz-analysis">
              <div v-for="(score, index) in detailedScores" :key="score.id" class="quiz-item">
                <div class="quiz-header">
                  <span class="quiz-number">#{{ index + 1 }}</span>
                  <span class="quiz-title">{{ score.quiz_title || 'Quiz' }}</span>
                  <span class="quiz-score" :class="getScoreClass(score.percentage)">
                    {{ score.percentage }}%
                  </span>
                </div>
                <div class="quiz-details">
                  <span class="quiz-date">{{ formatDate(score.timestamp) }}</span>
                  <span class="quiz-performance">{{ getPerformanceLabel(score.percentage) }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Performance Insights -->
          <div class="breakdown-card">
            <h3>💡 Performance Insights</h3>
            <div class="insights-list">
              <div class="insight-card" v-for="insight in performanceInsights" :key="insight.id">
                <div class="insight-icon">{{ insight.icon }}</div>
                <div class="insight-content">
                  <div class="insight-title">{{ insight.title }}</div>
                  <div class="insight-description">{{ insight.description }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Recommendations -->
      <section class="recommendations-section">
        <h2>🎯 Personalized Recommendations</h2>
        <div class="recommendations-grid">
          <div v-for="recommendation in recommendations" :key="recommendation.id" class="recommendation-card">
            <div class="recommendation-icon">{{ recommendation.icon }}</div>
            <div class="recommendation-content">
              <h4>{{ recommendation.title }}</h4>
              <p>{{ recommendation.description }}</p>
              <div class="recommendation-priority" :class="recommendation.priority">
                {{ recommendation.priority }} Priority
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue';
import axios from 'axios';
import Chart from 'chart.js/auto';

// Chart references
const performanceTrendChart = ref(null);
const subjectMasteryChart = ref(null);
const scoreDistributionChart = ref(null);
const progressTimelineChart = ref(null);
const performanceHeatmapChart = ref(null);
const improvementAreasChart = ref(null);

// Data
const scores = ref([]);
const userStats = ref({
  averageScore: 0,
  bestScore: 0,
  totalQuizzesTaken: 0,
  subjectsCovered: 0
});

const detailedScores = ref([]);
const performanceInsights = ref([]);
const recommendations = ref([]);

// Fetch user data
const fetchUserData = async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/user/quizzes/scores', {
      withCredentials: true
    });
    
    scores.value = response.data;
    detailedScores.value = response.data;
    
    calculateUserStats();
    generatePerformanceInsights();
    generateRecommendations();
    
    await nextTick();
    initializeCharts();
    
  } catch (error) {
    console.error('Error fetching user data:', error);
  }
};

const calculateUserStats = () => {
  if (scores.value.length === 0) return;

  const totalQuizzes = scores.value.length;
  const totalScore = scores.value.reduce((sum, score) => sum + score.percentage, 0);
  const averageScore = Math.round(totalScore / totalQuizzes);
  const bestScore = Math.max(...scores.value.map(score => score.percentage));
  
  const subjects = new Set(scores.value.map(score => {
    const title = score.quiz_title || '';
    return title.split(' - ')[0] || 'Unknown';
  }));

  userStats.value = {
    averageScore,
    bestScore,
    totalQuizzesTaken: totalQuizzes,
    subjectsCovered: subjects.size
  };
};

const generatePerformanceInsights = () => {
  const insights = [];
  
  if (scores.value.length === 0) {
    insights.push({
      id: 1,
      icon: '📚',
      title: 'Start Your Learning Journey',
      description: 'Take your first quiz to begin tracking your progress and performance.'
    });
    performanceInsights.value = insights;
    return;
  }

  // Analyze performance trends
  const recentScores = scores.value.slice(-5);
  const olderScores = scores.value.slice(0, -5);
  
  if (recentScores.length > 0 && olderScores.length > 0) {
    const recentAvg = recentScores.reduce((sum, s) => sum + s.percentage, 0) / recentScores.length;
    const olderAvg = olderScores.reduce((sum, s) => sum + s.percentage, 0) / olderScores.length;
    
    if (recentAvg > olderAvg) {
      insights.push({
        id: 1,
        icon: '📈',
        title: 'Improving Performance',
        description: `Your recent scores (${Math.round(recentAvg)}%) are better than your earlier scores (${Math.round(olderAvg)}%). Keep up the great work!`
      });
    } else if (recentAvg < olderAvg) {
      insights.push({
        id: 1,
        icon: '⚠️',
        title: 'Performance Decline',
        description: `Your recent scores (${Math.round(recentAvg)}%) are lower than your earlier scores (${Math.round(olderAvg)}%). Consider reviewing previous topics.`
      });
    }
  }

  // Analyze consistency
  const scoreVariance = calculateScoreVariance();
  if (scoreVariance < 10) {
    insights.push({
      id: 2,
      icon: '🎯',
      title: 'Consistent Performance',
      description: 'Your scores show excellent consistency. This indicates strong understanding across topics.'
    });
  } else {
    insights.push({
      id: 2,
      icon: '📊',
      title: 'Variable Performance',
      description: 'Your scores vary significantly. Focus on areas where you consistently score lower.'
    });
  }

  // Analyze subject performance
  const subjectPerformance = analyzeSubjectPerformance();
  const bestSubject = Object.entries(subjectPerformance).reduce((a, b) => a[1] > b[1] ? a : b);
  const worstSubject = Object.entries(subjectPerformance).reduce((a, b) => a[1] < b[1] ? a : b);
  
  insights.push({
    id: 3,
    icon: '🏆',
    title: 'Strongest Subject',
    description: `You excel in ${bestSubject[0]} with an average of ${Math.round(bestSubject[1])}%.`
  });

  insights.push({
    id: 4,
    icon: '📚',
    title: 'Focus Area',
    description: `Consider spending more time on ${worstSubject[0]} where your average is ${Math.round(worstSubject[1])}%.`
  });

  performanceInsights.value = insights;
};

const generateRecommendations = () => {
  const recs = [];
  
  if (scores.value.length === 0) {
    recs.push({
      id: 1,
      icon: '🚀',
      title: 'Take Your First Quiz',
      description: 'Start with any available quiz to begin your learning journey.',
      priority: 'high'
    });
    recommendations.value = recs;
    return;
  }

  // Analyze for recommendations
  const averageScore = userStats.value.averageScore;
  
  if (averageScore < 70) {
    recs.push({
      id: 1,
      icon: '📖',
      title: 'Review Fundamentals',
      description: 'Focus on understanding basic concepts before attempting advanced topics.',
      priority: 'high'
    });
  }

  if (userStats.value.subjectsCovered < 3) {
    recs.push({
      id: 2,
      icon: '🌍',
      title: 'Explore More Subjects',
      description: 'Try quizzes from different subjects to broaden your knowledge base.',
      priority: 'medium'
    });
  }

  const recentScores = scores.value.slice(-3);
  const recentAvg = recentScores.reduce((sum, s) => sum + s.percentage, 0) / recentScores.length;
  
  if (recentAvg < averageScore) {
    recs.push({
      id: 3,
      icon: '🔄',
      title: 'Practice Regularly',
      description: 'Your recent performance suggests you need more regular practice.',
      priority: 'high'
    });
  }

  if (averageScore >= 85) {
    recs.push({
      id: 4,
      icon: '🎯',
      title: 'Challenge Yourself',
      description: 'You\'re doing great! Try more difficult quizzes to push your limits.',
      priority: 'low'
    });
  }

  recommendations.value = recs;
};

const initializeCharts = () => {
  if (scores.value.length === 0) return;

  // Performance Trend Chart
  if (performanceTrendChart.value) {
    const ctx = performanceTrendChart.value.getContext('2d');
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
          fill: true,
          pointRadius: 6,
          pointHoverRadius: 8
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: 'Performance Trend Over Time',
            font: { size: 16, weight: 'bold' }
          },
          legend: {
            display: false
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            grid: {
              color: 'rgba(0,0,0,0.1)'
            }
          },
          x: {
            grid: {
              color: 'rgba(0,0,0,0.1)'
            }
          }
        }
      }
    });
  }

  // Subject Mastery Chart
  if (subjectMasteryChart.value) {
    const subjectData = analyzeSubjectPerformance();
    const ctx = subjectMasteryChart.value.getContext('2d');
    new Chart(ctx, {
      type: 'radar',
      data: {
        labels: Object.keys(subjectData),
        datasets: [{
          label: 'Mastery Level %',
          data: Object.values(subjectData),
          borderColor: '#FF6384',
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          pointBackgroundColor: '#FF6384',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: '#FF6384'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: 'Subject Mastery Analysis',
            font: { size: 16, weight: 'bold' }
          }
        },
        scales: {
          r: {
            beginAtZero: true,
            max: 100,
            ticks: {
              stepSize: 20
            }
          }
        }
      }
    });
  }

  // Score Distribution Chart
  if (scoreDistributionChart.value) {
    const distribution = calculateScoreDistribution();
    const ctx = scoreDistributionChart.value.getContext('2d');
    new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: Object.keys(distribution),
        datasets: [{
          data: Object.values(distribution),
          backgroundColor: [
            '#4CAF50',
            '#8BC34A',
            '#FFC107',
            '#FF9800',
            '#F44336',
            '#9C27B0'
          ],
          borderWidth: 2,
          borderColor: '#fff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: 'Score Distribution',
            font: { size: 16, weight: 'bold' }
          },
          legend: {
            position: 'bottom'
          }
        }
      }
    });
  }

  // Progress Timeline Chart
  if (progressTimelineChart.value) {
    const timelineData = scores.value.map(score => ({
      x: new Date(score.timestamp),
      y: score.percentage
    }));
    
    const ctx = progressTimelineChart.value.getContext('2d');
    new Chart(ctx, {
      type: 'scatter',
      data: {
        datasets: [{
          label: 'Quiz Performance',
          data: timelineData,
          backgroundColor: '#42b983',
          pointRadius: 8,
          pointHoverRadius: 10
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: 'Learning Progress Timeline',
            font: { size: 16, weight: 'bold' }
          }
        },
        scales: {
          x: {
            type: 'time',
            time: {
              unit: 'day'
            },
            title: {
              display: true,
              text: 'Date'
            }
          },
          y: {
            beginAtZero: true,
            max: 100,
            title: {
              display: true,
              text: 'Score %'
            }
          }
        }
      }
    });
  }
};

// Helper functions
const analyzeSubjectPerformance = () => {
  const subjectData = {};
  scores.value.forEach(score => {
    const subject = score.quiz_title?.split(' - ')[0] || 'Unknown';
    if (!subjectData[subject]) {
      subjectData[subject] = { total: 0, count: 0 };
    }
    subjectData[subject].total += score.percentage;
    subjectData[subject].count += 1;
  });

  const averages = {};
  Object.keys(subjectData).forEach(subject => {
    averages[subject] = Math.round(subjectData[subject].total / subjectData[subject].count);
  });

  return averages;
};

const calculateScoreDistribution = () => {
  const distribution = {
    '90-100%': 0,
    '80-89%': 0,
    '70-79%': 0,
    '60-69%': 0,
    '50-59%': 0,
    'Below 50%': 0
  };

  scores.value.forEach(score => {
    if (score.percentage >= 90) distribution['90-100%']++;
    else if (score.percentage >= 80) distribution['80-89%']++;
    else if (score.percentage >= 70) distribution['70-79%']++;
    else if (score.percentage >= 60) distribution['60-69%']++;
    else if (score.percentage >= 50) distribution['50-59%']++;
    else distribution['Below 50%']++;
  });

  return distribution;
};

const calculateScoreVariance = () => {
  if (scores.value.length < 2) return 0;
  
  const values = scores.value.map(score => score.percentage);
  const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
  const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length;
  
  return Math.sqrt(variance);
};

const getConsistencyScore = () => {
  const variance = calculateScoreVariance();
  return Math.max(0, Math.round(100 - variance));
};

const getTrendClass = (score) => {
  if (score >= 85) return 'positive';
  if (score >= 70) return 'neutral';
  return 'negative';
};

const getTrendText = (score) => {
  if (score >= 85) return 'Excellent';
  if (score >= 70) return 'Good';
  return 'Needs Improvement';
};

const getTrendDescription = (score) => {
  if (score >= 85) return 'Outstanding performance trend';
  if (score >= 70) return 'Good performance trend';
  return 'Performance needs attention';
};

const getScoreClass = (percentage) => {
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

const formatDate = (timestamp) => {
  return new Date(timestamp).toLocaleDateString();
};

onMounted(() => {
  fetchUserData();
});
</script>

<style scoped>
.user-summary {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #333;
}

.summary-header {
  text-align: center;
  padding: 3rem 2rem;
  color: white;
}

.summary-header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  font-weight: 700;
}

.summary-subtitle {
  font-size: 1.2rem;
  opacity: 0.9;
}

.summary-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem 2rem;
}

/* KPI Section */
.kpi-section {
  background: rgba(255,255,255,0.95);
  padding: 2rem;
  border-radius: 15px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
  margin-bottom: 2rem;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.kpi-card {
  display: flex;
  align-items: center;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  transition: transform 0.3s;
  color: white;
}

.kpi-card:hover {
  transform: translateY(-5px);
}

.kpi-card.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.kpi-card.success {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
}

.kpi-card.info {
  background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
}

.kpi-card.warning {
  background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
}

.kpi-icon {
  font-size: 2.5rem;
  margin-right: 1rem;
}

.kpi-value {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.kpi-label {
  font-size: 0.9rem;
  opacity: 0.9;
  margin-bottom: 0.5rem;
}

.kpi-trend {
  font-size: 0.8rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  background: rgba(255,255,255,0.2);
}

.kpi-trend.positive {
  background: rgba(76, 175, 80, 0.3);
}

.kpi-trend.negative {
  background: rgba(244, 67, 54, 0.3);
}

/* Analytics Section */
.analytics-section {
  background: rgba(255,255,255,0.95);
  padding: 2rem;
  border-radius: 15px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
  margin-bottom: 2rem;
}

.analytics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
  margin-top: 1rem;
}

.chart-container {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  transition: transform 0.3s;
}

.chart-container:hover {
  transform: translateY(-2px);
}

.chart-container.large {
  grid-column: span 2;
}

.chart-container h3 {
  margin-bottom: 1rem;
  color: #2c3e50;
  font-size: 1.2rem;
}

.chart-wrapper {
  position: relative;
  height: 300px;
  margin-bottom: 1rem;
}

.chart-insights {
  display: flex;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.insight-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.insight-label {
  font-weight: 600;
  color: #666;
}

.insight-value {
  font-weight: 600;
}

.insight-value.positive { color: #4CAF50; }
.insight-value.negative { color: #F44336; }
.insight-value.neutral { color: #FF9800; }

/* Breakdown Section */
.breakdown-section {
  background: rgba(255,255,255,0.95);
  padding: 2rem;
  border-radius: 15px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
  margin-bottom: 2rem;
}

.breakdown-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-top: 1rem;
}

.breakdown-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.breakdown-card h3 {
  margin-bottom: 1rem;
  color: #2c3e50;
  font-size: 1.2rem;
}

.quiz-analysis {
  max-height: 400px;
  overflow-y: auto;
}

.quiz-item {
  padding: 1rem;
  border-bottom: 1px solid #eee;
  transition: background-color 0.3s;
}

.quiz-item:hover {
  background-color: #f8f9fa;
}

.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.quiz-number {
  font-weight: bold;
  color: #666;
}

.quiz-title {
  flex: 1;
  margin: 0 1rem;
  font-weight: 500;
}

.quiz-score {
  font-weight: bold;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.quiz-details {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  color: #666;
}

.insights-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.insight-card {
  display: flex;
  align-items: flex-start;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  transition: transform 0.3s;
}

.insight-card:hover {
  transform: translateX(5px);
}

.insight-icon {
  font-size: 1.5rem;
  margin-right: 1rem;
  margin-top: 0.25rem;
}

.insight-title {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.insight-description {
  font-size: 0.9rem;
  color: #666;
  line-height: 1.4;
}

/* Recommendations Section */
.recommendations-section {
  background: rgba(255,255,255,0.95);
  padding: 2rem;
  border-radius: 15px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.recommendation-card {
  display: flex;
  align-items: flex-start;
  padding: 1.5rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  transition: transform 0.3s;
}

.recommendation-card:hover {
  transform: translateY(-2px);
}

.recommendation-icon {
  font-size: 2rem;
  margin-right: 1rem;
  margin-top: 0.25rem;
}

.recommendation-content h4 {
  margin-bottom: 0.5rem;
  color: #2c3e50;
  font-size: 1.1rem;
}

.recommendation-content p {
  margin-bottom: 1rem;
  color: #666;
  line-height: 1.4;
}

.recommendation-priority {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.recommendation-priority.high {
  background: #ffebee;
  color: #c62828;
}

.recommendation-priority.medium {
  background: #fff3e0;
  color: #f57c00;
}

.recommendation-priority.low {
  background: #e8f5e8;
  color: #2e7d32;
}

/* Performance indicators */
.excellent { color: #2e7d32; font-weight: 600; }
.good { color: #1976d2; font-weight: 600; }
.average { color: #f57c00; font-weight: 600; }
.below-average { color: #d32f2f; font-weight: 600; }
.poor { color: #c62828; font-weight: 600; }

/* Responsive design */
@media (max-width: 768px) {
  .summary-header h1 {
    font-size: 2rem;
  }
  
  .kpi-grid {
    grid-template-columns: 1fr;
  }
  
  .analytics-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-container.large {
    grid-column: span 1;
  }
  
  .breakdown-grid {
    grid-template-columns: 1fr;
  }
  
  .recommendations-grid {
    grid-template-columns: 1fr;
  }
  
  .summary-content {
    padding: 0 1rem 1rem;
  }
}
</style> 