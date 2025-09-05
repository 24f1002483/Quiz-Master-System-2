<template>
  <div class="upcoming-quizzes">
    <h2>Upcoming Quizzes</h2>
    
    <table class="quiz-table">
      <thead>
        <tr>
          <th>Mod-Questions</th>
          <th>Date</th>
          <th>Duration</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="quiz in quizzes" :key="quiz.id">
          <td>{{ quiz.question_count }}</td>
          <td>{{ formatDate(quiz.date) }}</td>
          <td>{{ formatDuration(quiz.duration) }}</td>
          <td>
            <button @click="startQuiz(quiz.id)" class="view-btn">View</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  data() {
    return {
      quizzes: []
    }
  },
  async created() {
    await this.loadUpcomingQuizzes()
  },
  methods: {
    async loadUpcomingQuizzes() {
      try {
        const response = await fetch('/api/user/quizzes/upcoming', {
          headers: {
            'Authorization': `Bearer ${this.$store.state.auth.token}`
          }
        })
        this.quizzes = await response.json()
      } catch (error) {
        console.error('Error loading quizzes:', error)
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return 'N/A'
      try {
        const date = new Date(dateStr)
        if (isNaN(date.getTime())) return 'Invalid Date'
        return date.toLocaleDateString()
      } catch (error) {
        return 'Invalid Date'
      }
    },
    formatDuration(seconds) {
      if (!seconds) return '00:00'
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    },
    startQuiz(quizId) {
      this.$router.push(`/user/quiz/${quizId}`)
    }
  }
}
</script>

<style scoped>
.upcoming-quizzes {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.quiz-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.quiz-table th, .quiz-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.quiz-table th {
  background-color: #f2f2f2;
}

.view-btn {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.view-btn:hover {
  background-color: #2980b9;
}
</style>