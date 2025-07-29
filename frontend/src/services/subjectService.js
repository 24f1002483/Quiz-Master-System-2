import axios from 'axios';

const API_URL = 'http://localhost:5000/api/admin';

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

export const fetchSubjects = async () => {
  try {
    const response = await axios.get(`${API_URL}/subjects`, { withCredentials: true });
    return response.data;
  } catch (error) {
    throw error.response?.data?.message || error.message || 'Unknown error';
  }
};

export const createSubject = async (subjectData) => {
  try {
    const csrfToken = getCookie('csrf_access_token');
    const response = await axios.post(
      `${API_URL}/subjects`,
      subjectData,
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

export const updateSubject = async (id, subjectData) => {
  try {
    const csrfToken = getCookie('csrf_access_token');
    const response = await axios.put(
      `${API_URL}/subjects/${id}`,
      subjectData,
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

export const deleteSubject = async (id) => {
  try {
    const csrfToken = getCookie('csrf_access_token');
    const response = await axios.delete(
      `${API_URL}/subjects/${id}`,
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