<template>
  <div v-if="showWarning" class="session-warning">
    <div class="warning-content">
      <div class="warning-icon">⚠️</div>
      <div class="warning-text">
        <h3>Session Timeout Warning</h3>
        <p>Your session will expire in {{ remainingMinutes }} minutes due to inactivity.</p>
        <p>Click anywhere to extend your session.</p>
      </div>
      <div class="warning-actions">
        <button @click="extendSession" class="extend-btn">Extend Session</button>
        <button @click="logout" class="logout-btn">Logout Now</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import sessionService from '../services/sessionService.js';

const showWarning = ref(false);
const remainingMinutes = ref(0);
const warningTimer = ref(null);

const WARNING_THRESHOLD = 5; // Show warning when 5 minutes remaining

onMounted(() => {
  // Check remaining time every minute
  warningTimer.value = setInterval(() => {
    const remaining = sessionService.getRemainingTime();
    remainingMinutes.value = remaining;
    
    if (remaining <= WARNING_THRESHOLD && remaining > 0) {
      showWarning.value = true;
    } else {
      showWarning.value = false;
    }
  }, 60000); // Check every minute
});

onUnmounted(() => {
  if (warningTimer.value) {
    clearInterval(warningTimer.value);
  }
});

const extendSession = () => {
  sessionService.resetActivityTimer();
  showWarning.value = false;
};

const logout = () => {
  sessionService.handleLogout('You have been logged out.');
};
</script>

<style scoped>
.session-warning {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.warning-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  max-width: 400px;
  text-align: center;
}

.warning-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.warning-text h3 {
  color: #e74c3c;
  margin-bottom: 1rem;
}

.warning-text p {
  margin-bottom: 0.5rem;
  color: #333;
}

.warning-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
  justify-content: center;
}

.extend-btn, .logout-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.extend-btn {
  background-color: #27ae60;
  color: white;
}

.extend-btn:hover {
  background-color: #229954;
}

.logout-btn {
  background-color: #e74c3c;
  color: white;
}

.logout-btn:hover {
  background-color: #c0392b;
}
</style> 