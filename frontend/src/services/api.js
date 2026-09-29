import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://ai-chatbot-backend-96p2.onrender.com/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const getDocuments = async () => {
  const response = await api.get('/documents');
  return response.data;
};

export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const deleteDocument = async (id) => {
  const response = await api.delete(`/documents/${id}`);
  return response.data;
};

export const getConversations = async () => {
  const response = await api.get('/conversations');
  return response.data;
};

export const getConversationDetails = async (id) => {
  const response = await api.get(`/conversations/${id}`);
  return response.data;
};

export const createConversation = async (title = 'New Conversation') => {
  const response = await api.post('/conversations', { title });
  return response.data;
};

export const deleteConversation = async (id) => {
  const response = await api.delete(`/conversations/${id}`);
  return response.data;
};

export const sendMessage = async (message, conversationId = null) => {
  const payload = {
    message,
    conversation_id: conversationId,
  };
  const response = await api.post('/chat', payload);
  return response.data;
};

export default api;
