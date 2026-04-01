import api from './api';

const reviewService = {
  getReviews: (bookId, params = {}) => {
    return api.get(`/books/${bookId}/reviews/`, { params });
  },

  createReview: (bookId, reviewData) => {
    return api.post(`/books/${bookId}/reviews/`, reviewData);
  },

  updateReview: (bookId, reviewId, reviewData) => {
    return api.put(`/books/${bookId}/reviews/${reviewId}/`, reviewData);
  },

  deleteReview: (bookId, reviewId) => {
    return api.delete(`/books/${bookId}/reviews/${reviewId}/`);
  },

  getUserReviews: () => {
    return api.get('/reviews/my-reviews/');
  },
};

export default reviewService;
