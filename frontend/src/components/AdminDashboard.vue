<template>
  <div class="admin-dashboard">
    <main class="dashboard-content">
      <section class="subjects-section">
        <h2>Subjects</h2>
        <div class="subjects-grid">
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
        <button class="add-subject-btn" @click="showAddSubject = true">+ Subject</button>
      </section>
    </main>

    <!-- Modals -->
    <NewSubjectModal v-if="showAddSubject" @save="addSubject" @cancel="showAddSubject = false" />
    <NewChapterModal v-if="showAddChapter" @save="addChapter" @cancel="showAddChapter = false" />
    <EditChapterModal v-if="showEditChapter" :modelValue="selectedChapter" @save="updateChapter" @cancel="showEditChapter = false" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import SubjectCard from './SubjectCard.vue';
import NewSubjectModal from './NewSubjectModal.vue';
import NewChapterModal from './NewChapterModal.vue';
import EditChapterModal from './EditChapterModal.vue';
import { logoutUser } from '../services/authService.js';
import { fetchSubjects, createSubject, deleteSubject as deleteSubjectApi } from '../services/subjectService.js';
import { createChapter, updateChapter as updateChapterApi, deleteChapter as deleteChapterApi } from '../services/chapterService.js';


const subjects = ref([]);
const showAddSubject = ref(false);
const showAddChapter = ref(false);
const showEditChapter = ref(false);
const selectedSubjectId = ref(null);
const selectedChapter = ref(null);

async function loadSubjects() {
  // Each subject should have a 'quizzes' array for SubjectCard
  subjects.value = await fetchSubjects();
}
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
  await createSubject(subject);
  showAddSubject.value = false;
  await loadSubjects();
};
const deleteSubject = async (id) => {
  await deleteSubjectApi(id);
  await loadSubjects();
};
const editSubject = async (subject) => {
  // Open edit modal or inline edit
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
    const chapterData = {
      ...chapter,
      subject_id: selectedSubjectId.value
    };
    await createChapter(chapterData);
    showAddChapter.value = false;
    await loadSubjects();
  } catch (error) {
    alert('Error creating chapter: ' + error);
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



</script>

<style scoped>
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
.admin-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #e3f0ff 0%, #f9f9ff 100%);
  padding: 2rem 0;
}
.dashboard-content { display: flex; flex-direction: column; gap: 2rem; padding: 2rem; }
.subjects-section {
  background: #fff;
  padding: 2rem;
  border-radius: 16px;
  margin-bottom: 2rem;
  box-shadow: 0 2px 12px rgba(44, 62, 80, 0.06);
}
.subjects-grid { display: flex; flex-direction: column; gap: 2rem; }
.subject-row {
  display: flex;
  gap: 2rem;
  justify-content: space-between;
}
.subject-card {
  flex: 1 1 0;
  min-width: 0;
}
a { color: #1ca01c; text-decoration: underline; cursor: pointer; }
.add-subject-btn {
  margin-top: 1.5rem;
  background: #e3e3e3;
  border-radius: 4px;
  border: none;
  padding: 0.5rem 1.2rem;
  font-weight: 500;
  cursor: pointer;
}
</style>