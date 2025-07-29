import axios from 'axios';

const API_URL = 'http://localhost:5000/api/admin';
const QUIZ_API_URL = 'http://localhost:5000/api/quiz';
const OPTIMIZED_API_URL = 'http://localhost:5000/api/v2';

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

// Fetch all quizzes for admin management
export const fetchAllQuizzes = async () => {
  try {
    const response = await axios.get(`${API_URL}/quizzes`, { 
      withCredentials: true 
    });
    return response.data;
  } catch (error) {
    throw error.response?.data?.message || error.message || 'Unknown error';
  }
};

// Fetch quizzes by chapter (existing functionality)
export const fetchQuizzes = async (chapterId) => {
  try {
    let url = `${QUIZ_API_URL}/quizzes`;
    if (chapterId !== undefined && chapterId !== null) {
      url += `/chapter/${chapterId}`;
    }
    
    const token = localStorage.getItem('token');
    const response = await axios.get(url, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.data;
  } catch (error) {
    throw error.response?.data?.message || error.message || 'Unknown error';
  }
};

// Fetch a specific quiz by ID (with fallback to optimized API)
export const fetchQuizById = async (quizId) => {
  try {
    // Try optimized API first
    const response = await axios.get(`${OPTIMIZED_API_URL}/quizzes/${quizId}`, { 
      withCredentials: true 
    });
    return response.data;
  } catch (error) {
    // Fallback to regular API if optimized fails
    try {
      const response = await axios.get(`${QUIZ_API_URL}/quizzes/${quizId}`, { 
        withCredentials: true 
      });
      return response.data;
    } catch (fallbackError) {
      throw fallbackError.response?.data?.message || fallbackError.message || 'Unknown error';
    }
  }
};

// Fetch questions for a specific quiz
export const fetchQuizQuestions = async (quizId) => {
  try {
    const response = await axios.get(`${QUIZ_API_URL}/questions/${quizId}`, { 
      withCredentials: true 
    });
    return response.data;
  } catch (error) {
    throw error.response?.data?.message || error.message || 'Unknown error';
  }
};

export const createQuiz = async (quizData) => {
  try {
    const csrfToken = getCookie('csrf_access_token');
    const response = await axios.post(
      `${API_URL}/quizzes`,
      quizData,
      {
        withCredentials: true,
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

export const updateQuiz = async (id, quizData) => {
  try {
    const csrfToken = getCookie('csrf_access_token');
    const response = await axios.put(
      `${API_URL}/quizzes/${id}`,
      quizData,
      {
        withCredentials: true,
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

export const deleteQuiz = async (id) => {
  try {
    const csrfToken = getCookie('csrf_access_token');
    const response = await axios.delete(
      `${API_URL}/quizzes/${id}`,
      {
        withCredentials: true,
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