import axios from 'axios';

const API_URL = 'http://localhost:5000/api/admin';
const QUIZ_API_URL = 'http://localhost:5000/api/quiz';

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

export const fetchChapters = async (subjectId) => {
  try {
    const response = await axios.get(`${QUIZ_API_URL}/chapters/${subjectId}`, { withCredentials: true });
    return response.data;
  } catch (error) {
    throw error.response?.data?.message || error.message || 'Unknown error';
  }
};

export const fetchAllChapters = async () => {
  try {
    const response = await axios.get(`${QUIZ_API_URL}/chapters`, { withCredentials: true });
    return response.data;
  } catch (error) {
    throw error.response?.data?.message || error.message || 'Unknown error';
  }
};

export const createChapter = async (chapterData) => {
  try {
    const csrfToken = getCookie('csrf_access_token');
    const response = await axios.post(
      `${API_URL}/chapters`,
      chapterData,
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

export const updateChapter = async (id, chapterData) => {
  try {
    const csrfToken = getCookie('csrf_access_token');
    const response = await axios.put(
      `${API_URL}/chapters/${id}`,
      chapterData,
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

export const deleteChapter = async (id) => {
  try {
    const csrfToken = getCookie('csrf_access_token');
    const response = await axios.delete(
      `${API_URL}/chapters/${id}`,
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