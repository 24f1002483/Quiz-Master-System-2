<template>
  <div class="admin-dashboard">
    <main class="dashboard-content">
      

      <!-- Subject Management Section -->
      <section class="subjects-section">
        <h2>📚 Subject Management</h2>
        <p class="section-description">Manage subjects and their chapters</p>
        
        <!-- Debug info -->
        <div v-if="subjects.length === 0" class="debug-info">
          <p>No subjects found. Click "Add Subject" to create your first subject.</p>
          <p>Debug: Subjects array length: {{ subjects.length }}</p>
        </div>
        
        <div class="subjects-grid" v-if="subjects.length > 0">
          <div class="subject-row" v-for="row in subjectRows" :key="row[0]?.id">
            <SubjectCard
              v-for="subject in row"
              :key="subject.id"
              :subject="subject"
              @add-chapter="openAddChapterModal"
              @edit-chapter="openEditChapterModal"
              @delete-chapter="deleteChapter"
              @edit="editSubject"
              @delete="deleteSubject"
            />
          </div>
        </div>
        
        <div class="subject-actions">
          <button class="add-subject-btn" @click="showAddSubject = true">+ Add Subject</button>
        </div>
      </section>
    </main>

    <!-- Modals -->
    <NewSubjectModal v-if="showAddSubject" @save="addSubject" @cancel="showAddSubject = false" />
    <NewChapterModal v-if="showAddChapter" @save="addChapter" @cancel="showAddChapter = false" />
    <EditChapterModal v-if="showEditChapter" :modelValue="selectedChapter" @save="updateChapter" @cancel="showEditChapter = false" />
    <EditSubjectModal v-if="showEditSubject" :subject="selectedSubject" @save="updateSubjectData" @cancel="showEditSubject = false" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import { Chart } from 'chart.js/auto';
import SubjectCard from './SubjectCard.vue';
import NewSubjectModal from './NewSubjectModal.vue';
import NewChapterModal from './NewChapterModal.vue';
import EditChapterModal from './EditChapterModal.vue';
import EditSubjectModal from './EditSubjectModal.vue';
import { logoutUser } from '../services/authService.js';
import { fetchSubjects, createSubject, updateSubject, deleteSubject as deleteSubjectApi } from '../services/subjectService.js';
import { createChapter, updateChapter as updateChapterApi, deleteChapter as deleteChapterApi } from '../services/chapterService.js';
import api from '../services/axiosConfig.js';

const subjects = ref([]);
const showAddSubject = ref(false);
const showAddChapter = ref(false);
const showEditChapter = ref(false);
const showEditSubject = ref(false);
const selectedSubjectId = ref(null);
const selectedChapter = ref(null);
const selectedSubject = ref(null);

// Analytics data
const systemStats = ref({
  totalSubjects: 0,
  totalChapters: 0,
  totalQuizzes: 0,
  totalUsers: 0
});

// Chart refs
const subjectChart = ref(null);
const quizPerformanceChart = ref(null);
const userActivityChart = ref(null);

// Chart instances
let subjectChartInstance = null;
let quizPerformanceChartInstance = null;
let userActivityChartInstance = null;

// Subject and chapter management

async function loadSubjects() {
  try {
    console.log('Loading subjects...');
    // Each subject should have a 'quizzes' array for SubjectCard
    subjects.value = await fetchSubjects();
    console.log('Subjects loaded:', subjects.value);
    
    // Update system stats
    await loadSystemStats();
    await createAnalyticsCharts();
  } catch (error) {
    console.error('Error loading subjects:', error);
    alert('Failed to load subjects: ' + error.message);
  }
}

// Analytics functions
const loadSystemStats = async () => {
  try {
    // Calculate stats from subjects data
    const totalSubjects = subjects.value.length;
    const totalChapters = subjects.value.reduce((sum, subject) => 
      sum + (subject.chapters ? subject.chapters.length : 0), 0);
    const totalQuizzes = subjects.value.reduce((sum, subject) => 
      sum + (subject.chapters ? subject.chapters.reduce((chapSum, chapter) => 
        chapSum + (chapter.quizzes ? chapter.quizzes.length : 0), 0) : 0), 0);
    
    // Get user count from API
    try {
      const response = await api.get('/api/users/count');
      const totalUsers = response.data.count || 0;
      systemStats.value = {
        totalSubjects,
        totalChapters,
        totalQuizzes,
        totalUsers
      };
    } catch (error) {
      systemStats.value = {
        totalSubjects,
        totalChapters,
        totalQuizzes,
        totalUsers: 0
      };
    }
  } catch (error) {
    console.error('Failed to load system stats:', error);
  }
};

const createAnalyticsCharts = async () => {
  await Promise.all([
    createSubjectChart(),
    createQuizPerformanceChart(),
    createUserActivityChart()
  ]);
};

const createSubjectChart = async () => {
  try {
    await nextTick();
    
    if (subjectChart.value) {
      // Destroy existing chart if it exists
      if (subjectChartInstance) {
        subjectChartInstance.destroy();
      }
      
      const ctx = subjectChart.value.getContext('2d');
      
      // Prepare chart data from subjects
      const labels = subjects.value.map(subject => subject.name);
      const chapterCounts = subjects.value.map(subject => 
        subject.chapters ? subject.chapters.length : 0);
      
      if (labels.length === 0) {
        // Create empty chart with axes
        subjectChartInstance = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: ['No Data'],
            datasets: [{
              label: 'Chapters',
              data: [0],
              backgroundColor: 'rgba(200, 200, 200, 0.5)',
              borderColor: 'rgba(200, 200, 200, 1)',
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Chapters'
                }
              },
              x: {
                title: {
                  display: true,
                  text: 'Subject'
                }
              }
            },
            plugins: {
              legend: {
                display: false
              }
            }
          }
        });
      } else {
        // Create chart with data
        subjectChartInstance = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: labels,
            datasets: [{
              label: 'Chapters',
              data: chapterCounts,
              backgroundColor: 'rgba(54, 162, 235, 0.8)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Chapters'
                }
              },
              x: {
                title: {
                  display: true,
                  text: 'Subject'
                }
              }
            },
            plugins: {
              legend: {
                display: false
              }
            }
          }
        });
      }
    }
  } catch (error) {
    console.error('Failed to create subject chart:', error);
  }
};

const createQuizPerformanceChart = async () => {
  try {
    await nextTick();
    
    if (quizPerformanceChart.value) {
      // Destroy existing chart if it exists
      if (quizPerformanceChartInstance) {
        quizPerformanceChartInstance.destroy();
      }
      
      const ctx = quizPerformanceChart.value.getContext('2d');
      
      // Get quiz performance data from API
      try {
        const response = await api.get('/api/quiz-performance-data');
        const data = response.data.slice(0, 8); // Show top 8 quizzes
        
        if (data.length === 0) {
          // Create empty chart with axes
          quizPerformanceChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
              labels: ['No Data'],
              datasets: [{
                label: 'Average Score (%)',
                data: [0],
                borderColor: 'rgba(200, 200, 200, 1)',
                backgroundColor: 'rgba(200, 200, 200, 0.2)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                y: {
                  beginAtZero: true,
                  max: 100,
                  title: {
                    display: true,
                    text: 'Score (%)'
                  }
                },
                x: {
                  title: {
                    display: true,
                    text: 'Quiz'
                  }
                }
              },
              plugins: {
                legend: {
                  display: false
                }
              }
            }
          });
        } else {
          // Create chart with data
          const labels = data.map(d => d.title.substring(0, 12) + (d.title.length > 12 ? '...' : ''));
          const scores = data.map(d => d.avg_score);
          
          quizPerformanceChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
              labels: labels,
              datasets: [{
                label: 'Average Score (%)',
                data: scores,
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                y: {
                  beginAtZero: true,
                  max: 100,
                  title: {
                    display: true,
                    text: 'Score (%)'
                  }
                },
                x: {
                  title: {
                    display: true,
                    text: 'Quiz'
                  }
                }
              },
              plugins: {
                legend: {
                  display: false
                }
              }
            }
          });
        }
      } catch (error) {
        // Create empty chart if API fails
        quizPerformanceChartInstance = new Chart(ctx, {
          type: 'line',
          data: {
            labels: ['No Data'],
            datasets: [{
              label: 'Average Score (%)',
              data: [0],
              borderColor: 'rgba(200, 200, 200, 1)',
              backgroundColor: 'rgba(200, 200, 200, 0.2)',
              borderWidth: 2,
              fill: true,
              tension: 0.4
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true,
                max: 100,
                title: {
                  display: true,
                  text: 'Score (%)'
                }
              },
              x: {
                title: {
                  display: true,
                  text: 'Quiz'
                }
              }
            },
            plugins: {
              legend: {
                display: false
              }
            }
          }
        });
      }
    }
  } catch (error) {
    console.error('Failed to create quiz performance chart:', error);
  }
};

const createUserActivityChart = async () => {
  try {
    await nextTick();
    
    if (userActivityChart.value) {
      // Destroy existing chart if it exists
      if (userActivityChartInstance) {
        userActivityChartInstance.destroy();
      }
      
      const ctx = userActivityChart.value.getContext('2d');
      
      // Get daily activity data from API
      try {
        const response = await api.get('/api/daily-activity');
        const data = response.data.slice(-14); // Show last 14 days
        
        if (data.length === 0 || data.every(d => d.count === 0)) {
          // Create empty chart with axes
          userActivityChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
              labels: ['No Data'],
              datasets: [{
                label: 'Activity',
                data: [0],
                backgroundColor: 'rgba(200, 200, 200, 0.5)',
                borderColor: 'rgba(200, 200, 200, 1)',
                borderWidth: 1
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                y: {
                  beginAtZero: true,
                  title: {
                    display: true,
                    text: 'Activity'
                  }
                },
                x: {
                  title: {
                    display: true,
                    text: 'Date'
                  }
                }
              },
              plugins: {
                legend: {
                  display: false
                }
              }
            }
          });
        } else {
          // Create chart with data
          const labels = data.map(d => {
            const date = new Date(d.date);
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
          });
          const counts = data.map(d => d.count);
          
          userActivityChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
              labels: labels,
              datasets: [{
                label: 'Activity',
                data: counts,
                backgroundColor: 'rgba(255, 159, 64, 0.8)',
                borderColor: 'rgba(255, 159, 64, 1)',
                borderWidth: 1
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                y: {
                  beginAtZero: true,
                  title: {
                    display: true,
                    text: 'Activity'
                  }
                },
                x: {
                  title: {
                    display: true,
                    text: 'Date'
                  }
                }
              },
              plugins: {
                legend: {
                  display: false
                }
              }
            }
          });
        }
      } catch (error) {
        // Create empty chart if API fails
        userActivityChartInstance = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: ['No Data'],
            datasets: [{
              label: 'Activity',
              data: [0],
              backgroundColor: 'rgba(200, 200, 200, 0.5)',
              borderColor: 'rgba(200, 200, 200, 1)',
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Activity'
                }
              },
              x: {
                title: {
                  display: true,
                  text: 'Date'
                }
              }
            },
            plugins: {
              legend: {
                display: false
              }
            }
          }
        });
      }
    }
  } catch (error) {
    console.error('Failed to create user activity chart:', error);
  }
};

onMounted(() => {
  loadSubjects();
});

// Group subjects into rows of 2 for the grid
const subjectRows = computed(() => {
  const rows = [];
  for (let i = 0; i < subjects.value.length; i += 3) {
    rows.push(subjects.value.slice(i, i + 3));
  }
  return rows;
});

const addSubject = async (subject) => {
  try {
    console.log('Adding subject:', subject);
    await createSubject(subject);
    showAddSubject.value = false;
    await loadSubjects();
    console.log('Subject added successfully');
  } catch (error) {
    console.error('Error adding subject:', error);
    alert('Failed to add subject: ' + error.message);
  }
};

const deleteSubject = async (id) => {
  await deleteSubjectApi(id);
  await loadSubjects();
};

const editSubject = async (subject) => {
  selectedSubject.value = subject;
  showEditSubject.value = true;
};

const updateSubjectData = async (subjectData) => {
  try {
    await updateSubject(selectedSubject.value.id, subjectData);
    showEditSubject.value = false;
    await loadSubjects();
    console.log('Subject updated successfully');
  } catch (error) {
    console.error('Error updating subject:', error);
    alert('Failed to update subject: ' + error.message);
  }
};

const openAddChapterModal = (subject) => {
  if (!subject || !subject.id) {
    alert('No subject selected. Please select a valid subject to add a chapter.');
    return;
  }
  selectedSubjectId.value = subject.id;
  showAddChapter.value = true;
};

const addChapter = async (chapter) => {
  if (!selectedSubjectId.value) {
    alert('No subject selected. Cannot create chapter without subject_id.');
    return;
  }
  try {
    console.log('Adding chapter:', chapter, 'to subject:', selectedSubjectId.value);
    const chapterData = {
      ...chapter,
      subject_id: selectedSubjectId.value
    };
    await createChapter(chapterData);
    showAddChapter.value = false;
    await loadSubjects();
    console.log('Chapter added successfully');
  } catch (error) {
    console.error('Error creating chapter:', error);
    alert('Error creating chapter: ' + error.message);
  }
};

const openEditChapterModal = (chapter) => {
  console.log('openEditChapterModal called with:', chapter);
  selectedChapter.value = { ...chapter };
  showEditChapter.value = true;
  console.log('Modal should be visible:', showEditChapter.value);
};

const updateChapter = async (chapter) => {
  try {
    await updateChapterApi(selectedChapter.value.id, chapter);
    showEditChapter.value = false;
    await loadSubjects();
  } catch (error) {
    alert('Error updating chapter: ' + error);
  }
};

const deleteChapter = async (chapterId) => {
  if (confirm('Are you sure you want to delete this chapter? This action cannot be undone.')) {
    try {
      await deleteChapterApi(chapterId);
      await loadSubjects();
    } catch (error) {
      alert('Error deleting chapter: ' + error);
    }
  }
};

// Load subjects on mount
onMounted(async () => {
  await loadSubjects();
});
</script>

<style scoped>
.admin-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #e3f0ff 0%, #f9f9ff 100%);
  padding: 2rem 0;
}

.dashboard-content { 
  display: flex; 
  flex-direction: column; 
  gap: 2rem; 
  padding: 2rem; 
}

/* Analytics Section Styles */
.analytics-section {
  background: #fff;
  padding: 2rem;
  border-radius: 16px;
  margin-bottom: 2rem;
  box-shadow: 0 2px 12px rgba(44, 62, 80, 0.06);
}

.analytics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.analytics-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
}

.analytics-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.analytics-card h3 {
  color: #333;
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.stat-item {
  text-align: center;
  padding: 1rem;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.stat-number {
  display: block;
  font-size: 1.5rem;
  font-weight: bold;
  color: #007bff;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
}

.chart-container {
  background: #fff;
  border-radius: 8px;
  padding: 1rem;
  border: 1px solid #dee2e6;
  text-align: center;
  height: 250px;
}

/* Subject Management Section */
.subjects-section {
  background: #fff;
  padding: 2rem;
  border-radius: 16px;
  margin-bottom: 2rem;
  box-shadow: 0 2px 12px rgba(44, 62, 80, 0.06);
}

.section-description {
  color: #666;
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
}

.subjects-grid { 
  display: flex; 
  flex-direction: column; 
  gap: 2rem; 
}

.subject-row {
  display: flex;
  gap: 2rem;
  justify-content: space-between;
}

.subject-card {
  flex: 1 1 0;
  min-width: 0;
  max-width: 33%;
  box-sizing: border-box;
  background: #f9f9ff;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 0;
  display: flex;
  flex-direction: column;
}

.add-subject-btn {
  background: #28a745;
  color: white;
  border-radius: 6px;
  border: none;
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}

.add-subject-btn:hover {
  background: #218838;
}

.refresh-subjects-btn {
  background: #17a2b8;
  color: white;
  border-radius: 6px;
  border: none;
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  cursor: pointer;
  margin-left: 1rem;
  transition: background-color 0.3s;
}

.refresh-subjects-btn:hover {
  background: #138496;
}

.subject-actions {
  margin-top: 1.5rem;
  display: flex;
  gap: 1rem;
  align-items: center;
}

.debug-info {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  text-align: center;
}

.debug-info p {
  margin: 0.5rem 0;
  color: #666;
}

a { 
  color: #1ca01c; 
  text-decoration: underline; 
  cursor: pointer; 
}

@media (max-width: 768px) {
  .analytics-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .subject-row {
    flex-direction: column;
  }
  
  .subject-card {
    max-width: 100%;
  }
}
</style>