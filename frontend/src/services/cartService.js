import api from './api';

const cartService = {
  getCart: () => {
    return api.get('/cart/');
  },

  addItem: (bookId, quantity = 1) => {
    return api.post('/cart/items/', { book_id: bookId, quantity });
  },

  updateItem: (itemId, quantity) => {
    return api.put(`/cart/items/${itemId}/`, { quantity });
  },

  removeItem: (itemId) => {
    return api.delete(`/cart/items/${itemId}/`);
  },

  clearCart: () => {
    return api.delete('/cart/clear/');
  },

  applyCoupon: (code) => {
    return api.post('/cart/apply-coupon/', { code });
  },

  removeCoupon: () => {
    return api.post('/cart/remove-coupon/');
  },
};

export default cartService;
