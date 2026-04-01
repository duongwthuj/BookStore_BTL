import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import AdminLayout from '../components/AdminLayout';
import orderService from '../services/orderService';
import LoadingSpinner from '../components/LoadingSpinner';

const formatPrice = (price) => {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(price);
};

const formatShortPrice = (price) => {
  if (price >= 1000000) {
    return (price / 1000000).toFixed(1) + 'M';
  }
  if (price >= 1000) {
    return (price / 1000).toFixed(0) + 'K';
  }
  return price.toString();
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

  const getStatusConfig = (status) => {
    const configs = {
      pending: { color: '#f59e0b', label: 'Chờ xử lý' },
      paid: { color: '#3b82f6', label: 'Đã thanh toán' },
      shipping: { color: '#8b5cf6', label: 'Đang giao' },
      delivered: { color: '#10b981', label: 'Đã giao' },
      completed: { color: '#22c55e', label: 'Hoàn thành' },
      cancelled: { color: '#ef4444', label: 'Đã hủy' },
    };
    return configs[status] || { color: '#6b7280', label: status };
  };

  if (loading) {
    return (
      <AdminLayout>
        <div className="flex justify-center items-center h-64"><LoadingSpinner /></div>
      </AdminLayout>
    );
  }

  const totalStatusCount = stats?.orders_by_status?.reduce((sum, item) => sum + item.count, 0) || 1;
  const maxDailyOrders = Math.max(...(stats?.orders_by_date?.map(i => i.count) || [1]), 1);
  const maxMonthlyRevenue = Math.max(...(stats?.orders_by_month?.map(i => parseFloat(i.revenue) || 0) || [1]), 1);

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Thống kê & Báo cáo</h1>
            <p className="text-gray-500 mt-1">Xin chào, {user?.first_name || 'Quản lý'}! 📊</p>
          </div>
        </div>

        {/* Date Filter */}
        <div className="bg-white rounded-xl shadow-sm p-4">
          <div className="flex flex-wrap gap-4 items-end">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Từ ngày</label>
              <input
                type="date"
                name="start_date"
                value={dateRange.start_date}
                onChange={handleDateChange}
                className="border border-gray-200 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Đến ngày</label>
              <input
                type="date"
                name="end_date"
                value={dateRange.end_date}
                onChange={handleDateChange}
                className="border border-gray-200 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <button
              onClick={fetchStats}
              className="px-6 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
            >
              Áp dụng
            </button>
          </div>
        </div>

        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl p-6 text-white shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100">Tổng đơn hàng</p>
                <p className="text-4xl font-bold mt-2">{stats?.total_orders || 0}</p>
              </div>
              <div className="bg-white/20 p-4 rounded-xl">
                <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-emerald-500 to-green-600 rounded-2xl p-6 text-white shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-emerald-100">Tổng doanh thu</p>
                <p className="text-3xl font-bold mt-2">{formatPrice(stats?.total_revenue || 0)}</p>
              </div>
              <div className="bg-white/20 p-4 rounded-xl">
                <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-purple-500 to-indigo-600 rounded-2xl p-6 text-white shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100">Giá trị đơn TB</p>
                <p className="text-3xl font-bold mt-2">{formatPrice(stats?.avg_order_value || 0)}</p>
              </div>
              <div className="bg-white/20 p-4 rounded-xl">
                <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Orders by Status - Donut Chart */}
          <div className="bg-white rounded-2xl shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Đơn hàng theo trạng thái</h3>
            {stats?.orders_by_status?.length > 0 ? (
              <div className="flex items-center gap-8">
                {/* Donut Chart */}
                <div className="relative w-48 h-48 flex-shrink-0">
                  <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                    {(() => {
                      let cumulativePercent = 0;
                      return stats.orders_by_status.map((item, index) => {
                        const percent = (item.count / totalStatusCount) * 100;
                        const dashArray = `${percent} ${100 - percent}`;
                        const dashOffset = -cumulativePercent;
                        cumulativePercent += percent;
                        const config = getStatusConfig(item.status);
                        return (
                          <circle
                            key={item.status}
                            cx="50"
                            cy="50"
                            r="40"
                            fill="none"
                            stroke={config.color}
                            strokeWidth="20"
                            strokeDasharray={dashArray}
                            strokeDashoffset={dashOffset}
                            className="transition-all duration-500"
                          />
                        );
                      });
                    })()}
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                      <p className="text-3xl font-bold text-gray-900">{stats?.total_orders || 0}</p>
                      <p className="text-sm text-gray-500">Đơn hàng</p>
                    </div>
                  </div>
                </div>

                {/* Legend */}
                <div className="flex-1 space-y-3">
                  {stats.orders_by_status.map(item => {
                    const config = getStatusConfig(item.status);
                    const percent = ((item.count / totalStatusCount) * 100).toFixed(1);
                    return (
                      <div key={item.status} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: config.color }}></div>
                          <span className="text-sm text-gray-600">{config.label}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-gray-900">{item.count}</span>
                          <span className="text-xs text-gray-400">({percent}%)</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">Chưa có dữ liệu</p>
            )}
          </div>

          {/* Top Products */}
          <div className="bg-white rounded-2xl shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Top sản phẩm bán chạy</h3>
            {stats?.top_products?.length > 0 ? (
              <div className="space-y-4">
                {stats.top_products.slice(0, 5).map((item, index) => {
                  const maxQty = stats.top_products[0]?.total_quantity || 1;
                  const percent = (item.total_quantity / maxQty) * 100;
                  const colors = ['from-indigo-500 to-purple-500', 'from-blue-500 to-cyan-500', 'from-emerald-500 to-teal-500', 'from-amber-500 to-orange-500', 'from-pink-500 to-rose-500'];
                  return (
                    <div key={item.book_id}>
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-3">
                          <span className={`w-7 h-7 rounded-full bg-gradient-to-r ${colors[index]} text-white text-sm font-bold flex items-center justify-center`}>
                            {index + 1}
                          </span>
                          <span className="text-sm font-medium text-gray-700 truncate max-w-[180px]">{item.book_title}</span>
                        </div>
                        <span className="text-sm font-bold text-gray-900">{item.total_quantity} cuốn</span>
                      </div>
                      <div className="ml-10 h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className={`h-full bg-gradient-to-r ${colors[index]} rounded-full transition-all duration-500`}
                          style={{ width: `${percent}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">Chưa có dữ liệu</p>
            )}
          </div>
        </div>

        {/* Daily Orders Chart */}
        <div className="bg-white rounded-2xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Đơn hàng 30 ngày qua</h3>
          {stats?.orders_by_date?.length > 0 ? (
            <div className="relative">
              {/* Y-axis labels */}
              <div className="absolute left-0 top-0 bottom-8 w-12 flex flex-col justify-between text-xs text-gray-400">
                <span>{maxDailyOrders}</span>
                <span>{Math.round(maxDailyOrders / 2)}</span>
                <span>0</span>
              </div>

              {/* Chart */}
              <div className="ml-14">
                <div className="flex items-end gap-1 h-48 border-b border-l border-gray-200 pb-2 pl-2">
                  {stats.orders_by_date.map((item, index) => {
                    const height = (item.count / maxDailyOrders) * 100;
                    return (
                      <div
                        key={item.date || index}
                        className="flex-1 bg-gradient-to-t from-indigo-500 to-purple-500 rounded-t hover:from-indigo-600 hover:to-purple-600 transition-all cursor-pointer group relative min-w-[8px]"
                        style={{ height: `${Math.max(height, 2)}%` }}
                      >
                        {/* Tooltip */}
                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10 pointer-events-none">
                          <p className="font-medium">{new Date(item.date).toLocaleDateString('vi-VN')}</p>
                          <p>{item.count} đơn hàng</p>
                          <p>{formatPrice(item.revenue || 0)}</p>
                        </div>
                      </div>
                    );
                  })}
                </div>
                <p className="text-center text-sm text-gray-500 mt-3">Di chuột vào cột để xem chi tiết</p>
              </div>
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">Chưa có dữ liệu</p>
          )}
        </div>

        {/* Monthly Revenue Chart */}
        <div className="bg-white rounded-2xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Doanh thu theo tháng</h3>
          {stats?.orders_by_month?.length > 0 ? (
            <div className="space-y-4">
              {stats.orders_by_month.slice(0, 6).map((item, index) => {
                const revenue = parseFloat(item.revenue) || 0;
                const percent = (revenue / maxMonthlyRevenue) * 100;
                const monthName = item.month
                  ? new Date(item.month).toLocaleDateString('vi-VN', { month: 'long', year: 'numeric' })
                  : '-';
                return (
                  <div key={item.month || index}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">{monthName}</span>
                      <div className="flex items-center gap-4">
                        <span className="text-sm text-gray-500">{item.count} đơn</span>
                        <span className="text-sm font-bold text-emerald-600">{formatPrice(revenue)}</span>
                      </div>
                    </div>
                    <div className="h-4 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-emerald-400 to-green-500 rounded-full transition-all duration-500"
                        style={{ width: `${percent}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">Chưa có dữ liệu</p>
          )}
        </div>
      </div>
    </AdminLayout>
  );
};

export default ManagerDashboard;
