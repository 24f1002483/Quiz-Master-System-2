<template>
  <div class="quiz-schedule-form">
    <h2>{{ editingQuiz ? 'Edit Quiz Schedule' : 'Create New Quiz' }}</h2>
    
    <form @submit.prevent="submitForm">
      <div class="form-group">
        <label>Quiz Title</label>
        <input v-model="form.title" required>
      </div>
      
      <div class="form-group">
        <label>Chapter</label>
        <select v-model="form.chapter_id" required>
          <option v-for="chapter in chapters" :key="chapter.id" :value="chapter.id">
            {{ chapter.name }} ({{ chapter.subject.name }})
          </option>
        </select>
      </div>
      
      <div class="form-row">
        <div class="form-group">
          <label>Start Date & Time</label>
          <input type="datetime-local" v-model="form.start_date" required>
        </div>
        
        <div class="form-group">
          <label>End Date & Time</label>
          <input type="datetime-local" v-model="form.end_date" required>
        </div>
      </div>
      
      <div class="form-group">
        <label>Duration (minutes)</label>
        <input type="number" v-model.number="form.duration" min="1" required>
      </div>
      
      <div class="form-group">
        <label>Description</label>
        <textarea v-model="form.description"></textarea>
      </div>
      
      <div class="form-actions">
        <button type="button" @click="cancel" class="cancel-btn">Cancel</button>
        <button type="submit" class="submit-btn">{{ editingQuiz ? 'Update' : 'Create' }}</button>
      </div>
    </form>
  </div>
</template>

<script>
export default {
  props: {
    chapters: Array,
    editingQuiz: Object
  },
  data() {
    return {
      form: {
        title: '',
        chapter_id: null,
        start_date: '',
        end_date: '',
        duration: 30,
        description: ''
      }
    }
  },
  created() {
    if (this.editingQuiz) {
      this.form = {
        title: this.editingQuiz.title,
        chapter_id: this.editingQuiz.chapter_id,
        start_date: this.formatForInput(this.editingQuiz.start_date),
        end_date: this.formatForInput(this.editingQuiz.end_date),
        duration: this.editingQuiz.time_duration,
        description: this.editingQuiz.description || ''
      }
    }
  },
  methods: {
    formatForInput(dateStr) {
      const date = new Date(dateStr)
      const isoString = date.toISOString()
      return isoString.substring(0, isoString.length - 8) // Remove seconds and timezone
    },
    async submitForm() {
      try {
        const payload = {
          ...this.form,
          start_date: new Date(this.form.start_date).toISOString(),
          end_date: new Date(this.form.end_date).toISOString()
        }
        
        const url = this.editingQuiz 
          ? `/api/schedule/quiz/${this.editingQuiz.id}`
          : '/api/schedule/quiz'
        
        const method = this.editingQuiz ? 'PUT' : 'POST'
        
        const response = await fetch(url, {
          method,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.$store.state.auth.token}`
          },
          body: JSON.stringify(payload)
        })
        
        if (!response.ok) {
          throw new Error(await response.text())
        }
        
        this.$emit('saved', await response.json())
      } catch (error) {
        console.error('Error saving quiz:', error)
        alert('Failed to save quiz: ' + error.message)
      }
    },
    cancel() {
      this.$emit('cancel')
    }
  }
}
</script>

<style scoped>
.quiz-schedule-form {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  max-width: 800px;
  margin: 0 auto;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group textarea {
  min-height: 100px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.cancel-btn {
  background-color: #e74c3c;
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
}

.submit-btn {
  background-color: #2ecc71;
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
}
</style>