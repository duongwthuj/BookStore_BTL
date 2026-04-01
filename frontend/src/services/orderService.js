import api from './api';

const orderService = {
  getOrders: (params = {}) => {
    return api.get('/orders/', { params });
  },

  getOrder: (id) => {
    return api.get(`/orders/${id}/`);
  },

  createOrder: (orderData) => {
    return api.post('/orders/', orderData);
  },

  cancelOrder: (id) => {
    return api.post(`/orders/${id}/cancel/`);
  },

  // Staff operations
  getAllOrders: (params = {}) => {
    return api.get('/orders/all/', { params });
  },

  updateOrderStatus: (id, status) => {
    return api.put(`/orders/${id}/status/`, { status });
  },

  updateStatus: (id, status) => {
    return api.put(`/orders/${id}/status/`, { status });
  },

  getOrderStats: () => {
    return api.get('/orders/stats/');
  },

  getStats: (params = {}) => {
    return api.get('/orders/stats/', { params });
  },
};

export default orderService;
