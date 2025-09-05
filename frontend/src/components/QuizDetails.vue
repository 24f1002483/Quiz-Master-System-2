<template>
  <div class="quiz-details">
    <div v-if="loading" class="loading">Loading...</div>
    
    <div v-else>
      <div class="quiz-header">
        <h2>Quiz Results: {{ attempt.quiz_title }}</h2>
        <div class="quiz-meta">
          <p><strong>Subject:</strong> {{ attempt.subject }}</p>
          <p><strong>Chapter:</strong> {{ attempt.chapter }}</p>
          <p><strong>Date:</strong> {{ formatDate(attempt.completed_at) }}</p>
          <p><strong>Time Taken:</strong> {{ formatTime(attempt.time_taken) }}</p>
        </div>
        <div class="quiz-score">
          <h3 :class="scoreClass">
            Score: {{ attempt.score }}/{{ attempt.total_questions }} ({{ attempt.percentage }}%)
          </h3>
        </div>
      </div>
      
      <div class="questions-list">
        <div v-for="(answer, index) in answers" :key="index" class="question-item">
          <h4>Question {{ index + 1 }}</h4>
          <p class="question-text">{{ answer.question_content }}</p>
          
          <div class="options">
            <div 
              v-for="(option, optIndex) in answer.options" 
              :key="optIndex"
              class="option"
              :class="{
                'selected': answer.selected_option === optIndex + 1,
                'correct': optIndex + 1 === answer.correct_answer
              }"
            >
              {{ optIndex + 1 }}) {{ option }}
            </div>
          </div>
          
          <p class="feedback" :class="answer.is_correct ? 'correct' : 'incorrect'">
            {{ answer.is_correct ? 'Correct' : 'Incorrect' }} - 
            You answered {{ answer.selected_option }}, 
            correct answer was {{ answer.correct_answer }}
          </p>
          
          <p class="time-spent">Time spent: {{ answer.time_spent }} seconds</p>
        </div>
      </div>
      
      <button @click="$router.go(-1)" class="back-btn">Back to History</button>
    </div>
  </div>
</template>

<script>
export default {
  props: ['attemptId'],
  data() {
    return {
      attempt: {},
      answers: [],
      loading: true
    }
  },
  computed: {
    scoreClass() {
      if (this.attempt.percentage >= 80) return 'excellent'
      if (this.attempt.percentage >= 60) return 'good'
      if (this.attempt.percentage >= 40) return 'average'
      return 'poor'
    }
  },
  async created() {
    await this.loadAttemptDetails()
  },
  methods: {
    async loadAttemptDetails() {
      try {
        const response = await fetch(`/api/scores/details/${this.attemptId}`, {
          headers: {
            'Authorization': `Bearer ${this.$store.state.auth.token}`
          }
        })
        const data = await response.json()
        this.attempt = data.attempt
        this.answers = data.answers
        this.loading = false
      } catch (error) {
        console.error('Error loading attempt details:', error)
        this.loading = false
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
    formatTime(seconds) {
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }
  }
}
</script>

<style scoped>
.quiz-details {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.quiz-header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.quiz-meta {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}

.quiz-score h3 {
  font-size: 1.5rem;
  margin: 1rem 0;
}

.excellent {
  color: #2ecc71;
}

.good {
  color: #3498db;
}

.average {
  color: #f39c12;
}

.poor {
  color: #e74c3c;
}

.questions-list {
  margin-top: 2rem;
}

.question-item {
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border: 1px solid #eee;
  border-radius: 8px;
}

.question-text {
  font-weight: bold;
  margin: 1rem 0;
}

.options {
  display: grid;
  gap: 0.5rem;
  margin: 1rem 0;
}

.option {
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.option.selected {
  background-color: #3498db;
  color: white;
  border-color: #2980b9;
}

.option.correct {
  background-color: #2ecc71;
  color: white;
  border-color: #27ae60;
}

.feedback {
  font-weight: bold;
  margin: 0.5rem 0;
}

.feedback.correct {
  color: #2ecc71;
}

.feedback.incorrect {
  color: #e74c3c;
}

.time-spent {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.back-btn {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 2rem;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #7f8c8d;
}
</style>