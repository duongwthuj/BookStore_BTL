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
    return api.post('/chat/new-session/');
  },

  endSession: (sessionId) => {
    return api.post(`/chat/end-session/${sessionId}/`);
  },
};

export default chatService;
