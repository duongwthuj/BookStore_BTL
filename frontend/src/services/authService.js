import api from './api';

const authService = {
  login: (email, password) => {
    return api.post('/auth/login/', { email, password });
  },

  register: (userData) => {
    return api.post('/auth/register/', userData);
  },

  logout: () => {
    const refreshToken = localStorage.getItem('refreshToken');
    return api.post('/auth/logout/', { refresh: refreshToken });
  },

  refreshToken: (refresh) => {
    return api.post('/auth/refresh/', { refresh });
  },

  getProfile: () => {
    return api.get('/auth/profile/');
  },

  updateProfile: (userData) => {
    return api.put('/auth/profile/', userData);
  },

  changePassword: (currentPassword, newPassword) => {
    return api.post('/auth/change-password/', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  },

  requestPasswordReset: (email) => {
    return api.post('/auth/password-reset/', { email });
  },

  resetPassword: (token, newPassword) => {
    return api.post('/auth/password-reset/confirm/', {
      token,
      new_password: newPassword,
    });
  },
};

export default authService;
