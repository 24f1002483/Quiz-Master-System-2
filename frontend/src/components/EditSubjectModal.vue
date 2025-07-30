<template>
  <div class="modal-overlay" @click="$emit('cancel')">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>✏️ Edit Subject</h3>
        <button class="close-btn" @click="$emit('cancel')">&times;</button>
      </div>
      
      <form @submit.prevent="handleSubmit" class="modal-form">
        <div class="form-group">
          <label for="name">Subject Name:</label>
          <input 
            id="name"
            v-model="formData.name" 
            type="text" 
            required 
            placeholder="Enter subject name"
            class="form-input"
          >
        </div>
        
        <div class="form-group">
          <label for="description">Description:</label>
          <textarea 
            id="description"
            v-model="formData.description" 
            placeholder="Enter subject description"
            class="form-textarea"
            rows="3"
          ></textarea>
        </div>
        
        <div class="form-actions">
          <button type="button" @click="$emit('cancel')" class="cancel-btn">
            Cancel
          </button>
          <button type="submit" class="save-btn" :disabled="loading">
            <span v-if="loading">Saving...</span>
            <span v-else>Save Changes</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const props = defineProps({
  subject: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['save', 'cancel']);

const loading = ref(false);
const formData = ref({
  name: '',
  description: ''
});

onMounted(() => {
  // Initialize form with current subject data
  formData.value = {
    name: props.subject.name || '',
    description: props.subject.description || ''
  };
});

const handleSubmit = async () => {
  if (!formData.value.name.trim()) {
    alert('Subject name is required');
    return;
  }
  
  loading.value = true;
  try {
    await emit('save', {
      name: formData.value.name.trim(),
      description: formData.value.description.trim()
    });
  } catch (error) {
    console.error('Error saving subject:', error);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e0e7ff;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.3rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background: #f0f0f0;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.95rem;
}

.form-input,
.form-textarea {
  padding: 0.75rem;
  border: 2px solid #e0e7ff;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #4f8cff;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1rem;
}

.cancel-btn,
.save-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.95rem;
}

.cancel-btn {
  background: #f8f9fa;
  color: #6c757d;
  border: 2px solid #dee2e6;
}

.cancel-btn:hover {
  background: #e9ecef;
  border-color: #adb5bd;
}

.save-btn {
  background: linear-gradient(90deg, #42b983 60%, #4f8cff 100%);
  color: white;
}

.save-btn:hover:not(:disabled) {
  background: linear-gradient(90deg, #4f8cff 60%, #42b983 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(79, 140, 255, 0.3);
}

.save-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}
</style> 