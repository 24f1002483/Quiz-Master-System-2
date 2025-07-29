<template>
  <div class="quiz-results">
    <h2>Quiz Results</h2>
    
    <div class="quiz-info">
      <p><strong>Subject:</strong> {{ quizInfo.subject }}</p>
      <p><strong>Chapter:</strong> {{ quizInfo.chapter }}</p>
      <p><strong>Number of Questions:</strong> {{ quizInfo.question_count }}</p>
      <p><strong>Your Score:</strong> {{ score }}/{{ totalQuestions }}</p>
      <p><strong>Percentage:</strong> {{ percentage }}%</p>
      <p><strong>Time Taken:</strong> {{ formatTime(timeTaken) }}</p>
    </div>
    
    <div class="question-results">
      <div v-for="(result, index) in results" :key="index" class="question-result">
        <h4>Question {{ index + 1 }}</h4>
        <p>{{ result.question }}</p>
        <p><strong>Your Answer:</strong> {{ result.selectedOption }} - {{ result.selectedText }}</p>
        <p><strong>Correct Answer:</strong> {{ result.correctOption }} - {{ result.correctText }}</p>
        <p :class="result.isCorrect ? 'correct' : 'incorrect'">
          {{ result.isCorrect ? 'Correct' : 'Incorrect' }}
        </p>
      </div>
    </div>
    
    <button @click="$router.push('/user')" class="home-btn">Back to Dashboard</button>
  </div>
</template>

<script>
export default {
  props: ['attemptId'],
  data() {
    return {
      quizInfo: {},
      results: [],
      score: 0,
      totalQuestions: 0,
      percentage: 0,
      timeTaken: 0
    }
  },
  async created() {
    await this.loadResults()
  },
  methods: {
    async loadResults() {
      try {
        // Load attempt details
        const attemptRes = await fetch(`/api/user/quiz/attempt/${this.attemptId}`, {
          headers: {
            'Authorization': `Bearer ${this.$store.state.auth.token}`
          }
        })
        const attemptData = await attemptRes.json()
        
        this.quizInfo = {
          subject: attemptData.quiz.chapter.subject.name,
          chapter: attemptData.quiz.chapter.name,
          question_count: attemptData.total_questions
        }
        
        this.score = attemptData.score
        this.totalQuestions = attemptData.total_questions
        this.percentage = Math.round((this.score / this.totalQuestions) * 100)
        this.timeTaken = attemptData.duration
        
        // Load question results
        const answersRes = await fetch(`/api/user/quiz/answers/${this.attemptId}`, {
          headers: {
            'Authorization': `Bearer ${this.$store.state.auth.token}`
          }
        })
        const answersData = await answersRes.json()
        
        this.results = answersData.map(answer => ({
          question: answer.question.content,
          selectedOption: answer.selected_option,
          selectedText: answer.question[`option${answer.selected_option}`],
          correctOption: answer.question.correct_answer,
          correctText: answer.question[`option${answer.question.correct_answer}`],
          isCorrect: answer.is_correct
        }))
      } catch (error) {
        console.error('Error loading results:', error)
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
.quiz-results {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  max-width: 800px;
  margin: 0 auto;
}

.quiz-info {
  background-color: #f9f9f9;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.quiz-info p {
  margin: 0.5rem 0;
}

.question-results {
  margin-top: 2rem;
}

.question-result {
  padding: 1rem;
  border-bottom: 1px solid #eee;
  margin-bottom: 1rem;
}

.correct {
  color: #2ecc71;
  font-weight: bold;
}

.incorrect {
  color: #e74c3c;
  font-weight: bold;
}

.home-btn {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 2rem;
}
</style>