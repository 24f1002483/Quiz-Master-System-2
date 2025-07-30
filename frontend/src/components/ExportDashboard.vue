<template>
  <div class="export-dashboard">
    <main class="dashboard-content">
      <!-- Analytics Section -->
      <section class="analytics-section">
        <h2>📊 Export Analytics</h2>
        <p class="section-description">Visualize export patterns and data trends</p>
        
        <div class="analytics-grid">
          <!-- Export Statistics -->
          <div class="analytics-card">
            <h3>📈 Export Statistics</h3>
            <div class="stats-grid">
              <div class="stat-item">
                <span class="stat-number">{{ exportStats.totalExports }}</span>
                <span class="stat-label">Total Exports</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">{{ exportStats.thisMonth }}</span>
                <span class="stat-label">This Month</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">{{ exportStats.totalSize }}</span>
                <span class="stat-label">Total Size</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">{{ exportStats.avgSize }}</span>
                <span class="stat-label">Avg Size</span>
              </div>
            </div>
          </div>

          <!-- Export Type Distribution -->
          <div class="analytics-card">
            <h3>📊 Export Types</h3>
            <div class="chart-container">
              <canvas ref="exportTypeChart" width="400" height="200"></canvas>
            </div>
          </div>

          <!-- Monthly Export Trend -->
          <div class="analytics-card">
            <h3>📅 Monthly Trend</h3>
            <div class="chart-container">
              <canvas ref="monthlyTrendChart" width="400" height="200"></canvas>
            </div>
          </div>

          <!-- File Size Distribution -->
          <div class="analytics-card">
            <h3>📦 File Size Distribution</h3>
            <div class="chart-container">
              <canvas ref="fileSizeChart" width="400" height="200"></canvas>
            </div>
          </div>
        </div>
      </section>

      <!-- Export Section -->
      <section class="export-section">
        <h2>📊 Data Export</h2>
        <p class="section-description">Export quiz data and analytics for analysis</p>
        
        <div class="export-grid">
          <!-- User Performance Export -->
          <div class="export-card">
            <h3>👥 User Performance</h3>
            <p>Export comprehensive user performance data with filtering options</p>
            
            <div class="export-filters" v-if="showUserPerformanceFilters">
              <div class="filter-group">
                <label>Date From:</label>
                <input type="datetime-local" v-model="userPerformanceFilters.dateFrom">
              </div>
              <div class="filter-group">
                <label>Date To:</label>
                <input type="datetime-local" v-model="userPerformanceFilters.dateTo">
              </div>
              <div class="filter-group">
                <label>Status:</label>
                <select v-model="userPerformanceFilters.status">
                  <option value="">All</option>
                  <option value="completed">Completed</option>
                  <option value="in_progress">In Progress</option>
                </select>
              </div>
            </div>
            
            <div class="export-actions">
              <select v-model="userPerformanceFormat" class="format-selector">
                <option value="csv">CSV</option>
                <option value="excel">Excel</option>
              </select>
              <button 
                @click="exportUserPerformance" 
                :disabled="userPerformanceLoading"
                class="export-btn"
              >
                <span v-if="userPerformanceLoading">⏳ Processing...</span>
                <span v-else>📊 Export User Performance</span>
              </button>
              <button 
                @click="showUserPerformanceFilters = !showUserPerformanceFilters"
                class="filter-toggle-btn"
              >
                {{ showUserPerformanceFilters ? 'Hide' : 'Show' }} Filters
              </button>
            </div>
            
            <!-- Export Status -->
            <div v-if="userPerformanceTaskId" class="export-status">
              <div class="status-indicator">
                <span v-if="userPerformanceStatus === 'processing'" class="processing">⏳ Processing...</span>
                <span v-else-if="userPerformanceStatus === 'completed'" class="completed">✅ Completed</span>
                <span v-else-if="userPerformanceStatus === 'failed'" class="failed">❌ Failed</span>
              </div>
              <button 
                v-if="userPerformanceStatus === 'completed' && userPerformanceResult" 
                @click="downloadFile(userPerformanceResult.filename)"
                class="download-btn"
              >
                📁 Download {{ userPerformanceResult.filename }}
              </button>
            </div>
          </div>

          <!-- Quiz Analytics Export -->
          <div class="export-card">
            <h3>📈 Quiz Analytics</h3>
            <p>Export detailed question-level analytics and response data</p>
            
            <div class="export-filters" v-if="showQuizAnalyticsFilters">
              <div class="filter-group">
                <label>Quiz ID (Optional):</label>
                <input type="number" v-model="quizAnalyticsFilters.quizId" placeholder="Leave empty for all quizzes">
              </div>
            </div>
            
            <div class="export-actions">
              <select v-model="quizAnalyticsFormat" class="format-selector">
                <option value="csv">CSV</option>
                <option value="excel">Excel</option>
              </select>
              <button 
                @click="exportQuizAnalytics" 
                :disabled="quizAnalyticsLoading"
                class="export-btn"
              >
                <span v-if="quizAnalyticsLoading">⏳ Processing...</span>
                <span v-else>📈 Export Quiz Analytics</span>
              </button>
              <button 
                @click="showQuizAnalyticsFilters = !showQuizAnalyticsFilters"
                class="filter-toggle-btn"
              >
                {{ showQuizAnalyticsFilters ? 'Hide' : 'Show' }} Filters
              </button>
            </div>
            
            <!-- Export Status -->
            <div v-if="quizAnalyticsTaskId" class="export-status">
              <div class="status-indicator">
                <span v-if="quizAnalyticsStatus === 'processing'" class="processing">⏳ Processing...</span>
                <span v-else-if="quizAnalyticsStatus === 'completed'" class="completed">✅ Completed</span>
                <span v-else-if="quizAnalyticsStatus === 'failed'" class="failed">❌ Failed</span>
              </div>
              <button 
                v-if="quizAnalyticsStatus === 'completed' && quizAnalyticsResult" 
                @click="downloadFile(quizAnalyticsResult.filename)"
                class="download-btn"
              >
                📁 Download {{ quizAnalyticsResult.filename }}
              </button>
            </div>
          </div>

          <!-- Export History -->
          <div class="export-card">
            <h3>📚 Export History</h3>
            <p>View and manage your previous export files</p>
            
            <button @click="loadExportHistory" class="refresh-btn">🔄 Refresh</button>
            
            <div v-if="exportHistory.length === 0" class="no-exports">
              No exports found
            </div>
            <div v-else class="export-list">
              <div 
                v-for="exportItem in exportHistory" 
                :key="exportItem.filename" 
                class="export-item"
              >
                <div class="export-info">
                  <span class="filename">{{ exportItem.filename }}</span>
                  <span class="size">{{ formatFileSize(exportItem.size) }}</span>
                  <span class="date">{{ formatDate(exportItem.created) }}</span>
                </div>
                <div class="export-item-actions">
                  <button @click="downloadFile(exportItem.filename)" class="action-btn">
                    📥 Download
                  </button>
                  <button @click="deleteFile(exportItem.filename)" class="action-btn delete">
                    🗑️ Delete
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { Chart } from 'chart.js/auto';
import api from '../services/axiosConfig.js';

// Export functionality
const userPerformanceFormat = ref('csv');
const quizAnalyticsFormat = ref('csv');
const userPerformanceLoading = ref(false);
const quizAnalyticsLoading = ref(false);
const userPerformanceTaskId = ref(null);
const quizAnalyticsTaskId = ref(null);
const userPerformanceStatus = ref('');
const quizAnalyticsStatus = ref('');
const userPerformanceResult = ref(null);
const quizAnalyticsResult = ref(null);
const showUserPerformanceFilters = ref(false);
const showQuizAnalyticsFilters = ref(false);
const exportHistory = ref([]);

// Analytics data
const exportStats = ref({
  totalExports: 0,
  thisMonth: 0,
  totalSize: '0 KB',
  avgSize: '0 KB'
});

// Chart refs
const exportTypeChart = ref(null);
const monthlyTrendChart = ref(null);
const fileSizeChart = ref(null);

// Chart instances
let exportTypeChartInstance = null;
let monthlyTrendChartInstance = null;
let fileSizeChartInstance = null;

const userPerformanceFilters = ref({
  dateFrom: '',
  dateTo: '',
  status: ''
});

const quizAnalyticsFilters = ref({
  quizId: null
});

// Analytics functions
const loadExportStats = async () => {
  try {
    // Calculate stats from export history
    const totalExports = exportHistory.value.length;
    const now = new Date();
    const thisMonth = exportHistory.value.filter(item => {
      const itemDate = new Date(item.created);
      return itemDate.getMonth() === now.getMonth() && 
             itemDate.getFullYear() === now.getFullYear();
    }).length;
    
    const totalSize = exportHistory.value.reduce((sum, item) => sum + (item.size || 0), 0);
    const avgSize = totalExports > 0 ? totalSize / totalExports : 0;
    
    exportStats.value = {
      totalExports,
      thisMonth,
      totalSize: formatFileSize(totalSize),
      avgSize: formatFileSize(avgSize)
    };
  } catch (error) {
    console.error('Failed to load export stats:', error);
  }
};

const createExportTypeChart = async () => {
  try {
    await nextTick();
    
    if (exportTypeChart.value) {
      // Destroy existing chart if it exists
      if (exportTypeChartInstance) {
        exportTypeChartInstance.destroy();
      }
      
      const ctx = exportTypeChart.value.getContext('2d');
      
      // Analyze export types from history
      const typeCounts = {};
      exportHistory.value.forEach(item => {
        const type = item.filename.split('.').pop() || 'unknown';
        typeCounts[type] = (typeCounts[type] || 0) + 1;
      });
      
      const labels = Object.keys(typeCounts);
      const data = Object.values(typeCounts);
      
      if (labels.length === 0) {
        // Create empty chart with axes
        exportTypeChartInstance = new Chart(ctx, {
          type: 'doughnut',
          data: {
            labels: ['No Data'],
            datasets: [{
              data: [1],
              backgroundColor: ['rgba(200, 200, 200, 0.5)'],
              borderWidth: 2,
              borderColor: '#fff'
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'bottom'
              }
            }
          }
        });
      } else {
        // Create chart with data
        const colors = [
          'rgba(255, 99, 132, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 205, 86, 0.8)',
          'rgba(75, 192, 192, 0.8)',
          'rgba(153, 102, 255, 0.8)'
        ];
        
        exportTypeChartInstance = new Chart(ctx, {
          type: 'doughnut',
          data: {
            labels: labels,
            datasets: [{
              data: data,
              backgroundColor: colors.slice(0, labels.length),
              borderWidth: 2,
              borderColor: '#fff'
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'bottom'
              }
            }
          }
        });
      }
    }
  } catch (error) {
    console.error('Failed to create export type chart:', error);
  }
};

const createMonthlyTrendChart = async () => {
  try {
    await nextTick();
    
    if (monthlyTrendChart.value) {
      // Destroy existing chart if it exists
      if (monthlyTrendChartInstance) {
        monthlyTrendChartInstance.destroy();
      }
      
      const ctx = monthlyTrendChart.value.getContext('2d');
      
      // Group exports by month
      const monthlyData = {};
      exportHistory.value.forEach(item => {
        const date = new Date(item.created);
        const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
        monthlyData[monthKey] = (monthlyData[monthKey] || 0) + 1;
      });
      
      const labels = Object.keys(monthlyData).sort();
      const data = labels.map(key => monthlyData[key]);
      
      if (labels.length === 0) {
        // Create empty chart with axes
        monthlyTrendChartInstance = new Chart(ctx, {
          type: 'line',
          data: {
            labels: ['No Data'],
            datasets: [{
              label: 'Exports',
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
                title: {
                  display: true,
                  text: 'Exports'
                }
              },
              x: {
                title: {
                  display: true,
                  text: 'Month'
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
        monthlyTrendChartInstance = new Chart(ctx, {
          type: 'line',
          data: {
            labels: labels.map(label => {
              const [year, month] = label.split('-');
              return `${month}/${year}`;
            }),
            datasets: [{
              label: 'Exports',
              data: data,
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
                title: {
                  display: true,
                  text: 'Exports'
                }
              },
              x: {
                title: {
                  display: true,
                  text: 'Month'
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
    console.error('Failed to create monthly trend chart:', error);
  }
};

const createFileSizeChart = async () => {
  try {
    await nextTick();
    
    if (fileSizeChart.value) {
      // Destroy existing chart if it exists
      if (fileSizeChartInstance) {
        fileSizeChartInstance.destroy();
      }
      
      const ctx = fileSizeChart.value.getContext('2d');
      
      // Create size distribution
      const sizeRanges = {
        '0-1KB': 0,
        '1-10KB': 0,
        '10-100KB': 0,
        '100KB-1MB': 0,
        '1MB+': 0
      };
      
      exportHistory.value.forEach(item => {
        const sizeKB = (item.size || 0) / 1024;
        if (sizeKB < 1) sizeRanges['0-1KB']++;
        else if (sizeKB < 10) sizeRanges['1-10KB']++;
        else if (sizeKB < 100) sizeRanges['10-100KB']++;
        else if (sizeKB < 1024) sizeRanges['100KB-1MB']++;
        else sizeRanges['1MB+']++;
      });
      
      const labels = Object.keys(sizeRanges);
      const data = Object.values(sizeRanges);
      
      if (data.every(val => val === 0)) {
        // Create empty chart with axes
        fileSizeChartInstance = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: ['No Data'],
            datasets: [{
              label: 'Files',
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
                  text: 'Files'
                }
              },
              x: {
                title: {
                  display: true,
                  text: 'Size Range'
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
        fileSizeChartInstance = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: labels,
            datasets: [{
              label: 'Files',
              data: data,
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
                  text: 'Files'
                }
              },
              x: {
                title: {
                  display: true,
                  text: 'Size Range'
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
    console.error('Failed to create file size chart:', error);
  }
};

// Export functions
const exportUserPerformance = async () => {
  userPerformanceLoading.value = true;
  try {
    const filters = {};
    if (userPerformanceFilters.value.dateFrom) {
      filters.date_from = new Date(userPerformanceFilters.value.dateFrom).toISOString();
    }
    if (userPerformanceFilters.value.dateTo) {
      filters.date_to = new Date(userPerformanceFilters.value.dateTo).toISOString();
    }
    if (userPerformanceFilters.value.status) {
      filters.status = userPerformanceFilters.value.status;
    }

    const response = await api.post('/api/export/user-performance', {
      format: userPerformanceFormat.value,
      filters: filters
    });
    
    userPerformanceTaskId.value = response.data.task_id;
    userPerformanceStatus.value = 'processing';
    startStatusPolling('userPerformance');
    
  } catch (error) {
    console.error('Export failed:', error);
    alert('Export failed: ' + (error.response?.data?.error || 'Unknown error'));
  } finally {
    userPerformanceLoading.value = false;
  }
};

const exportQuizAnalytics = async () => {
  quizAnalyticsLoading.value = true;
  try {
    const response = await api.post('/api/export/quiz-analytics', {
      format: quizAnalyticsFormat.value,
      quiz_id: quizAnalyticsFilters.value.quizId || null
    });
    
    quizAnalyticsTaskId.value = response.data.task_id;
    quizAnalyticsStatus.value = 'processing';
    startStatusPolling('quizAnalytics');
    
  } catch (error) {
    console.error('Export failed:', error);
    alert('Export failed: ' + (error.response?.data?.error || 'Unknown error'));
  } finally {
    quizAnalyticsLoading.value = false;
  }
};

const startStatusPolling = (type) => {
  const taskId = type === 'userPerformance' ? userPerformanceTaskId.value : quizAnalyticsTaskId.value;
  if (!taskId) return;

  const interval = setInterval(async () => {
    try {
      const response = await api.get(`/api/export/status/${taskId}`);
      const status = response.data.state;
      
      if (type === 'userPerformance') {
        userPerformanceStatus.value = status === 'SUCCESS' ? 'completed' : 
                                     status === 'FAILURE' ? 'failed' : 'processing';
        
        if (status === 'SUCCESS') {
          userPerformanceResult.value = response.data.result;
          clearInterval(interval);
          loadExportHistory();
          alert('Export completed successfully!');
        } else if (status === 'FAILURE') {
          clearInterval(interval);
          alert('Export failed: ' + response.data.status);
        }
      } else {
        quizAnalyticsStatus.value = status === 'SUCCESS' ? 'completed' : 
                                   status === 'FAILURE' ? 'failed' : 'processing';
        
        if (status === 'SUCCESS') {
          quizAnalyticsResult.value = response.data.result;
          clearInterval(interval);
          loadExportHistory();
          alert('Export completed successfully!');
        } else if (status === 'FAILURE') {
          clearInterval(interval);
          alert('Export failed: ' + response.data.status);
        }
      }
    } catch (error) {
      console.error('Status check failed:', error);
      clearInterval(interval);
    }
  }, 2000);
};

const downloadFile = async (filename) => {
  try {
    const response = await api.get(`/api/export/download/${filename}`, {
      responseType: 'blob'
    });
    
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    
    alert('File downloaded successfully!');
  } catch (error) {
    console.error('Download failed:', error);
    alert('Download failed: ' + (error.response?.data?.error || 'Unknown error'));
  }
};

const loadExportHistory = async () => {
  try {
    const response = await api.get('/api/export/list');
    exportHistory.value = response.data.exports;
    
    // Update analytics after loading history
    await loadExportStats();
    await Promise.all([
      createExportTypeChart(),
      createMonthlyTrendChart(),
      createFileSizeChart()
    ]);
  } catch (error) {
    console.error('Failed to load export history:', error);
  }
};

const deleteFile = async (filename) => {
  if (!confirm('Are you sure you want to delete this export file?')) {
    return;
  }
  
  try {
    await api.delete(`/api/export/delete/${filename}`);
    alert('File deleted successfully!');
    loadExportHistory();
  } catch (error) {
    console.error('Delete failed:', error);
    alert('Delete failed: ' + (error.response?.data?.error || 'Unknown error'));
  }
};

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString();
};

// Load export history on mount
onMounted(async () => {
  await loadExportHistory();
});
</script>

<style scoped>
.export-dashboard {
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

/* Export Section Styles */
.export-section {
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

.export-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.export-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
}

.export-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.export-card h3 {
  color: #333;
  margin-bottom: 0.5rem;
  font-size: 1.2rem;
}

.export-card p {
  color: #666;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.export-filters {
  background: #fff;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  border: 1px solid #dee2e6;
}

.filter-group {
  margin-bottom: 0.75rem;
}

.filter-group label {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
  color: #495057;
  font-size: 0.9rem;
}

.filter-group input,
.filter-group select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.9rem;
}

.export-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.format-selector {
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  background: #fff;
  font-size: 0.9rem;
}

.export-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s;
  font-size: 0.9rem;
}

.export-btn:hover:not(:disabled) {
  background: #0056b3;
}

.export-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.filter-toggle-btn {
  background: #6c757d;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: background-color 0.3s;
}

.filter-toggle-btn:hover {
  background: #545b62;
}

.export-status {
  margin-top: 1rem;
  padding: 1rem;
  background: #fff;
  border-radius: 6px;
  border-left: 4px solid #007bff;
}

.status-indicator {
  margin-bottom: 0.5rem;
}

.processing {
  color: #ffc107;
  font-weight: 500;
}

.completed {
  color: #28a745;
  font-weight: 500;
}

.failed {
  color: #dc3545;
  font-weight: 500;
}

.download-btn {
  background: #28a745;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: background-color 0.3s;
}

.download-btn:hover {
  background: #218838;
}

.refresh-btn {
  background: #17a2b8;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  margin-bottom: 1rem;
  transition: background-color 0.3s;
}

.refresh-btn:hover {
  background: #138496;
}

.no-exports {
  text-align: center;
  color: #666;
  font-style: italic;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 6px;
}

.export-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.export-item {
  background: #fff;
  border-radius: 6px;
  padding: 0.75rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid #dee2e6;
}

.export-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.filename {
  font-weight: 500;
  color: #333;
  font-size: 0.9rem;
}

.size {
  font-size: 0.8rem;
  color: #666;
}

.date {
  font-size: 0.8rem;
  color: #666;
}

.export-item-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.7rem;
  transition: background-color 0.3s;
}

.action-btn:hover {
  background: #0056b3;
}

.action-btn.delete {
  background: #dc3545;
}

.action-btn.delete:hover {
  background: #c82333;
}

@media (max-width: 768px) {
  .analytics-grid,
  .export-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .export-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .export-item-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style> 