import api from './axiosConfig.js';

const API_URL = '/api';

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

export const fetchSubjects = async () => {
  try {
    const response = await api.get(`${API_URL}/subjects`);
    return response.data;
  } catch (error) {
    throw error.response?.data?.message || error.message || 'Unknown error';
  }
};

export const createSubject = async (subjectData) => {
  try {
    const response = await api.post(`${API_URL}/subjects`, subjectData);
    return response.data;
  } catch (error) {
    throw error.response?.data?.message || error.message || 'Unknown error';
  }
};

export const updateSubject = async (id, subjectData) => {
  try {
    const response = await api.put(`${API_URL}/subjects/${id}`, subjectData);
    return response.data;
  } catch (error) {
    throw error.response?.data?.message || error.message || 'Unknown error';
  }
};

export const deleteSubject = async (id) => {
  try {
    const response = await api.delete(`${API_URL}/subjects/${id}`);
    return response.data;
  } catch (error) {
    throw error.response?.data?.message || error.message || 'Unknown error';
  }
};