import api from './api';

const bookService = {
  getBooks: (params = {}) => {
    return api.get('/books/', { params });
  },

  getBook: (id) => {
    return api.get(`/books/${id}/`);
  },

  getFeaturedBooks: () => {
    return api.get('/books/', { params: { featured: true, limit: 8 } });
  },

  getRecommendations: () => {
    return api.get('/books/recommendations/');
  },

  searchBooks: (query) => {
    return api.get('/books/', { params: { search: query } });
  },

  getCategories: () => {
    return api.get('/categories/');
  },

  // Staff operations
  createBook: (bookData) => {
    return api.post('/books/', bookData);
  },

  updateBook: (id, bookData) => {
    return api.put(`/books/${id}/`, bookData);
  },

  deleteBook: (id) => {
    return api.delete(`/books/${id}/`);
  },

  uploadBookImage: (id, formData) => {
    return api.post(`/books/${id}/upload-image/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

export default bookService;
