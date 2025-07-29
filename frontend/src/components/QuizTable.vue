<template>
    <div class="quiz-table">
      <h4>{{ quizGroupTitle }}</h4>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Q_Title</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="quiz in quizzes" :key="quiz.id">
            <td>{{ quiz.id }}</td>
            <td>{{ quiz.title }}</td>
            <td>
              <button @click="$emit('edit', quiz)">Edit</button>
              <button @click="$emit('delete', quiz.id)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
      <button @click="$emit('add-question')">+ Question</button>
    </div>
  </template>
  <script setup>
  defineProps(['quizzes', 'quizGroupTitle']);
  </script>
  <style scoped>
  .quiz-table { border: 1px solid #ddd; border-radius: 4px; padding: 1rem; min-width: 300px; }
  table { width: 100%; margin-bottom: 0.5rem; }
  th, td { padding: 0.3rem; text-align: left; }
  button { margin-right: 0.5rem; }
  </style>