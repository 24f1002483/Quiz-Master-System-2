<template>
  <div class="quiz-timer" :class="timerClass">
    <span v-if="timeRemaining > 0">
      {{ formattedTime }}
    </span>
    <span v-else>
      Time's up!
    </span>
  </div>
</template>

<script>
export default {
  props: {
    attemptId: {
      type: Number,
      required: true
    },
    initialTime: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      timeRemaining: this.initialTime,
      timerInterval: null,
      isExpired: false
    }
  },
  computed: {
    formattedTime() {
      const mins = Math.floor(this.timeRemaining / 60)
      const secs = this.timeRemaining % 60
      return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    },
    timerClass() {
      if (this.timeRemaining <= 0) return 'expired'
      if (this.timeRemaining < 60) return 'warning'
      return 'normal'
    }
  },
  mounted() {
    this.startTimer()
  },
  beforeDestroy() {
    clearInterval(this.timerInterval)
  },
  methods: {
    startTimer() {
      this.timerInterval = setInterval(async () => {
        if (this.timeRemaining > 0) {
          this.timeRemaining--
          
          // Check with server every 30 seconds to sync time
          if (this.timeRemaining % 30 === 0) {
            await this.syncWithServer()
          }
        } else {
          clearInterval(this.timerInterval)
          this.isExpired = true
          this.$emit('time-expired')
        }
      }, 1000)
    },
    async syncWithServer() {
      try {
        const response = await fetch(`/api/user/quiz/check-time/${this.attemptId}`, {
          headers: {
            'Authorization': `Bearer ${this.$store.state.auth.token}`
          }
        })
        const data = await response.json()
        
        if (data.status === 'expired') {
          this.timeRemaining = 0
          clearInterval(this.timerInterval)
          this.isExpired = true
          this.$emit('time-expired')
        } else {
          // Adjust client time to match server if there's a discrepancy
          const discrepancy = this.timeRemaining - data.time_remaining
          if (Math.abs(discrepancy) > 5) {
            this.timeRemaining = data.time_remaining
          }
        }
      } catch (error) {
        console.error('Error syncing time with server:', error)
      }
    }
  }
}
</script>

<style scoped>
.quiz-timer {
  font-size: 1.5rem;
  font-weight: bold;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  display: inline-block;
}

.normal {
  background-color: #2ecc71;
  color: white;
}

.warning {
  background-color: #f39c12;
  color: white;
  animation: pulse 1s infinite;
}

.expired {
  background-color: #e74c3c;
  color: white;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}
</style>