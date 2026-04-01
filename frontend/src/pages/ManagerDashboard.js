import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import AdminLayout from '../components/AdminLayout';
import orderService from '../services/orderService';
import LoadingSpinner from '../components/LoadingSpinner';

const formatPrice = (price) => {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(price);
};

const ManagerDashboard = () => {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState({
    start_date: '',
    end_date: '',
  });

  useEffect(() => {
    if (!isAuthenticated || user?.role !== 'manager') {
      navigate('/login');
      return;
    }
    fetchStats();
  }, [isAuthenticated, user, navigate]);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const response = await orderService.getStats(dateRange);
      setStats(response.data || response);
    } catch (error) {
      console.error('Error fetching stats:', error);
      setStats({
        total_orders: 0,
        total_revenue: 0,
        avg_order_value: 0,
        orders_by_status: [],
        top_products: [],
        orders_by_month: [],
        orders_by_date: []
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDateChange = (e) => {
    setDateRange(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const getStatusText = (status) => {
    const texts = {
      pending: 'Chờ xử lý',
      paid: 'Đã thanh toán',
      shipping: 'Đang giao',
      delivered: 'Đã giao',
      completed: 'Hoàn thành',
      cancelled: 'Đã hủy',
    };
    return texts[status] || status;
  };

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
        <h1 className="text-2xl font-bold text-gray-900">Thống kê & Báo cáo</h1>

        {/* Date Filter */}
        <div className="bg-white shadow rounded-lg p-4">
          <div className="flex flex-wrap gap-4 items-end">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Từ ngày</label>
              <input
                type="date"
                name="start_date"
                value={dateRange.start_date}
                onChange={handleDateChange}
                className="border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Đến ngày</label>
              <input
                type="date"
                name="end_date"
                value={dateRange.end_date}
                onChange={handleDateChange}
                className="border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <button
              onClick={fetchStats}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              Áp dụng
            </button>
          </div>
        </div>

        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-full">
                <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <div className="ml-4">
                <h3 className="text-sm font-medium text-gray-500">Tổng đơn hàng</h3>
                <p className="text-2xl font-bold text-gray-900">{stats?.total_orders || 0}</p>
              </div>
            </div>
          </div>
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center">
              <div className="p-3 bg-green-100 rounded-full">
                <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-4">
                <h3 className="text-sm font-medium text-gray-500">Tổng doanh thu</h3>
                <p className="text-2xl font-bold text-green-600">{formatPrice(stats?.total_revenue || 0)}</p>
              </div>
            </div>
          </div>
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center">
              <div className="p-3 bg-indigo-100 rounded-full">
                <svg className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </div>
              <div className="ml-4">
                <h3 className="text-sm font-medium text-gray-500">Giá trị đơn TB</h3>
                <p className="text-2xl font-bold text-indigo-600">{formatPrice(stats?.avg_order_value || 0)}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Orders by Status & Top Products */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Đơn hàng theo trạng thái</h3>
            <div className="space-y-3">
              {stats?.orders_by_status?.length > 0 ? (
                stats.orders_by_status.map(item => (
                  <div key={item.status} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="font-medium">{getStatusText(item.status)}</span>
                    <span className="text-lg font-bold text-indigo-600">{item.count}</span>
                  </div>
                ))
              ) : (
                <p className="text-gray-500 text-center py-4">Chưa có dữ liệu</p>
              )}
            </div>
          </div>

          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Sản phẩm bán chạy</h3>
            <div className="space-y-3">
              {stats?.top_products?.length > 0 ? (
                stats.top_products.slice(0, 5).map((item, index) => (
                  <div key={item.book_id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="flex items-center">
                      <span className="w-6 h-6 bg-indigo-600 text-white rounded-full flex items-center justify-center text-sm mr-3">
                        {index + 1}
                      </span>
                      <span className="truncate max-w-[200px]">{item.book_title}</span>
                    </span>
                    <span className="font-bold text-green-600">{item.total_quantity} đã bán</span>
                  </div>
                ))
              ) : (
                <p className="text-gray-500 text-center py-4">Chưa có dữ liệu</p>
              )}
            </div>
          </div>
        </div>

        {/* Monthly Revenue */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Doanh thu theo tháng</h3>
          {stats?.orders_by_month?.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left text-sm font-medium text-gray-500 pb-3">Tháng</th>
                    <th className="text-left text-sm font-medium text-gray-500 pb-3">Số đơn</th>
                    <th className="text-left text-sm font-medium text-gray-500 pb-3">Doanh thu</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {stats.orders_by_month.map(item => (
                    <tr key={item.month}>
                      <td className="py-3 text-sm text-gray-900">
                        {item.month ? new Date(item.month).toLocaleDateString('vi-VN', { month: 'long', year: 'numeric' }) : '-'}
                      </td>
                      <td className="py-3 text-sm font-medium text-gray-900">{item.count}</td>
                      <td className="py-3 text-sm font-medium text-green-600">{formatPrice(item.revenue || 0)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">Chưa có dữ liệu</p>
          )}
        </div>

        {/* Daily Orders Chart */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Đơn hàng 30 ngày qua</h3>
          {stats?.orders_by_date?.length > 0 ? (
            <>
              <div className="flex items-end space-x-1" style={{ minHeight: '200px' }}>
                {stats.orders_by_date.map(item => {
                  const maxCount = Math.max(...(stats.orders_by_date?.map(i => i.count) || [1]));
                  const height = (item.count / maxCount) * 150;
                  return (
                    <div
                      key={item.date}
                      className="flex-1 bg-indigo-500 hover:bg-indigo-600 transition-colors rounded-t cursor-pointer group relative"
                      style={{ height: `${Math.max(height, 10)}px` }}
                    >
                      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 whitespace-nowrap">
                        {new Date(item.date).toLocaleDateString('vi-VN')}: {item.count} đơn
                      </div>
                    </div>
                  );
                })}
              </div>
              <div className="mt-2 text-xs text-gray-500 text-center">
                Di chuột vào cột để xem chi tiết
              </div>
            </>
          ) : (
            <p className="text-gray-500 text-center py-8">Chưa có dữ liệu</p>
          )}
        </div>
      </div>
    </AdminLayout>
  );
};

export default ManagerDashboard;
