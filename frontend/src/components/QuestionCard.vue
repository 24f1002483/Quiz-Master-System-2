<template>
  <div class="question-card">
    <div class="question-header">
      <h4>{{ question.question_title }}</h4>
      <div class="question-actions">
        <button class="edit-question-btn" @click="$emit('edit', question)" title="Edit Question">
          ✏️
        </button>
        <button class="delete-question-btn" @click="handleDelete" title="Delete Question">
          🗑️
        </button>
      </div>
    </div>
    
    <div class="question-content">
      <p class="question-statement">{{ question.question_statement }}</p>
      
      <div class="options-list">
        <div 
          v-for="(option, index) in options" 
          :key="index" 
          class="option-item"
          :class="{ 'correct-option': index + 1 === question.correct_answer }"
        >
          <span class="option-label">{{ String.fromCharCode(65 + index) }}.</span>
          <span class="option-text">{{ option }}</span>
          <span v-if="index + 1 === question.correct_answer" class="correct-indicator">✓</span>
        </div>
      </div>
      
      <div v-if="question.explanation" class="explanation">
        <strong>Explanation:</strong> {{ question.explanation }}
      </div>
      
      <div class="question-meta">
        <span class="difficulty-badge" :class="`difficulty-${question.difficulty}`">
          {{ getDifficultyText(question.difficulty) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  question: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['edit', 'delete']);

const options = computed(() => [
  props.question.option1,
  props.question.option2,
  props.question.option3,
  props.question.option4
].filter(option => option && option.trim()));

const getDifficultyText = (difficulty) => {
  const levels = {
    1: 'Easy',
    2: 'Medium', 
    3: 'Hard',
    4: 'Expert'
  };
  return levels[difficulty] || 'Medium';
};

const handleDelete = () => {
  if (confirm(`Are you sure you want to delete the question "${props.question.question_title}"?`)) {
    emit('delete', props.question.id);
  }
};
</script>

<style scoped>
.question-card {
  background: #fff;
  border: 1px solid #e0e7ff;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 8px rgba(44, 62, 80, 0.08);
  transition: all 0.2s ease;
}

.question-card:hover {
  box-shadow: 0 4px 16px rgba(44, 62, 80, 0.12);
  transform: translateY(-1px);
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #f0f0f0;
}

.question-header h4 {
  color: #2c3e50;
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  flex: 1;
  line-height: 1.4;
}

.question-actions {
  display: flex;
  gap: 0.5rem;
  margin-left: 1rem;
}

.edit-question-btn,
.delete-question-btn {
  background: none;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  padding: 0.4rem;
  border-radius: 4px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
}

.edit-question-btn:hover {
  background: #e0e7ff;
  transform: scale(1.1);
}

.delete-question-btn:hover {
  background: #ffe0e0;
  transform: scale(1.1);
}

.question-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.question-statement {
  color: #555;
  font-size: 1rem;
  line-height: 1.5;
  margin: 0;
  font-weight: 500;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.8rem;
  border-radius: 6px;
  background: #f8f9ff;
  border: 1px solid #e0e7ff;
  transition: all 0.2s ease;
}

.option-item.correct-option {
  background: #e8f5e8;
  border-color: #42b983;
}

.option-label {
  font-weight: 600;
  color: #666;
  min-width: 20px;
}

.option-text {
  flex: 1;
  color: #555;
}

.correct-indicator {
  color: #42b983;
  font-weight: bold;
  font-size: 1.1rem;
}

.explanation {
  background: #f0f7ff;
  padding: 1rem;
  border-radius: 6px;
  border-left: 4px solid #42b983;
  font-size: 0.9rem;
  color: #555;
  line-height: 1.4;
}

.question-meta {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.difficulty-badge {
  padding: 0.3rem 0.8rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
}

.difficulty-1 {
  background: #e8f5e8;
  color: #2d5a2d;
}

.difficulty-2 {
  background: #fff3cd;
  color: #856404;
}

.difficulty-3 {
  background: #f8d7da;
  color: #721c24;
}

.difficulty-4 {
  background: #d1ecf1;
  color: #0c5460;
}

/* Responsive design */
@media (max-width: 768px) {
  .question-header {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .question-actions {
    margin-left: 0;
    align-self: flex-end;
  }
  
  .option-item {
    padding: 0.4rem 0.6rem;
  }
}
</style>