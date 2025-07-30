<template>
  <div class="export-container">
    <div class="export-header">
      <h2>📊 Data Export</h2>
      <p>Export your quiz data in CSV or Excel format</p>
    </div>

    <!-- User Export Section -->
    <div class="export-section" v-if="userRole === 'user'">
      <h3>📋 My Quiz History</h3>
      <div class="export-options">
        <div class="format-selector">
          <label>Export Format:</label>
          <select v-model="userExportFormat">
            <option value="csv">CSV</option>
            <option value="excel">Excel</option>
          </select>
        </div>
        <button 
          @click="exportQuizHistory" 
          :disabled="userExportLoading"
          class="export-btn"
        >
          <span v-if="userExportLoading">⏳ Processing...</span>
          <span v-else>📥 Export Quiz History</span>
        </button>
      </div>
      
      <!-- Export Status -->
      <div v-if="userExportTaskId" class="export-status">
        <div class="status-indicator">
          <span v-if="userExportStatus === 'processing'" class="processing">⏳ Processing...</span>
          <span v-else-if="userExportStatus === 'completed'" class="completed">✅ Completed</span>
          <span v-else-if="userExportStatus === 'failed'" class="failed">❌ Failed</span>
        </div>
        <button 
          v-if="userExportStatus === 'completed' && userExportResult" 
          @click="downloadFile(userExportResult.filename)"
          class="download-btn"
        >
          📁 Download {{ userExportResult.filename }}
        </button>
      </div>
    </div>

    <!-- Admin Export Section -->
    <div class="export-section" v-if="userRole === 'admin'">
      <h3>👥 User Performance Export</h3>
      <div class="export-options">
        <div class="format-selector">
          <label>Export Format:</label>
          <select v-model="adminExportFormat">
            <option value="csv">CSV</option>
            <option value="excel">Excel</option>
          </select>
        </div>
        
        <!-- Filters -->
        <div class="filters">
          <div class="filter-group">
            <label>Date From:</label>
            <input type="datetime-local" v-model="filters.dateFrom">
          </div>
          <div class="filter-group">
            <label>Date To:</label>
            <input type="datetime-local" v-model="filters.dateTo">
          </div>
          <div class="filter-group">
            <label>Status:</label>
            <select v-model="filters.status">
              <option value="">All</option>
              <option value="completed">Completed</option>
              <option value="in_progress">In Progress</option>
            </select>
          </div>
        </div>
        
        <button 
          @click="exportUserPerformance" 
          :disabled="adminExportLoading"
          class="export-btn"
        >
          <span v-if="adminExportLoading">⏳ Processing...</span>
          <span v-else>📊 Export User Performance</span>
        </button>
      </div>
      
      <!-- Export Status -->
      <div v-if="adminExportTaskId" class="export-status">
        <div class="status-indicator">
          <span v-if="adminExportStatus === 'processing'" class="processing">⏳ Processing...</span>
          <span v-else-if="adminExportStatus === 'completed'" class="completed">✅ Completed</span>
          <span v-else-if="adminExportStatus === 'failed'" class="failed">❌ Failed</span>
        </div>
        <button 
          v-if="adminExportStatus === 'completed' && adminExportResult" 
          @click="downloadFile(adminExportResult.filename)"
          class="download-btn"
        >
          📁 Download {{ adminExportResult.filename }}
        </button>
      </div>

      <!-- Quiz Analytics Export -->
      <h3>📈 Quiz Analytics Export</h3>
      <div class="export-options">
        <div class="format-selector">
          <label>Export Format:</label>
          <select v-model="analyticsExportFormat">
            <option value="csv">CSV</option>
            <option value="excel">Excel</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Quiz ID (Optional):</label>
          <input type="number" v-model="analyticsQuizId" placeholder="Leave empty for all quizzes">
        </div>
        <button 
          @click="exportQuizAnalytics" 
          :disabled="analyticsExportLoading"
          class="export-btn"
        >
          <span v-if="analyticsExportLoading">⏳ Processing...</span>
          <span v-else>📈 Export Quiz Analytics</span>
        </button>
      </div>
      
      <!-- Analytics Export Status -->
      <div v-if="analyticsExportTaskId" class="export-status">
        <div class="status-indicator">
          <span v-if="analyticsExportStatus === 'processing'" class="processing">⏳ Processing...</span>
          <span v-else-if="analyticsExportStatus === 'completed'" class="completed">✅ Completed</span>
          <span v-else-if="analyticsExportStatus === 'failed'" class="failed">❌ Failed</span>
        </div>
        <button 
          v-if="analyticsExportStatus === 'completed' && analyticsExportResult" 
          @click="downloadFile(analyticsExportResult.filename)"
          class="download-btn"
        >
          📁 Download {{ analyticsExportResult.filename }}
        </button>
      </div>
    </div>

    <!-- Export History -->
    <div class="export-history">
      <h3>📚 Export History</h3>
      <div v-if="exportHistory.length === 0" class="no-exports">
        No exports found
      </div>
      <div v-else class="export-list">
        <div 
          v-for="export in exportHistory" 
          :key="export.filename" 
          class="export-item"
        >
          <div class="export-info">
            <span class="filename">{{ export.filename }}</span>
            <span class="size">{{ formatFileSize(export.size) }}</span>
            <span class="date">{{ formatDate(export.created) }}</span>
          </div>
          <div class="export-actions">
            <button @click="downloadFile(export.filename)" class="action-btn">
              📥 Download
            </button>
            <button @click="deleteFile(export.filename)" class="action-btn delete">
              🗑️ Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ExportComponent',
  data() {
    return {
      userRole: 'user', // This should come from your auth system
      userExportFormat: 'csv',
      adminExportFormat: 'csv',
      analyticsExportFormat: 'csv',
      userExportLoading: false,
      adminExportLoading: false,
      analyticsExportLoading: false,
      userExportTaskId: null,
      adminExportTaskId: null,
      analyticsExportTaskId: null,
      userExportStatus: '',
      adminExportStatus: '',
      analyticsExportStatus: '',
      userExportResult: null,
      adminExportResult: null,
      analyticsExportResult: null,
      filters: {
        dateFrom: '',
        dateTo: '',
        status: ''
      },
      analyticsQuizId: null,
      exportHistory: [],
      statusPolling: null
    }
  },
  mounted() {
    this.loadExportHistory()
  },
  beforeUnmount() {
    if (this.statusPolling) {
      clearInterval(this.statusPolling)
    }
  },
  methods: {
    async exportQuizHistory() {
      this.userExportLoading = true
      try {
        const response = await axios.post('/api/export/quiz-history', {
          format: this.userExportFormat
        })
        
        this.userExportTaskId = response.data.task_id
        this.userExportStatus = 'processing'
        this.startStatusPolling('user')
        
      } catch (error) {
        console.error('Export failed:', error)
        this.$toast.error('Export failed: ' + error.response?.data?.error || 'Unknown error')
      } finally {
        this.userExportLoading = false
      }
    },

    async exportUserPerformance() {
      this.adminExportLoading = true
      try {
        const filters = {}
        if (this.filters.dateFrom) {
          filters.date_from = new Date(this.filters.dateFrom).toISOString()
        }
        if (this.filters.dateTo) {
          filters.date_to = new Date(this.filters.dateTo).toISOString()
        }
        if (this.filters.status) {
          filters.status = this.filters.status
        }

        const response = await axios.post('/api/export/user-performance', {
          format: this.adminExportFormat,
          filters: filters
        })
        
        this.adminExportTaskId = response.data.task_id
        this.adminExportStatus = 'processing'
        this.startStatusPolling('admin')
        
      } catch (error) {
        console.error('Export failed:', error)
        this.$toast.error('Export failed: ' + error.response?.data?.error || 'Unknown error')
      } finally {
        this.adminExportLoading = false
      }
    },

    async exportQuizAnalytics() {
      this.analyticsExportLoading = true
      try {
        const response = await axios.post('/api/export/quiz-analytics', {
          format: this.analyticsExportFormat,
          quiz_id: this.analyticsQuizId || null
        })
        
        this.analyticsExportTaskId = response.data.task_id
        this.analyticsExportStatus = 'processing'
        this.startStatusPolling('analytics')
        
      } catch (error) {
        console.error('Export failed:', error)
        this.$toast.error('Export failed: ' + error.response?.data?.error || 'Unknown error')
      } finally {
        this.analyticsExportLoading = false
      }
    },

    startStatusPolling(type) {
      const taskId = this[`${type}ExportTaskId`]
      if (!taskId) return

      this.statusPolling = setInterval(async () => {
        try {
          const response = await axios.get(`/api/export/status/${taskId}`)
          const status = response.data.state
          
          this[`${type}ExportStatus`] = status === 'SUCCESS' ? 'completed' : 
                                       status === 'FAILURE' ? 'failed' : 'processing'
          
          if (status === 'SUCCESS') {
            this[`${type}ExportResult`] = response.data.result
            clearInterval(this.statusPolling)
            this.loadExportHistory()
            this.$toast.success('Export completed successfully!')
          } else if (status === 'FAILURE') {
            clearInterval(this.statusPolling)
            this.$toast.error('Export failed: ' + response.data.status)
          }
        } catch (error) {
          console.error('Status check failed:', error)
          clearInterval(this.statusPolling)
        }
      }, 2000)
    },

    async downloadFile(filename) {
      try {
        const response = await axios.get(`/api/export/download/${filename}`, {
          responseType: 'blob'
        })
        
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', filename)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
        
        this.$toast.success('File downloaded successfully!')
      } catch (error) {
        console.error('Download failed:', error)
        this.$toast.error('Download failed: ' + error.response?.data?.error || 'Unknown error')
      }
    },

    async loadExportHistory() {
      try {
        const response = await axios.get('/api/export/list')
        this.exportHistory = response.data.exports
      } catch (error) {
        console.error('Failed to load export history:', error)
      }
    },

    async deleteFile(filename) {
      if (!confirm('Are you sure you want to delete this export file?')) {
        return
      }
      
      try {
        await axios.delete(`/api/export/delete/${filename}`)
        this.$toast.success('File deleted successfully!')
        this.loadExportHistory()
      } catch (error) {
        console.error('Delete failed:', error)
        this.$toast.error('Delete failed: ' + error.response?.data?.error || 'Unknown error')
      }
    },

    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleString()
    }
  }
}
</script>

<style scoped>
.export-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.export-header {
  text-align: center;
  margin-bottom: 30px;
}

.export-header h2 {
  color: #333;
  margin-bottom: 10px;
}

.export-header p {
  color: #666;
}

.export-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.export-section h3 {
  color: #333;
  margin-bottom: 15px;
  border-bottom: 2px solid #007bff;
  padding-bottom: 10px;
}

.export-options {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.format-selector {
  display: flex;
  align-items: center;
  gap: 10px;
}

.format-selector label {
  font-weight: 500;
  min-width: 100px;
}

.format-selector select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
}

.filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.filter-group label {
  font-weight: 500;
  font-size: 14px;
}

.filter-group input,
.filter-group select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
}

.export-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s;
}

.export-btn:hover:not(:disabled) {
  background: #0056b3;
}

.export-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.export-status {
  margin-top: 15px;
  padding: 15px;
  background: white;
  border-radius: 6px;
  border-left: 4px solid #007bff;
}

.status-indicator {
  margin-bottom: 10px;
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
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.download-btn:hover {
  background: #218838;
}

.export-history {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
}

.export-history h3 {
  color: #333;
  margin-bottom: 15px;
  border-bottom: 2px solid #007bff;
  padding-bottom: 10px;
}

.no-exports {
  text-align: center;
  color: #666;
  font-style: italic;
  padding: 20px;
}

.export-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.export-item {
  background: white;
  border-radius: 6px;
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid #ddd;
}

.export-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.filename {
  font-weight: 500;
  color: #333;
}

.size {
  font-size: 12px;
  color: #666;
}

.date {
  font-size: 12px;
  color: #666;
}

.export-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
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
  .export-container {
    padding: 10px;
  }
  
  .export-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .export-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .filters {
    grid-template-columns: 1fr;
  }
}
</style> 