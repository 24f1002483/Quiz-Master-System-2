<template>
  <div class="quiz-attempt">
    <div class="quiz-header">
      <div class="quiz-progress">
        Q{{ currentQuestionNumber }}/{{ totalQuestions }} 
        <span class="timer">{{ formattedTime }}</span>
      </div>
    </div>
    
    <div class="question-container">
      <h3 class="question-title">{{ currentQuestion.title }}</h3>
      <p class="question-content">{{ currentQuestion.content }}</p>
      
      <div class="options">
        <div 
          v-for="(option, index) in currentQuestion.options" 
          :key="index"
          class="option"
          :class="{
            'selected': selectedOption === index + 1,
            'correct': showFeedback && index + 1 === correctAnswer,
            'incorrect': showFeedback && selectedOption === index + 1 && selectedOption !== correctAnswer
          }"
          @click="selectOption(index + 1)"
        >
          {{ index + 1 }}) {{ option }}
        </div>
      </div>
    </div>
    
    <div class="quiz-footer">
      <button 
        v-if="currentQuestionNumber > 1" 
        @click="prevQuestion"
        class="nav-btn"
      >
        Previous
      </button>
      <button 
        v-if="currentQuestionNumber < totalQuestions" 
        @click="nextQuestion"
        class="nav-btn"
      >
        Save and Next
      </button>
      <button 
        v-else
        @click="submitQuiz"
        class="submit-btn"
      >
        Submit
      </button>
    </div>
    
    <div v-if="showFeedback" class="feedback">
      <p v-if="selectedOption === correctAnswer" class="correct-feedback">
        Correct! Well done.
      </p>
      <p v-else class="incorrect-feedback">
        Incorrect. The correct answer is {{ correctAnswer }}.
      </p>
    </div>
  </div>
</template>

<script>
export default {
  props: ['quizId'],
  data() {
    return {
      attemptId: null,
      currentQuestionNumber: 1,
      totalQuestions: 0,
      currentQuestion: {},
      selectedOption: null,
      correctAnswer: null,
      showFeedback: false,
      timeRemaining: 0,
      timerInterval: null,
      quizDuration: 0
    }
  },
  computed: {
    formattedTime() {
      const mins = Math.floor(this.timeRemaining / 60)
      const secs = this.timeRemaining % 60
      return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }
  },
  async created() {
    await this.startQuizAttempt()
    await this.loadQuestion()
    this.startTimer()
  },
  beforeDestroy() {
    clearInterval(this.timerInterval)
  },
  methods: {
    async startQuizAttempt() {
      try {
        const response = await fetch(`/api/user/quiz/start/${this.quizId}`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.$store.state.auth.token}`
          }
        })
        const data = await response.json()
        this.attemptId = data.id
        this.totalQuestions = data.total_questions
        this.quizDuration = data.duration || 1800 // Default to 30 minutes if no duration
        this.timeRemaining = this.quizDuration
      } catch (error) {
        console.error('Error starting quiz:', error)
      }
    },
    async loadQuestion() {
      try {
        const response = await fetch(`/api/user/quiz/question/${this.attemptId}/${this.currentQuestionNumber}`, {
          headers: {
            'Authorization': `Bearer ${this.$store.state.auth.token}`
          }
        })
        const data = await response.json()
        this.currentQuestion = data.question
      } catch (error) {
        console.error('Error loading question:', error)
      }
    },
    startTimer() {
      this.timerInterval = setInterval(() => {
        if (this.timeRemaining > 0) {
          this.timeRemaining--
        } else {
          clearInterval(this.timerInterval)
          this.submitQuiz()
        }
      }, 1000)
    },
    selectOption(option) {
      if (this.showFeedback) return
      this.selectedOption = option
    },
    async submitAnswer() {
      if (!this.selectedOption) return
      
      try {
        const response = await fetch('/api/user/quiz/answer', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.$store.state.auth.token}`
          },
          body: JSON.stringify({
            attempt_id: this.attemptId,
            question_id: this.currentQuestion.id,
            selected_option: this.selectedOption,
            time_taken: 10 // This would be calculated based on actual time
          })
        })
        const data = await response.json()
        this.correctAnswer = data.correct_answer
        this.showFeedback = true
        
        // Hide feedback after 2 seconds
        setTimeout(() => {
          this.showFeedback = false
        }, 2000)
      } catch (error) {
        console.error('Error submitting answer:', error)
      }
    },
    async nextQuestion() {
      if (this.selectedOption) {
        await this.submitAnswer()
      }
      this.currentQuestionNumber++
      this.selectedOption = null
      await this.loadQuestion()
    },
    async prevQuestion() {
      this.currentQuestionNumber--
      this.selectedOption = null
      await this.loadQuestion()
    },
    async submitQuiz() {
      if (this.selectedOption) {
        await this.submitAnswer()
      }
      
      try {
        await fetch(`/api/user/quiz/complete/${this.attemptId}`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.$store.state.auth.token}`
          }
        })
        this.$router.push(`/user/quiz/results/${this.attemptId}`)
      } catch (error) {
        console.error('Error completing quiz:', error)
      }
    }
  }
}
</script>

<style scoped>
.quiz-attempt {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  max-width: 800px;
  margin: 0 auto;
}

.quiz-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.quiz-progress {
  font-weight: bold;
  font-size: 1.2rem;
}

.timer {
  margin-left: 1rem;
  color: #e74c3c;
}

.question-container {
  margin-bottom: 2rem;
}

.question-title {
  font-size: 1.3rem;
  margin-bottom: 1rem;
}

.question-content {
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.options {
  display: grid;
  gap: 1rem;
}

.option {
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.option:hover {
  background-color: #f5f5f5;
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

.option.incorrect {
  background-color: #e74c3c;
  color: white;
  border-color: #c0392b;
}

.quiz-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 2rem;
}

.nav-btn, .submit-btn {
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.nav-btn {
  background-color: #3498db;
  color: white;
}

.submit-btn {
  background-color: #2ecc71;
  color: white;
}

.feedback {
  margin-top: 1.5rem;
  padding: 1rem;
  border-radius: 4px;
}

.correct-feedback {
  color: #27ae60;
  font-weight: bold;
}

.incorrect-feedback {
  color: #c0392b;
  font-weight: bold;
}
</style>