import api from './axiosConfig.js';

const API_URL = '/api/admin';
const QUIZ_API_URL = '/api/quiz';

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

export const fetchQuestions = async (quizId) => {
  try {
    const response = await api.get(`${QUIZ_API_URL}/questions/${quizId}`);
    return response.data;
  } catch (error) {
    throw error.response?.data?.message || error.message || 'Unknown error';
  }
};

export const createQuestion = async (questionData) => {
  try {
    const csrfToken = getCookie('csrf_access_token');
    const response = await api.post(
      `${API_URL}/questions`,
      questionData,
      {
        headers: {
          'X-CSRF-TOKEN': csrfToken
        }
      }
    );
    return response.data;
  } catch (error) {
    throw error.response?.data?.message || error.message || 'Unknown error';
  }
};

export const updateQuestion = async (id, questionData) => {
  try {
    const csrfToken = getCookie('csrf_access_token');
    const response = await api.put(
      `${API_URL}/questions/${id}`,
      questionData,
      {
        headers: {
          'X-CSRF-TOKEN': csrfToken
        }
      }
    );
    return response.data;
  } catch (error) {
    throw error.response?.data?.message || error.message || 'Unknown error';
  }
};

export const deleteQuestion = async (id) => {
  try {
    const csrfToken = getCookie('csrf_access_token');
    const response = await api.delete(
      `${API_URL}/questions/${id}`,
      {
        headers: {
          'X-CSRF-TOKEN': csrfToken
        }
      }
    );
    return response.data;
  } catch (error) {
    throw error.response?.data?.message || error.message || 'Unknown error';
  }
}; 