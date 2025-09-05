<template>
  <div class="quiz-management-section">
    <h2>Quiz Management</h2>

    <div class="quiz-cards-container">
      <div v-for="quiz in quizzes" :key="quiz.id" class="quiz-card">
        <div class="quiz-header">
          <h3>{{ quiz.title }}</h3>
          <div class="quiz-actions-header">
            <button class="edit-quiz-btn" @click="handleEditQuiz(quiz)" title="Edit Quiz">
              Edit
            </button>
            <button class="delete-quiz-btn-header" @click="handleDeleteQuiz(quiz.id)" title="Delete Quiz">
              Delete
            </button>
          </div>
        </div>
        <p class="quiz-info">
          <span class="question-count">{{ quiz.questions ? quiz.questions.length : 0 }} questions</span>
          <span class="quiz-duration">{{ quiz.time_duration }} minutes</span>
        </p>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Question Title</th>
                <th>Statement</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="quiz.questions && quiz.questions.length > 0" v-for="question in quiz.questions" :key="question.id">
                <td>{{ question.id }}</td>
                <td>{{ question.question_title }}</td>
                <td>{{ question.question_statement }}</td>
                <td class="action-buttons">
                  <button class="edit-btn" @click="handleEditQuestion(quiz.id, question.id)">Edit</button>
                  <button class="delete-btn" @click="handleDeleteQuestion(quiz.id, question.id)">Delete</button>
                </td>
              </tr>
              <tr v-else>
                <td colspan="4" style="text-align: center; color: #666; padding: 1rem;">
                  No questions added yet. Click "+ Question" to add the first question.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="quiz-actions">
          <button class="add-question-btn" @click="handleAddQuestion(quiz.id)">+ Question</button>
        </div>
      </div>
    </div>

    <button class="new-quiz-btn" @click="handleAddQuiz">+ New Quiz</button>

    <!-- Modals -->
    <NewQuizModal v-if="showAddQuiz" :chapters="chapters" @save="addQuiz" @cancel="showAddQuiz = false" />
    <NewQuestionModal v-if="showAddQuestion" :chapters="chapters" @save="addQuestion" @cancel="showAddQuestion = false" />
    <EditQuestionModal 
      v-if="showEditQuestion && selectedQuestion" 
      :question="selectedQuestion" 
      @save="editQuestion" 
      @cancel="showEditQuestion = false; selectedQuestion = null" 
    />
    <EditQuizModal 
      v-if="showEditQuiz && selectedQuiz" 
      :quiz="selectedQuiz" 
      :chapters="chapters"
      @save="editQuiz" 
      @cancel="showEditQuiz = false; selectedQuiz = null" 
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { fetchAllQuizzes, createQuiz, deleteQuiz, updateQuiz } from '../services/quizService.js';
import { createQuestion, deleteQuestion, updateQuestion } from '../services/questionService.js';
import { fetchAllChapters } from '../services/chapterService.js';
import NewQuizModal from './NewQuizModal.vue';
import NewQuestionModal from './NewQuestionModal.vue';
import EditQuestionModal from './EditQuestionModal.vue';
import EditQuizModal from './EditQuizModal.vue';

const quizzes = ref([]);
const chapters = ref([]);
const showAddQuiz = ref(false);
const showAddQuestion = ref(false);
const showEditQuestion = ref(false);
const showEditQuiz = ref(false);
const selectedQuizId = ref(null);
const selectedQuiz = ref(null);
const selectedQuestion = ref(null);

const loadQuizzes = async () => {
  try {
    const allQuizzes = await fetchAllQuizzes();
    quizzes.value = allQuizzes;
  } catch (error) {
    console.error('Error loading quizzes:', error);
    alert('Error loading quizzes: ' + error);
  }
};

const loadChapters = async () => {
  try {
    // Fetch all chapters from the database
    const allChapters = await fetchAllChapters();
    console.log('Fetched chapters:', allChapters);
    chapters.value = allChapters;
  } catch (error) {
    console.error('Error loading chapters:', error);
    alert('Error loading chapters: ' + error);
  }
};

const handleAddQuiz = () => {
  showAddQuiz.value = true;
};

const handleAddQuestion = (quizId) => {
  selectedQuizId.value = quizId;
  // Find the selected quiz to get its chapter_id
  selectedQuiz.value = quizzes.value.find(quiz => quiz.id === quizId);
  showAddQuestion.value = true;
};

const handleEditQuiz = (quiz) => {
  console.log('Edit quiz clicked:', quiz);
  selectedQuiz.value = quiz;
  showEditQuiz.value = true;
  console.log('Modal should show:', showEditQuiz.value);
};

const handleEditQuestion = (quizId, questionId) => {
  // Find the quiz and question to edit
  const quiz = quizzes.value.find(q => q.id === quizId);
  if (quiz && quiz.questions) {
    const question = quiz.questions.find(q => q.id === questionId);
    if (question) {
      selectedQuestion.value = question;
      selectedQuizId.value = quizId;
      showEditQuestion.value = true;
    }
  }
};

const handleDeleteQuestion = async (quizId, questionId) => {
  if (confirm('Are you sure you want to delete this question? This action cannot be undone.')) {
    try {
      await deleteQuestion(questionId);
      await loadQuizzes();
    } catch (error) {
      console.error('Error deleting question:', error);
      alert('Error deleting question: ' + error);
    }
  }
};

const handleDeleteQuiz = async (quizId) => {
  if (confirm('Are you sure you want to delete this quiz? This action cannot be undone.')) {
    try {
      await deleteQuiz(quizId);
      await loadQuizzes();
    } catch (error) {
      console.error('Error deleting quiz:', error);
      alert('Error deleting quiz: ' + error);
    }
  }
};

const addQuiz = async (quiz) => {
  try {
    const quizData = {
      title: quiz.title,
      description: quiz.description,
      chapter_id: parseInt(quiz.chapterId),
      start_date: quiz.start_date,
      end_date: quiz.end_date,
      duration: parseInt(quiz.duration)
    };
    await createQuiz(quizData);
    showAddQuiz.value = false;
    await loadQuizzes();
  } catch (error) {
    alert('Error creating quiz: ' + error);
  }
};

const addQuestion = async (question) => {
  try {
    const questionData = {
      quiz_id: selectedQuizId.value,         // Add quiz_id - now required
      question_title: question.title,         // Add question_title field
      question_statement: question.statement,  // Changed from 'statement' to 'question_statement'
      option1: question.options[0],           // Changed from 'options' array to individual options
      option2: question.options[1],
      option3: question.options[2],
      option4: question.options[3],
      correct_answer: parseInt(question.correctOption),  // Changed from 'correct_option' to 'correct_answer'
      explanation: '',  // Optional field
      difficulty: 3     // Optional field with default value
    };
    await createQuestion(questionData);
    showAddQuestion.value = false;
    await loadQuizzes();
  } catch (error) {
    console.error('Error creating question:', error);
    alert('Error creating question: ' + error);
  }
};

const editQuestion = async (questionData) => {
  try {
    await updateQuestion(questionData.id, questionData);
    showEditQuestion.value = false;
    selectedQuestion.value = null;
    await loadQuizzes();
  } catch (error) {
    console.error('Error updating question:', error);
    alert('Error updating question: ' + error);
  }
};

const editQuiz = async (quizData) => {
  try {
    await updateQuiz(quizData.id, quizData);
    showEditQuiz.value = false;
    selectedQuiz.value = null;
    await loadQuizzes();
  } catch (error) {
    console.error('Error updating quiz:', error);
    alert('Error updating quiz: ' + error);
  }
};

onMounted(() => {
  loadQuizzes();
  loadChapters();
});
</script>

<style scoped>
.quiz-management-section {
  padding: 2rem;
  background: linear-gradient(135deg, #e0e7ff 0%, #f5f5f5 100%);
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(44, 62, 80, 0.10);
  margin-top: 2rem;
}

h2 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 2rem;
  font-size: 1.7rem;
  font-weight: 700;
}

.quiz-cards-container {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
  justify-content: center;
  margin-bottom: 2rem;
}

.quiz-card {
  flex: 1;
  min-width: 300px;
  max-width: 45%;
  background: #fff;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 24px rgba(44, 62, 80, 0.10);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  border: 1px solid #e0e7ff;
}

.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e0e7ff;
  margin-bottom: 1rem;
}

.quiz-header h3 {
  color: #2c3e50;
  margin: 0;
  font-size: 1.4rem;
  font-weight: 700;
  flex: 1;
}

.quiz-actions-header {
  display: flex;
  gap: 0.5rem;
}

.edit-quiz-btn,
.delete-quiz-btn-header {
  background: none;
  border: none;
  font-size: 0.9rem;
  cursor: pointer;
  padding: 0.5rem 0.8rem;
  border-radius: 6px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
}

.edit-quiz-btn:hover {
  background: #e0e7ff;
  transform: scale(1.05);
  color: #42b983;
}

.delete-quiz-btn-header:hover {
  background: #ffe0e0;
  transform: scale(1.05);
  color: #e74c3c;
}

.quiz-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0.5rem 0 1rem 0;
  padding: 0.5rem 0;
  font-size: 0.9rem;
  color: #666;
}

.question-count {
  background: linear-gradient(90deg, #42b983 20%, #4f8cff 100%);
  color: white;
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-weight: 500;
  font-size: 0.8rem;
}

.quiz-duration {
  background: #f0f0f0;
  color: #555;
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-weight: 500;
  font-size: 0.8rem;
}

.table-container {
  overflow-x: auto;
}

.quiz-card table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
}

.quiz-card th,
.quiz-card td {
  padding: 0.8rem;
  text-align: left;
  border-bottom: 1px solid #e0e7ff;
}

.quiz-card th {
  background: linear-gradient(90deg, #e0e7ff 0%, #f5f5f5 100%);
  color: #2c3e50;
  font-weight: 600;
  font-size: 0.9rem;
}

.quiz-card td {
  color: #555;
  font-size: 0.9rem;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.quiz-card td:nth-child(3) {
  max-width: 300px;
  white-space: normal;
  word-wrap: break-word;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.edit-btn, .delete-btn {
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.edit-btn {
  background: linear-gradient(90deg, #42b983 60%, #4f8cff 100%);
  color: white;
}

.edit-btn:hover {
  background: linear-gradient(90deg, #4f8cff 60%, #42b983 100%);
  box-shadow: 0 2px 8px rgba(66, 185, 131, 0.3);
}

.delete-btn {
  background: #e74c3c;
  color: white;
}

.delete-btn:hover {
  background: #c0392b;
  box-shadow: 0 2px 8px rgba(231, 76, 60, 0.3);
}

.quiz-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 1rem;
}

.add-question-btn {
  background: linear-gradient(90deg, #42b983 60%, #4f8cff 100%);
  color: #fff;
  font-weight: 600;
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(79, 140, 255, 0.13);
  transition: background 0.2s, box-shadow 0.2s;
}



.add-question-btn:hover {
  background: linear-gradient(90deg, #4f8cff 60%, #42b983 100%);
  box-shadow: 0 4px 16px rgba(66, 185, 131, 0.18);
}

.new-quiz-btn {
  display: block;
  margin: 0 auto;
  background: linear-gradient(90deg, #42b983 60%, #4f8cff 100%);
  color: #fff;
  font-weight: 600;
  padding: 1rem 2rem;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(79, 140, 255, 0.13);
  transition: background 0.2s, box-shadow 0.2s;
}

.new-quiz-btn:hover {
  background: linear-gradient(90deg, #4f8cff 60%, #42b983 100%);
  box-shadow: 0 4px 16px rgba(66, 185, 131, 0.18);
}
</style>