import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import AdminLayout from '../components/AdminLayout';
import orderService from '../services/orderService';
import LoadingSpinner from '../components/LoadingSpinner';

const formatPrice = (price) => {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(price);
};

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const StaffDashboard = () => {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (!isAuthenticated || (user?.role !== 'staff' && user?.role !== 'manager')) {
      navigate('/login');
      return;
    }
    fetchOrders();
  }, [isAuthenticated, user, navigate]);

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const response = await orderService.getOrders();
      const ordersData = response.data?.results || response.results || response.data || response || [];
      setOrders(Array.isArray(ordersData) ? ordersData : []);
    } catch (error) {
      console.error('Error fetching orders:', error);
      setOrders([]);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (orderId, newStatus) => {
    try {
      await orderService.updateStatus(orderId, newStatus);
      setOrders(orders.map(order =>
        order.id === orderId ? { ...order, status: newStatus } : order
      ));
      setSelectedOrder(null);
    } catch (error) {
      alert('Cập nhật trạng thái thất bại: ' + (error.response?.data?.error || error.message));
    }
  };

  const getStatusConfig = (status) => {
    const configs = {
      pending: {
        color: 'bg-amber-100 text-amber-800 border-amber-200',
        icon: '⏳',
        label: 'Chờ xử lý'
      },
      paid: {
        color: 'bg-blue-100 text-blue-800 border-blue-200',
        icon: '💳',
        label: 'Đã thanh toán'
      },
      shipping: {
        color: 'bg-purple-100 text-purple-800 border-purple-200',
        icon: '🚚',
        label: 'Đang giao'
      },
      delivered: {
        color: 'bg-emerald-100 text-emerald-800 border-emerald-200',
        icon: '📦',
        label: 'Đã giao'
      },
      completed: {
        color: 'bg-green-100 text-green-800 border-green-200',
        icon: '✅',
        label: 'Hoàn thành'
      },
      cancelled: {
        color: 'bg-red-100 text-red-800 border-red-200',
        icon: '❌',
        label: 'Đã hủy'
      },
    };
    return configs[status] || { color: 'bg-gray-100 text-gray-800', icon: '📋', label: status };
  };

  const statusCounts = orders.reduce((acc, order) => {
    acc[order.status] = (acc[order.status] || 0) + 1;
    return acc;
  }, {});

  const filteredOrders = orders
    .filter(o => filterStatus === 'all' || o.status === filterStatus)
    .filter(o =>
      searchTerm === '' ||
      o.id.toString().includes(searchTerm) ||
      o.phone?.includes(searchTerm) ||
      o.shipping_address?.toLowerCase().includes(searchTerm.toLowerCase())
    );

  const todayOrders = orders.filter(o => {
    const today = new Date().toDateString();
    return new Date(o.created_at).toDateString() === today;
  });

  const todayRevenue = orders
    .filter(o => {
      const today = new Date().toDateString();
      return new Date(o.created_at).toDateString() === today &&
             ['paid', 'shipping', 'delivered', 'completed'].includes(o.status);
    })
    .reduce((sum, o) => sum + parseFloat(o.total || 0), 0);

  if (loading) {
    return (
      <AdminLayout>
        <div className="flex justify-center items-center h-64"><LoadingSpinner /></div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Quản lý đơn hàng</h1>
            <p className="text-gray-500 mt-1">Xin chào, {user?.first_name || user?.username}! 👋</p>
          </div>
          <button
            onClick={fetchOrders}
            className="mt-4 md:mt-0 inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Làm mới
          </button>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-5 text-white shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100 text-sm">Tổng đơn hàng</p>
                <p className="text-3xl font-bold mt-1">{orders.length}</p>
              </div>
              <div className="bg-blue-400/30 p-3 rounded-lg">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-amber-500 to-orange-500 rounded-xl p-5 text-white shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-amber-100 text-sm">Chờ xử lý</p>
                <p className="text-3xl font-bold mt-1">{statusCounts.pending || 0}</p>
              </div>
              <div className="bg-amber-400/30 p-3 rounded-lg">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-5 text-white shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100 text-sm">Đơn hôm nay</p>
                <p className="text-3xl font-bold mt-1">{todayOrders.length}</p>
              </div>
              <div className="bg-purple-400/30 p-3 rounded-lg">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-emerald-500 to-green-600 rounded-xl p-5 text-white shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-emerald-100 text-sm">Doanh thu hôm nay</p>
                <p className="text-2xl font-bold mt-1">{formatPrice(todayRevenue)}</p>
              </div>
              <div className="bg-emerald-400/30 p-3 rounded-lg">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-sm p-4">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <input
                type="text"
                placeholder="Tìm theo mã đơn, SĐT, địa chỉ..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
              <svg className="absolute left-3 top-3 h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>

            {/* Status Filter */}
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setFilterStatus('all')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  filterStatus === 'all'
                    ? 'bg-indigo-600 text-white shadow-md'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                Tất cả ({orders.length})
              </button>
              {['pending', 'paid', 'shipping', 'delivered', 'completed', 'cancelled'].map(status => {
                const config = getStatusConfig(status);
                return (
                  <button
                    key={status}
                    onClick={() => setFilterStatus(status)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                      filterStatus === status
                        ? 'bg-indigo-600 text-white shadow-md'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {config.icon} {config.label} ({statusCounts[status] || 0})
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Orders Table */}
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-100">
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Đơn hàng</th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Khách hàng</th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Sản phẩm</th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Tổng tiền</th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Trạng thái</th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Thời gian</th>
                  <th className="px-6 py-4 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">Thao tác</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filteredOrders.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="px-6 py-12 text-center">
                      <div className="text-gray-400">
                        <svg className="mx-auto h-12 w-12 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                        </svg>
                        <p className="text-lg font-medium">Không có đơn hàng nào</p>
                        <p className="text-sm mt-1">Thử thay đổi bộ lọc hoặc tìm kiếm</p>
                      </div>
                    </td>
                  </tr>
                ) : (
                  filteredOrders.map(order => {
                    const statusConfig = getStatusConfig(order.status);
                    return (
                      <tr key={order.id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-4">
                          <div className="flex items-center">
                            <div className="bg-indigo-100 text-indigo-600 p-2 rounded-lg mr-3">
                              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                              </svg>
                            </div>
                            <div>
                              <p className="font-semibold text-gray-900">#{order.id}</p>
                              <p className="text-xs text-gray-500">{order.payment_method?.toUpperCase()}</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div>
                            <p className="font-medium text-gray-900">{order.shipping_address?.split(',')[0] || `KH #${order.customer_id}`}</p>
                            <p className="text-sm text-gray-500">{order.phone}</p>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <p className="text-sm text-gray-600">
                            {order.items?.length || 0} sản phẩm
                          </p>
                        </td>
                        <td className="px-6 py-4">
                          <p className="font-semibold text-gray-900">{formatPrice(order.total)}</p>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${statusConfig.color}`}>
                            <span className="mr-1.5">{statusConfig.icon}</span>
                            {statusConfig.label}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <p className="text-sm text-gray-600">{formatDate(order.created_at)}</p>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <button
                            onClick={() => setSelectedOrder(order)}
                            className="inline-flex items-center px-3 py-1.5 bg-indigo-50 text-indigo-600 rounded-lg hover:bg-indigo-100 transition-colors font-medium text-sm"
                          >
                            <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                            Cập nhật
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Order Detail Modal */}
      {selectedOrder && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-4 rounded-t-2xl">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold text-white">Đơn hàng #{selectedOrder.id}</h3>
                <button
                  onClick={() => setSelectedOrder(null)}
                  className="text-white/80 hover:text-white transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Order Info */}
            <div className="p-6 border-b">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-500">Khách hàng</p>
                  <p className="font-medium">{selectedOrder.shipping_address?.split(',')[0]}</p>
                </div>
                <div>
                  <p className="text-gray-500">Điện thoại</p>
                  <p className="font-medium">{selectedOrder.phone}</p>
                </div>
                <div className="col-span-2">
                  <p className="text-gray-500">Địa chỉ</p>
                  <p className="font-medium">{selectedOrder.shipping_address}</p>
                </div>
                <div>
                  <p className="text-gray-500">Tổng tiền</p>
                  <p className="font-bold text-lg text-indigo-600">{formatPrice(selectedOrder.total)}</p>
                </div>
                <div>
                  <p className="text-gray-500">Thanh toán</p>
                  <p className="font-medium">{selectedOrder.payment_method?.toUpperCase()}</p>
                </div>
              </div>
            </div>

            {/* Status Update */}
            <div className="p-6">
              <p className="text-sm font-medium text-gray-700 mb-3">Cập nhật trạng thái:</p>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { key: 'pending', label: 'Chờ xử lý', icon: '⏳' },
                  { key: 'paid', label: 'Đã thanh toán', icon: '💳' },
                  { key: 'shipping', label: 'Đang giao', icon: '🚚' },
                  { key: 'delivered', label: 'Đã giao', icon: '📦' },
                  { key: 'completed', label: 'Hoàn thành', icon: '✅' },
                  { key: 'cancelled', label: 'Đã hủy', icon: '❌' },
                ].map(status => (
                  <button
                    key={status.key}
                    onClick={() => handleStatusUpdate(selectedOrder.id, status.key)}
                    disabled={selectedOrder.status === status.key}
                    className={`py-3 px-4 rounded-xl text-sm font-medium transition-all flex items-center justify-center gap-2 ${
                      selectedOrder.status === status.key
                        ? 'bg-indigo-600 text-white cursor-default ring-2 ring-indigo-300'
                        : 'bg-gray-100 text-gray-700 hover:bg-indigo-50 hover:text-indigo-600'
                    }`}
                  >
                    <span>{status.icon}</span>
                    {status.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-4 bg-gray-50 rounded-b-2xl">
              <button
                onClick={() => setSelectedOrder(null)}
                className="w-full py-3 bg-gray-200 text-gray-700 rounded-xl font-medium hover:bg-gray-300 transition-colors"
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}
    </AdminLayout>
  );
};

export default StaffDashboard;
