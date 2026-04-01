import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import orderService from '../services/orderService';
import LoadingSpinner from '../components/LoadingSpinner';
import Pagination from '../components/Pagination';

const Orders = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

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
    fetchOrders();
  }, [isAuthenticated, currentPage]);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const response = await orderService.getOrders({ page: currentPage });
      setOrders(response.data.results || response.data || []);
      setTotalPages(Math.ceil((response.data.count || response.data.length || 0) / 10));
    } catch (error) {
      console.error('Error fetching orders:', error);
    } finally {
      setLoading(false);
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
      pending: 'Cho xu ly',
      processing: 'Dang xu ly',
      shipped: 'Dang giao hang',
      delivered: 'Da giao hang',
      cancelled: 'Da huy',
    };
    return statusMap[status?.toLowerCase()] || status;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('vi-VN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  if (!isAuthenticated) {
    return null;
  }

  if (loading) {
    return <LoadingSpinner fullScreen />;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Don Hang Cua Toi</h1>

      {orders.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-xl shadow-md">
          <svg
            className="w-24 h-24 text-gray-300 mx-auto mb-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">Chua co don hang nao</h2>
          <p className="text-gray-500 mb-6">
            Ban chua dat don hang nao. Hay bat dau mua sam!
          </p>
          <Link to="/books" className="btn-primary">
            Xem Sach
          </Link>
        </div>
      ) : (
        <>
          <div className="space-y-4">
            {orders.map((order) => (
              <Link
                key={order.id}
                to={`/orders/${order.id}`}
                className="block bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow overflow-hidden"
              >
                <div className="p-6">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">
                        Don hang #{order.id || order.order_number}
                      </h3>
                      <p className="text-sm text-gray-500">
                        Dat ngay {formatDate(order.created_at)}
                      </p>
                    </div>
                    <span
                      className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium mt-2 sm:mt-0 ${getStatusColor(
                        order.status
                      )}`}
                    >
                      {getStatusText(order.status)}
                    </span>
                  </div>

                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                    <div className="flex items-center space-x-4">
                      {/* Item Preview */}
                      <div className="flex -space-x-2">
                        {(order.items || []).slice(0, 3).map((item, index) => (
                          <div
                            key={index}
                            className="w-12 h-16 bg-gray-100 rounded border-2 border-white overflow-hidden"
                          >
                            {item.book?.image ? (
                              <img
                                src={item.book.image}
                                alt={item.book.title}
                                className="w-full h-full object-cover"
                              />
                            ) : (
                              <div className="w-full h-full bg-primary-100" />
                            )}
                          </div>
                        ))}
                        {(order.items?.length || 0) > 3 && (
                          <div className="w-12 h-16 bg-gray-200 rounded border-2 border-white flex items-center justify-center">
                            <span className="text-sm text-gray-600">
                              +{order.items.length - 3}
                            </span>
                          </div>
                        )}
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">
                          {order.items?.length || 0} san pham
                        </p>
                      </div>
                    </div>

                    <div className="mt-4 sm:mt-0 flex items-center justify-between sm:justify-end sm:space-x-6">
                      <div className="text-right">
                        <p className="text-sm text-gray-500">Tong tien</p>
                        <p className="text-lg font-semibold text-primary-600">
                          {formatPrice(order.total || 0)}
                        </p>
                      </div>
                      <svg
                        className="w-5 h-5 text-gray-400 hidden sm:block"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 5l7 7-7 7"
                        />
                      </svg>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>

          <div className="mt-8">
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={setCurrentPage}
            />
          </div>
        </>
      )}
    </div>
  );
};

export default Orders;
