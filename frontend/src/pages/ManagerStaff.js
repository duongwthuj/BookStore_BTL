import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import AdminLayout from '../components/AdminLayout';
import LoadingSpinner from '../components/LoadingSpinner';
import api from '../services/api';

const ManagerStaff = () => {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [staffList, setStaffList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [staffForm, setStaffForm] = useState({
    username: '', email: '', password: '', first_name: '', last_name: '', role: 'staff',
  });

  useEffect(() => {
    if (!isAuthenticated || user?.role !== 'manager') {
      navigate('/login');
      return;
    }
    fetchStaff();
  }, [isAuthenticated, user, navigate]);

  const fetchStaff = async () => {
    setLoading(true);
    try {
      const response = await api.get('/auth/users/');
      const users = response.data?.results || response.data || [];
      // Filter only staff and manager roles
      const staffUsers = users.filter(u => u.role === 'staff' || u.role === 'manager');
      setStaffList(Array.isArray(staffUsers) ? staffUsers : []);
    } catch (error) {
      console.error('Error fetching staff:', error);
      setStaffList([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (staffForm.id) {
        await api.put(`/auth/users/${staffForm.id}/`, staffForm);
      } else {
        await api.post('/auth/register/', { ...staffForm, role: staffForm.role || 'staff' });
      }
      setShowModal(false);
      setStaffForm({ username: '', email: '', password: '', first_name: '', last_name: '', role: 'staff' });
      fetchStaff();
    } catch (error) {
      alert('Thao tác thất bại: ' + (error.response?.data?.message || JSON.stringify(error.response?.data) || error.message));
    }
  };

  const handleEdit = (staff) => {
    setStaffForm({
      id: staff.id,
      username: staff.username || '',
      email: staff.email || '',
      password: '',
      first_name: staff.first_name || '',
      last_name: staff.last_name || '',
      role: staff.role || 'staff',
    });
    setShowModal(true);
  };

  const handleDelete = async (staffId) => {
    if (window.confirm('Bạn có chắc muốn xóa nhân viên này?')) {
      try {
        await api.delete(`/auth/users/${staffId}/`);
        fetchStaff();
      } catch (error) {
        alert('Xóa thất bại');
      }
    }
  };

  const filteredStaff = staffList.filter(staff =>
    staff.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    staff.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    staff.first_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    staff.last_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
          <h1 className="text-xl font-bold text-gray-900">Quản lý nhân viên</h1>
          <button
            onClick={() => {
              setStaffForm({ username: '', email: '', password: '', first_name: '', last_name: '', role: 'staff' });
              setShowModal(true);
            }}
            className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700"
          >
            + Thêm nhân viên
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-white p-3 rounded-lg shadow-sm text-center">
            <div className="text-2xl font-bold text-gray-800">{staffList.length}</div>
            <div className="text-xs text-gray-500">Tổng số</div>
          </div>
          <div className="bg-white p-3 rounded-lg shadow-sm text-center">
            <div className="text-2xl font-bold text-indigo-600">{staffList.filter(s => s.role === 'staff').length}</div>
            <div className="text-xs text-gray-500">Nhân viên</div>
          </div>
          <div className="bg-white p-3 rounded-lg shadow-sm text-center">
            <div className="text-2xl font-bold text-purple-600">{staffList.filter(s => s.role === 'manager').length}</div>
            <div className="text-xs text-gray-500">Quản lý</div>
          </div>
        </div>

        {/* Search */}
        <input
          type="text"
          placeholder="Tìm theo tên, email..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full max-w-sm px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />

        {/* Staff Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nhân viên</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Vai trò</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filteredStaff.length === 0 ? (
                <tr>
                  <td colSpan="4" className="px-4 py-8 text-center text-gray-400">
                    {searchTerm ? 'Không tìm thấy nhân viên' : 'Chưa có nhân viên nào'}
                  </td>
                </tr>
              ) : (
                filteredStaff.map(staff => (
                  <tr key={staff.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 bg-indigo-100 rounded-full flex items-center justify-center">
                          <span className="text-indigo-600 font-medium text-sm">
                            {(staff.first_name?.[0] || staff.username?.[0] || '?').toUpperCase()}
                          </span>
                        </div>
                        <div>
                          <div className="font-medium text-gray-900">
                            {staff.first_name && staff.last_name
                              ? `${staff.first_name} ${staff.last_name}`
                              : staff.username}
                          </div>
                          <div className="text-xs text-gray-400">@{staff.username}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">{staff.email || '-'}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                        staff.role === 'manager'
                          ? 'bg-purple-100 text-purple-700'
                          : 'bg-blue-100 text-blue-700'
                      }`}>
                        {staff.role === 'manager' ? 'Quản lý' : 'Nhân viên'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2 justify-end">
                        <button
                          onClick={() => handleEdit(staff)}
                          className="text-indigo-600 hover:text-indigo-800 text-sm"
                        >
                          Sửa
                        </button>
                        {staff.id !== user?.id && (
                          <button
                            onClick={() => handleDelete(staff.id)}
                            className="text-red-600 hover:text-red-800 text-sm"
                          >
                            Xóa
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Staff Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between px-5 py-4 border-b">
              <h3 className="font-bold text-lg">{staffForm.id ? 'Chỉnh sửa nhân viên' : 'Thêm nhân viên mới'}</h3>
              <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-600">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-5 space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Họ</label>
                  <input
                    type="text"
                    value={staffForm.first_name}
                    onChange={(e) => setStaffForm({ ...staffForm, first_name: e.target.value })}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Tên</label>
                  <input
                    type="text"
                    value={staffForm.last_name}
                    onChange={(e) => setStaffForm({ ...staffForm, last_name: e.target.value })}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tên đăng nhập *</label>
                <input
                  type="text"
                  value={staffForm.username}
                  onChange={(e) => setStaffForm({ ...staffForm, username: e.target.value })}
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  required
                  disabled={!!staffForm.id}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email *</label>
                <input
                  type="email"
                  value={staffForm.email}
                  onChange={(e) => setStaffForm({ ...staffForm, email: e.target.value })}
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Mật khẩu {staffForm.id ? '(để trống nếu không đổi)' : '*'}
                </label>
                <input
                  type="password"
                  value={staffForm.password}
                  onChange={(e) => setStaffForm({ ...staffForm, password: e.target.value })}
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  required={!staffForm.id}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Vai trò</label>
                <select
                  value={staffForm.role}
                  onChange={(e) => setStaffForm({ ...staffForm, role: e.target.value })}
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="staff">Nhân viên</option>
                  <option value="manager">Quản lý</option>
                </select>
              </div>
              <div className="flex gap-3 pt-2">
                <button
                  type="submit"
                  className="flex-1 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium"
                >
                  {staffForm.id ? 'Cập nhật' : 'Thêm mới'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 py-2 border border-gray-200 rounded-lg hover:bg-gray-50 font-medium"
                >
                  Hủy
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AdminLayout>
  );
};

export default ManagerStaff;
