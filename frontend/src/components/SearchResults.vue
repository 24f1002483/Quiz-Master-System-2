<template>
  <div v-if="isVisible" class="search-results-overlay" @click="closeOnOverlayClick">
    <div class="search-results-modal" @click.stop>
      <div class="search-header">
        <h2>🔍 Search Results for "{{ searchQuery }}"</h2>
        <button @click="close" class="close-btn">×</button>
      </div>
      
      <div class="search-sections">
        <!-- Quizzes Section -->
        <div class="search-section">
          <h3>📚 Quizzes ({{ quizzes.length }})</h3>
          <div class="search-grid">
            <div v-for="quiz in quizzes" :key="quiz.id" class="search-item quiz-item">
              <h4>{{ quiz.title }}</h4>
              <p><strong>ID:</strong> {{ quiz.id }}</p>
              <p><strong>Duration:</strong> {{ quiz.time_duration }} minutes</p>
              <p><strong>Status:</strong> 
                <span :class="{ 'available': quiz.is_available, 'unavailable': !quiz.is_available }">
                  {{ quiz.is_available ? 'Available' : 'Not Available' }}
                </span>
              </p>
              <p><strong>Start:</strong> {{ formatDate(quiz.start_date) }}</p>
              <p><strong>End:</strong> {{ formatDate(quiz.end_date) }}</p>
            </div>
          </div>
        </div>
        
        <!-- Scores Section -->
        <div class="search-section">
          <h3>📊 Scores ({{ scores.length }})</h3>
          <div class="search-grid">
            <div v-for="score in scores" :key="score.id" class="search-item score-item">
              <h4>{{ score.quiz_title || 'Quiz' }}</h4>
              <p><strong>ID:</strong> {{ score.id }}</p>
              <p><strong>Score:</strong> {{ score.score }}/{{ score.total_questions }}</p>
              <p><strong>Percentage:</strong> {{ score.percentage }}%</p>
              <p><strong>Date:</strong> {{ formatDate(score.timestamp) }}</p>
            </div>
          </div>
        </div>
        
        <!-- Users Section (Admin Only) -->
        <div v-if="isAdmin" class="search-section">
          <h3>👥 Users ({{ users.length }})</h3>
          <div class="search-grid">
            <div v-for="user in users" :key="user.id" class="search-item user-item">
              <h4>{{ user.username }}</h4>
              <p><strong>ID:</strong> {{ user.id }}</p>
              <p><strong>Full Name:</strong> {{ user.full_name }}</p>
              <p><strong>Role:</strong> {{ user.role }}</p>
              <p><strong>Status:</strong> 
                <span :class="{ 'active': user.is_active, 'inactive': !user.is_active }">
                  {{ user.is_active ? 'Active' : 'Inactive' }}
                </span>
              </p>
            </div>
          </div>
        </div>
        
        <!-- Subjects Section -->
        <div class="search-section">
          <h3>📖 Subjects ({{ subjects.length }})</h3>
          <div class="search-grid">
            <div v-for="subject in subjects" :key="subject.id" class="search-item subject-item">
              <h4>{{ subject.name }}</h4>
              <p><strong>ID:</strong> {{ subject.id }}</p>
              <p><strong>Description:</strong> {{ subject.description }}</p>
              <p><strong>Status:</strong> 
                <span :class="{ 'active': subject.is_active, 'inactive': !subject.is_active }">
                  {{ subject.is_active ? 'Active' : 'Inactive' }}
                </span>
              </p>
            </div>
          </div>
        </div>
        
        <!-- Chapters Section -->
        <div class="search-section">
          <h3>📑 Chapters ({{ chapters.length }})</h3>
          <div class="search-grid">
            <div v-for="chapter in chapters" :key="chapter.id" class="search-item chapter-item">
              <h4>{{ chapter.name }}</h4>
              <p><strong>ID:</strong> {{ chapter.id }}</p>
              <p><strong>Subject:</strong> {{ chapter.subject_name }}</p>
              <p><strong>Sequence:</strong> {{ chapter.sequence }}</p>
              <p><strong>Description:</strong> {{ chapter.description }}</p>
            </div>
          </div>
        </div>
        
        <!-- Questions Section -->
        <div class="search-section">
          <h3>❓ Questions ({{ questions.length }})</h3>
          <div class="search-grid">
            <div v-for="question in questions" :key="question.id" class="search-item question-item">
              <h4>{{ question.question_title.substring(0, 50) }}...</h4>
              <p><strong>ID:</strong> {{ question.id }}</p>
              <p><strong>Statement:</strong> {{ question.question_statement.substring(0, 100) }}...</p>
              <p><strong>Subject:</strong> {{ question.subject_name }}</p>
              <p><strong>Chapter:</strong> {{ question.chapter_title }}</p>
              <p><strong>Difficulty:</strong> {{ question.difficulty }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="search-footer">
        <button @click="close" class="close-search-btn">Close</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false
  },
  searchQuery: {
    type: String,
    default: ''
  },
  quizzes: {
    type: Array,
    default: () => []
  },
  scores: {
    type: Array,
    default: () => []
  },
  users: {
    type: Array,
    default: () => []
  },
  subjects: {
    type: Array,
    default: () => []
  },
  chapters: {
    type: Array,
    default: () => []
  },
  questions: {
    type: Array,
    default: () => []
  },
  isAdmin: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['close']);

const close = () => {
  emit('close');
};

const closeOnOverlayClick = (event) => {
  if (event.target.classList.contains('search-results-overlay')) {
    close();
  }
};

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleDateString();
};
</script>

<style scoped>
.search-results-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.search-results-modal {
  background: white;
  border-radius: 12px;
  max-width: 90%;
  max-height: 90%;
  width: 1200px;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.search-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  border-bottom: 2px solid #e0e0e0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px 12px 0 0;
}

.search-header h2 {
  margin: 0;
  font-size: 24px;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 28px;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.3s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.search-sections {
  padding: 20px 30px;
}

.search-section {
  margin-bottom: 30px;
}

.search-section h3 {
  color: #333;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 10px;
  margin-bottom: 20px;
  font-size: 20px;
}

.search-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.search-item {
  background: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.search-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.search-item h4 {
  margin: 0 0 10px 0;
  color: #2c3e50;
  font-size: 16px;
  font-weight: 600;
}

.search-item p {
  margin: 5px 0;
  font-size: 14px;
  color: #555;
}

.search-item strong {
  color: #333;
}

/* Item type specific styling */
.quiz-item {
  border-left: 4px solid #3498db;
}

.score-item {
  border-left: 4px solid #e74c3c;
}

.user-item {
  border-left: 4px solid #2ecc71;
}

.subject-item {
  border-left: 4px solid #f39c12;
}

.chapter-item {
  border-left: 4px solid #9b59b6;
}

.question-item {
  border-left: 4px solid #1abc9c;
}

/* Status indicators */
.available {
  color: #27ae60;
  font-weight: 600;
}

.unavailable {
  color: #e74c3c;
  font-weight: 600;
}

.active {
  color: #27ae60;
  font-weight: 600;
}

.inactive {
  color: #e74c3c;
  font-weight: 600;
}

.search-footer {
  padding: 20px 30px;
  border-top: 2px solid #e0e0e0;
  text-align: center;
  background: #f8f9fa;
  border-radius: 0 0 12px 12px;
}

.close-search-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.close-search-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

/* Responsive design */
@media (max-width: 768px) {
  .search-results-modal {
    max-width: 95%;
    margin: 10px;
  }
  
  .search-grid {
    grid-template-columns: 1fr;
  }
  
  .search-header {
    padding: 15px 20px;
  }
  
  .search-sections {
    padding: 15px 20px;
  }
  
  .search-footer {
    padding: 15px 20px;
  }
}
</style> 