import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import orderService from '../services/orderService';
import LoadingSpinner from '../components/LoadingSpinner';

const OrderDetail = () => {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [cancelling, setCancelling] = useState(false);
  const isSuccess = searchParams.get('success') === 'true';

  const formatPrice = (price) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND',
    }).format(price);
  };

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login?redirect=/orders');
      return;
    }
    fetchOrder();
  }, [id, isAuthenticated]);

  const fetchOrder = async () => {
    try {
      setLoading(true);
      const response = await orderService.getOrder(id);
      setOrder(response.data);
    } catch (error) {
      console.error('Error fetching order:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelOrder = async () => {
    if (!window.confirm('Bạn có chắc chắn muốn huỷ đơn hàng này không?')) return;

    try {
      setCancelling(true);
      await orderService.cancelOrder(id);
      fetchOrder();
    } catch (error) {
      alert(error.response?.data?.message || 'Huỷ đơn hàng thất bại');
    } finally {
      setCancelling(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      processing: 'bg-blue-100 text-blue-800',
      shipped: 'bg-purple-100 text-purple-800',
      delivered: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800',
    };
    return colors[status?.toLowerCase()] || 'bg-gray-100 text-gray-800';
  };

  const getStatusText = (status) => {
    const statusMap = {
      pending: 'Chờ xử lý',
      processing: 'Đang xử lý',
      shipped: 'Đang giao hàng',
      delivered: 'Đã giao hàng',
      cancelled: 'Đã huỷ',
    };
    return statusMap[status?.toLowerCase()] || status;
  };

  const getStatusStep = (status) => {
    const steps = ['pending', 'processing', 'shipped', 'delivered'];
    return steps.indexOf(status?.toLowerCase());
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Không có';
    return new Date(dateString).toLocaleDateString('vi-VN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (!isAuthenticated) {
    return null;
  }

  if (loading) {
    return <LoadingSpinner fullScreen />;
  }

  if (!order) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Không tìm thấy đơn hàng</h1>
        <p className="text-gray-500 mb-6">Đơn hàng bạn đang tìm không tồn tại.</p>
        <Link to="/orders" className="btn-primary">
          Xem tất cả đơn hàng
        </Link>
      </div>
    );
  }

  const currentStep = getStatusStep(order.status);
  const isCancelled = order.status?.toLowerCase() === 'cancelled';

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Success Message */}
      {isSuccess && (
        <div className="mb-6 p-4 bg-green-100 border border-green-400 text-green-700 rounded-lg flex items-center">
          <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          Đặt hàng thành công! Cảm ơn bạn đã mua hàng.
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
        <div>
          <Link to="/orders" className="text-primary-600 hover:text-primary-700 text-sm mb-2 inline-block">
            &larr; Quay lại đơn hàng
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">
            Đơn hàng #{order.id || order.order_number}
          </h1>
          <p className="text-gray-500">Đặt ngày {formatDate(order.created_at)}</p>
        </div>
        <span
          className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium mt-4 sm:mt-0 ${getStatusColor(
            order.status
          )}`}
        >
          {getStatusText(order.status)}
        </span>
      </div>

      {/* Order Tracking */}
      {!isCancelled && (
        <div className="bg-white rounded-xl shadow-md p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">Trạng thái đơn hàng</h2>
          <div className="relative">
            <div className="flex items-center justify-between">
              {['Chờ xử lý', 'Đang xử lý', 'Đang giao', 'Đã giao'].map((step, index) => (
                <div key={step} className="flex flex-col items-center relative z-10">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      index <= currentStep
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-200 text-gray-500'
                    }`}
                  >
                    {index < currentStep ? (
                      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    ) : (
                      index + 1
                    )}
                  </div>
                  <span
                    className={`mt-2 text-sm font-medium ${
                      index <= currentStep ? 'text-primary-600' : 'text-gray-500'
                    }`}
                  >
                    {step}
                  </span>
                </div>
              ))}
            </div>
            <div className="absolute top-5 left-0 right-0 h-0.5 bg-gray-200 -z-0">
              <div
                className="h-full bg-primary-600 transition-all duration-500"
                style={{ width: `${(currentStep / 3) * 100}%` }}
              />
            </div>
          </div>

          {order.tracking_number && (
            <div className="mt-6 pt-6 border-t">
              <p className="text-sm text-gray-600">
                <span className="font-medium">Mã vận đơn:</span> {order.tracking_number}
              </p>
            </div>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Order Items */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-xl shadow-md p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Sản phẩm</h2>
            <div className="divide-y">
              {(order.items || []).map((item, index) => (
                <div key={index} className="py-4 flex items-center">
                  <div className="w-20 h-28 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
                    {item.book?.image ? (
                      <img
                        src={item.book.image}
                        alt={item.book?.title}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full bg-primary-100 flex items-center justify-center">
                        <svg
                          className="w-8 h-8 text-primary-400"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={1}
                            d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                          />
                        </svg>
                      </div>
                    )}
                  </div>
                  <div className="ml-4 flex-grow">
                    <Link
                      to={`/books/${item.book?.id}`}
                      className="font-medium text-gray-900 hover:text-primary-600"
                    >
                      {item.book?.title || 'Sách không xác định'}
                    </Link>
                    <p className="text-sm text-gray-500">{item.book?.author}</p>
                    <p className="text-sm text-gray-500 mt-1">SL: {item.quantity}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-gray-900">
                      {formatPrice((item.price || item.book?.price || 0) * item.quantity)}
                    </p>
                    <p className="text-sm text-gray-500">
                      {formatPrice(item.price || item.book?.price || 0)}/cuốn
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Order Summary Sidebar */}
        <div className="lg:col-span-1 space-y-6">
          {/* Payment Summary */}
          <div className="bg-white rounded-xl shadow-md p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Tóm tắt đơn hàng</h2>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Tạm tính</span>
                <span className="font-medium">{formatPrice(order.subtotal || 0)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Phí vận chuyển</span>
                <span className="font-medium">
                  {parseFloat(order.shipping_cost || 0) === 0 ? (
                    <span className="text-green-600">MIỄN PHÍ</span>
                  ) : (
                    formatPrice(order.shipping_cost || 0)
                  )}
                </span>
              </div>
              <div className="border-t pt-3 mt-3">
                <div className="flex justify-between text-lg font-semibold">
                  <span>Tổng cộng</span>
                  <span className="text-primary-600">
                    {formatPrice(order.total || 0)}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Shipping Address */}
          <div className="bg-white rounded-xl shadow-md p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Địa chỉ giao hàng</h2>
            <p className="text-gray-600">
              {order.shipping_address?.first_name} {order.shipping_address?.last_name}<br />
              {order.shipping_address?.address}<br />
              {order.shipping_address?.district}, {order.shipping_address?.city}<br />
              {order.shipping_address?.phone}
            </p>
          </div>

          {/* Payment Method */}
          <div className="bg-white rounded-xl shadow-md p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Phương thức thanh toán</h2>
            <p className="text-gray-600">
              {order.payment_method === 'cod' && 'Thanh toán khi nhận hàng (COD)'}
              {order.payment_method === 'bank' && 'Chuyển khoản ngân hàng'}
              {order.payment_method === 'momo' && 'Ví MoMo'}
              {order.payment_method === 'vnpay' && 'VNPay'}
              {!order.payment_method && 'Chưa xác định'}
            </p>
          </div>

          {/* Cancel Order Button */}
          {order.status?.toLowerCase() === 'pending' && (
            <button
              onClick={handleCancelOrder}
              disabled={cancelling}
              className="w-full btn-danger py-3"
            >
              {cancelling ? <LoadingSpinner size="small" /> : 'Huỷ đơn hàng'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default OrderDetail;
