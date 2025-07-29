<template>
  <div class="score-history">
    <h2>Quiz Scores</h2>
    
    <div class="filters">
      <select v-model="selectedSubject" @change="filterAttempts">
        <option value="">All Subjects</option>
        <option v-for="subject in subjects" :key="subject" :value="subject">
          {{ subject }}
        </option>
      </select>
      
      <select v-model="selectedTimeframe" @change="filterAttempts">
        <option value="all">All Time</option>
        <option value="week">Last Week</option>
        <option value="month">Last Month</option>
        <option value="year">Last Year</option>
      </select>
    </div>
    
    <table class="scores-table">
      <thead>
        <tr>
          <th>Quiz</th>
          <th>Subject</th>
          <th>Chapter</th>
          <th>Date</th>
          <th>Score</th>
          <th>Time</th>
          <th>Details</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="attempt in filteredAttempts" :key="attempt.id">
          <td>{{ attempt.quiz_title }}</td>
          <td>{{ attempt.subject }}</td>
          <td>{{ attempt.chapter }}</td>
          <td>{{ formatDate(attempt.completed_at) }}</td>
          <td :class="getScoreClass(attempt.percentage)">
            {{ attempt.score }}/{{ attempt.total_questions }} ({{ attempt.percentage }}%)
          </td>
          <td>{{ formatTime(attempt.time_taken) }}</td>
          <td>
            <button @click="viewDetails(attempt.id)" class="details-btn">View</button>
          </td>
        </tr>
      </tbody>
    </table>
    
    <div v-if="loading" class="loading">Loading...</div>
    <div v-if="!loading && filteredAttempts.length === 0" class="no-results">
      No quiz attempts found
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      attempts: [],
      filteredAttempts: [],
      subjects: [],
      selectedSubject: '',
      selectedTimeframe: 'all',
      loading: true
    }
  },
  async created() {
    await this.loadScoreHistory()
  },
  methods: {
    async loadScoreHistory() {
      try {
        const response = await fetch('/api/scores/history', {
          headers: {
            'Authorization': `Bearer ${this.$store.state.auth.token}`
          }
        })
        this.attempts = await response.json()
        this.filteredAttempts = [...this.attempts]
        
        // Extract unique subjects
        this.subjects = [...new Set(this.attempts.map(a => a.subject))]
        
        this.loading = false
      } catch (error) {
        console.error('Error loading score history:', error)
        this.loading = false
      }
    },
    filterAttempts() {
      let filtered = [...this.attempts]
      
      // Filter by subject
      if (this.selectedSubject) {
        filtered = filtered.filter(a => a.subject === this.selectedSubject)
      }
      
      // Filter by timeframe
      const now = new Date()
      if (this.selectedTimeframe !== 'all') {
        let cutoffDate = new Date()
        
        switch (this.selectedTimeframe) {
          case 'week':
            cutoffDate.setDate(now.getDate() - 7)
            break
          case 'month':
            cutoffDate.setMonth(now.getMonth() - 1)
            break
          case 'year':
            cutoffDate.setFullYear(now.getFullYear() - 1)
            break
        }
        
        filtered = filtered.filter(a => {
          const attemptDate = new Date(a.completed_at)
          return attemptDate >= cutoffDate
        })
      }
      
      this.filteredAttempts = filtered
    },
    formatDate(dateStr) {
      return new Date(dateStr).toLocaleDateString()
    },
    formatTime(seconds) {
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    },
    getScoreClass(percentage) {
      if (percentage >= 80) return 'excellent'
      if (percentage >= 60) return 'good'
      if (percentage >= 40) return 'average'
      return 'poor'
    },
    viewDetails(attemptId) {
      this.$router.push(`/scores/details/${attemptId}`)
    }
  }
}
</script>

<style scoped>
.score-history {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.filters {
  display: flex;
  gap: 1rem;
  margin: 1rem 0;
}

.filters select {
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.scores-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.scores-table th, .scores-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.scores-table th {
  background-color: #f2f2f2;
  position: sticky;
  top: 0;
}

.excellent {
  color: #2ecc71;
  font-weight: bold;
}

.good {
  color: #3498db;
  font-weight: bold;
}

.average {
  color: #f39c12;
  font-weight: bold;
}

.poor {
  color: #e74c3c;
  font-weight: bold;
}

.details-btn {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.loading, .no-results {
  text-align: center;
  padding: 2rem;
  color: #7f8c8d;
}
</style>