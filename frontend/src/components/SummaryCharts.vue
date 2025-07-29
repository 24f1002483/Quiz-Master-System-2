<template>
  <div class="summary-charts">
    <div class="bar-chart">[Bar Chart Placeholder: Subject wise top scores]</div>
    <div class="target-chart">[Target Chart Placeholder: Subject wise user attempts]</div>
  </div>
</template>
<script setup>
// Accept props for chart data if needed in the future
</script>
<style scoped>
.summary-charts { display: flex; gap: 2rem; }
.bar-chart, .target-chart { flex: 1; background: #f0f0f0; border-radius: 8px; padding: 1rem; text-align: center; min-height: 200px; }
</style> 