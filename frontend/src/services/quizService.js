import api from './axiosConfig.js';

const API_URL = '/api/admin';
const QUIZ_API_URL = '/api/quiz';
const OPTIMIZED_API_URL = '/api/v2';

// Fetch all quizzes for admin management
export const fetchAllQuizzes = async () => {
  try {
    const response = await api.get(`${API_URL}/quizzes`);
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
    
    const response = await api.get(url);
    return response.data;
  } catch (error) {
    throw error.response?.data?.message || error.message || 'Unknown error';
  }
};

// Fetch a specific quiz by ID (with fallback to optimized API)
export const fetchQuizById = async (quizId) => {
  try {
    // Try optimized API first
    const response = await api.get(`${OPTIMIZED_API_URL}/quizzes/${quizId}`);
    return response.data;
  } catch (error) {
    // Fallback to regular API if optimized fails
    try {
      const response = await api.get(`${QUIZ_API_URL}/quizzes/${quizId}`);
      return response.data;
    } catch (fallbackError) {
      throw fallbackError.response?.data?.message || fallbackError.message || 'Unknown error';
    }
  }
};

// Fetch questions for a specific quiz
export const fetchQuizQuestions = async (quizId) => {
  try {
    const response = await api.get(`${QUIZ_API_URL}/questions/${quizId}`);
    return response.data;
  } catch (error) {
    throw error.response?.data?.message || error.message || 'Unknown error';
  }
};

export const createQuiz = async (quizData) => {
  try {
    const response = await api.post(`${API_URL}/quizzes`, quizData);
    return response.data;
  } catch (error) {
    throw error.response?.data?.message || error.message || 'Unknown error';
  }
};

export const updateQuiz = async (id, quizData) => {
  try {
    const response = await api.put(`${API_URL}/quizzes/${id}`, quizData);
    return response.data;
  } catch (error) {
    throw error.response?.data?.message || error.message || 'Unknown error';
  }
};

export const deleteQuiz = async (id) => {
  try {
    const response = await api.delete(`${API_URL}/quizzes/${id}`);
    return response.data;
  } catch (error) {
    throw error.response?.data?.message || error.message || 'Unknown error';
  }
}; 