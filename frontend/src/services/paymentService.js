import api from './api';

const paymentService = {
  // Create MoMo payment
  createMoMoPayment: (orderId, amount) => {
    return api.post('/payments/momo/create/', { order_id: orderId, amount });
  },

  // Create COD payment
  createCODPayment: (orderId, amount) => {
    return api.post('/payments/cod/create/', { order_id: orderId, amount });
  },

  // Get payment status
  getPaymentStatus: (orderId) => {
    return api.get(`/payments/${orderId}/`);
  },

  // Confirm COD payment (staff only)
  confirmCODPayment: (orderId) => {
    return api.post(`/payments/${orderId}/confirm/`);
  },
};

export default paymentService;
