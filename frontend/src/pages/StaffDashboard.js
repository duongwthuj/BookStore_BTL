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
    hour: '2-digit',
    minute: '2-digit'
  });
};

const statusConfig = {
  pending: { label: 'Chờ xử lý', bg: 'bg-yellow-100', text: 'text-yellow-700', dot: 'bg-yellow-500' },
  paid: { label: 'Đã thanh toán', bg: 'bg-blue-100', text: 'text-blue-700', dot: 'bg-blue-500' },
  shipping: { label: 'Đang giao', bg: 'bg-purple-100', text: 'text-purple-700', dot: 'bg-purple-500' },
  delivered: { label: 'Đã giao', bg: 'bg-green-100', text: 'text-green-700', dot: 'bg-green-500' },
  completed: { label: 'Hoàn thành', bg: 'bg-emerald-100', text: 'text-emerald-700', dot: 'bg-emerald-500' },
  cancelled: { label: 'Đã hủy', bg: 'bg-red-100', text: 'text-red-700', dot: 'bg-red-500' },
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
      alert('Cập nhật thất bại: ' + (error.response?.data?.error || error.message));
    }
  };

  const filteredOrders = orders.filter(o => {
    const matchStatus = filterStatus === 'all' || o.status === filterStatus;
    const matchSearch = searchTerm === '' ||
      o.id.toString().includes(searchTerm) ||
      o.phone?.includes(searchTerm);
    return matchStatus && matchSearch;
  });

  const getStatusCount = (status) => orders.filter(o => o.status === status).length;

  if (loading) {
    return (
      <AdminLayout>
        <div className="flex justify-center items-center h-64"><LoadingSpinner /></div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-900">Quản lý đơn hàng</h1>
          <button
            onClick={fetchOrders}
            className="px-3 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700"
          >
            Làm mới
          </button>
        </div>

        {/* Stats Row */}
        <div className="flex gap-2 overflow-x-auto pb-2">
          {Object.entries(statusConfig).map(([key, config]) => (
            <button
              key={key}
              onClick={() => setFilterStatus(filterStatus === key ? 'all' : key)}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm whitespace-nowrap transition-all ${
                filterStatus === key
                  ? `${config.bg} ${config.text} ring-2 ring-offset-1 ring-current`
                  : 'bg-white text-gray-600 hover:bg-gray-50'
              }`}
            >
              <span className={`w-2 h-2 rounded-full ${config.dot}`}></span>
              {config.label}
              <span className="font-semibold">{getStatusCount(key)}</span>
            </button>
          ))}
        </div>

        {/* Search */}
        <input
          type="text"
          placeholder="Tìm theo mã đơn hoặc SĐT..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full max-w-sm px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />

        {/* Orders Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Đơn</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Khách hàng</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tổng tiền</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Trạng thái</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ngày tạo</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filteredOrders.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-4 py-8 text-center text-gray-400">
                    Không có đơn hàng
                  </td>
                </tr>
              ) : (
                filteredOrders.map(order => {
                  const status = statusConfig[order.status] || statusConfig.pending;
                  return (
                    <tr key={order.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <span className="font-semibold">#{order.id}</span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="text-sm">{order.shipping_address?.split(',')[0] || '-'}</div>
                        <div className="text-xs text-gray-500">{order.phone}</div>
                      </td>
                      <td className="px-4 py-3 font-medium text-indigo-600">
                        {formatPrice(order.total)}
                      </td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${status.bg} ${status.text}`}>
                          <span className={`w-1.5 h-1.5 rounded-full ${status.dot}`}></span>
                          {status.label}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {formatDate(order.created_at)}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <button
                          onClick={() => setSelectedOrder(order)}
                          className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                        >
                          Chi tiết
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

      {/* Order Detail Modal */}
      {selectedOrder && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full max-h-[85vh] overflow-y-auto">
            {/* Header */}
            <div className="flex items-center justify-between px-5 py-4 border-b">
              <h3 className="font-bold text-lg">Đơn hàng #{selectedOrder.id}</h3>
              <button onClick={() => setSelectedOrder(null)} className="text-gray-400 hover:text-gray-600">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Content */}
            <div className="p-5 space-y-4">
              {/* Customer Info */}
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Điện thoại:</span>
                  <span className="font-medium">{selectedOrder.phone}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Địa chỉ:</span>
                  <span className="font-medium text-right max-w-[200px]">{selectedOrder.shipping_address}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Thanh toán:</span>
                  <span className="font-medium">{selectedOrder.payment_method?.toUpperCase()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Tổng tiền:</span>
                  <span className="font-bold text-indigo-600">{formatPrice(selectedOrder.total)}</span>
                </div>
              </div>

              {/* Items */}
              {selectedOrder.items?.length > 0 && (
                <div className="border-t pt-4">
                  <p className="text-sm text-gray-500 mb-2">Sản phẩm:</p>
                  <div className="space-y-2">
                    {selectedOrder.items.map((item, idx) => (
                      <div key={idx} className="flex justify-between text-sm bg-gray-50 px-3 py-2 rounded">
                        <span>{item.book_title} x{item.quantity}</span>
                        <span>{formatPrice(item.price * item.quantity)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Status Update */}
              <div className="border-t pt-4">
                <p className="text-sm text-gray-500 mb-3">Cập nhật trạng thái:</p>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(statusConfig).map(([key, config]) => (
                    <button
                      key={key}
                      onClick={() => handleStatusUpdate(selectedOrder.id, key)}
                      disabled={selectedOrder.status === key}
                      className={`flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                        selectedOrder.status === key
                          ? `${config.bg} ${config.text} ring-2 ring-current`
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                      }`}
                    >
                      <span className={`w-2 h-2 rounded-full ${config.dot}`}></span>
                      {config.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="px-5 py-4 border-t bg-gray-50 rounded-b-xl">
              <button
                onClick={() => setSelectedOrder(null)}
                className="w-full py-2 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300"
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
