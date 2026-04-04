import api from './api';

const chatService = {
  sendMessage: (message, sessionId = null) => {
    return api.post('/chat/', {
      message,
      session_id: sessionId,
    });
  },

  getChatHistory: (sessionId) => {
    return api.get(`/chat/history/${sessionId}/`);
  },

  startNewSession: () => {
    return api.post('/chat/sessions/');
  },

  endSession: (sessionId) => {
    return api.delete(`/chat/sessions/${sessionId}/`);
  },

  listSessions: () => {
    return api.get('/chat/sessions/');
  },

  // Document management (admin)
  uploadDocument: (formData) => {
    return api.post('/chat/documents/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  listDocuments: (type = null) => {
    const params = type ? { type } : {};
    return api.get('/chat/documents/', { params });
  },

  deleteDocument: (docId) => {
    return api.delete(`/chat/documents/${docId}/`);
  },

  syncBooks: () => {
    return api.post('/chat/sync-books/');
  },

  getRagStats: () => {
    return api.get('/chat/rag-stats/');
  },
};

export default chatService;
