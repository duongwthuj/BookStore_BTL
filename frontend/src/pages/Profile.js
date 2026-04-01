import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import authService from '../services/authService';
import LoadingSpinner from '../components/LoadingSpinner';

const Profile = () => {
  const { user, isAuthenticated, updateUser, logout } = useAuth();
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  const [profileData, setProfileData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
  });

  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login?redirect=/profile');
      return;
    }

    if (user) {
      setProfileData({
        firstName: user.first_name || '',
        lastName: user.last_name || '',
        email: user.email || '',
        phone: user.phone || '',
      });
    }
  }, [user, isAuthenticated, navigate]);

  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfileData((prev) => ({ ...prev, [name]: value }));
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData((prev) => ({ ...prev, [name]: value }));
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await authService.updateProfile({
        first_name: profileData.firstName,
        last_name: profileData.lastName,
        phone: profileData.phone,
      });

      updateUser(response.data);
      setMessage({ type: 'success', text: 'Cap nhat thong tin thanh cong!' });
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.message || 'Cap nhat that bai',
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ type: '', text: '' });

    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setMessage({ type: 'error', text: 'Mat khau moi khong khop' });
      setLoading(false);
      return;
    }

    if (passwordData.newPassword.length < 8) {
      setMessage({ type: 'error', text: 'Mat khau phai co it nhat 8 ky tu' });
      setLoading(false);
      return;
    }

    try {
      await authService.changePassword(
        passwordData.currentPassword,
        passwordData.newPassword
      );

      setMessage({ type: 'success', text: 'Doi mat khau thanh cong!' });
      setPasswordData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      });
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.message || 'Doi mat khau that bai',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (!window.confirm('Ban co chac chan muon xoa tai khoan? Hanh dong nay khong the hoan tac.')) {
      return;
    }

    try {
      logout();
      navigate('/');
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.message || 'Xoa tai khoan that bai',
      });
    }
  };

  const tabLabels = {
    profile: 'Thong tin',
    password: 'Mat khau',
    preferences: 'Tuy chon',
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Cai Dat Tai Khoan</h1>

      {/* Tabs */}
      <div className="flex space-x-1 bg-gray-100 rounded-lg p-1 mb-8">
        {['profile', 'password', 'preferences'].map((tab) => (
          <button
            key={tab}
            onClick={() => {
              setActiveTab(tab);
              setMessage({ type: '', text: '' });
            }}
            className={`flex-1 py-2 px-4 rounded-md font-medium text-sm transition-colors ${
              activeTab === tab
                ? 'bg-white text-primary-600 shadow'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {tabLabels[tab]}
          </button>
        ))}
      </div>

      {/* Message */}
      {message.text && (
        <div
          className={`mb-6 p-4 rounded-lg ${
            message.type === 'success'
              ? 'bg-green-100 border border-green-400 text-green-700'
              : 'bg-red-100 border border-red-400 text-red-700'
          }`}
        >
          {message.text}
        </div>
      )}

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Thong Tin Ca Nhan</h2>
          <form onSubmit={handleProfileSubmit} className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Ho
                </label>
                <input
                  type="text"
                  name="firstName"
                  value={profileData.firstName}
                  onChange={handleProfileChange}
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Ten
                </label>
                <input
                  type="text"
                  name="lastName"
                  value={profileData.lastName}
                  onChange={handleProfileChange}
                  className="input-field"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Dia Chi Email
              </label>
              <input
                type="email"
                name="email"
                value={profileData.email}
                disabled
                className="input-field bg-gray-100 cursor-not-allowed"
              />
              <p className="text-sm text-gray-500 mt-1">
                Email khong the thay doi
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                So Dien Thoai
              </label>
              <input
                type="tel"
                name="phone"
                value={profileData.phone}
                onChange={handleProfileChange}
                className="input-field"
                placeholder="0901234567"
              />
            </div>

            <div className="pt-4">
              <button
                type="submit"
                disabled={loading}
                className="btn-primary"
              >
                {loading ? <LoadingSpinner size="small" /> : 'Luu Thay Doi'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Password Tab */}
      {activeTab === 'password' && (
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Doi Mat Khau</h2>
          <form onSubmit={handlePasswordSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Mat Khau Hien Tai
              </label>
              <input
                type="password"
                name="currentPassword"
                value={passwordData.currentPassword}
                onChange={handlePasswordChange}
                className="input-field"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Mat Khau Moi
              </label>
              <input
                type="password"
                name="newPassword"
                value={passwordData.newPassword}
                onChange={handlePasswordChange}
                className="input-field"
                required
                minLength={8}
              />
              <p className="text-sm text-gray-500 mt-1">
                Phai co it nhat 8 ky tu
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Xac Nhan Mat Khau Moi
              </label>
              <input
                type="password"
                name="confirmPassword"
                value={passwordData.confirmPassword}
                onChange={handlePasswordChange}
                className="input-field"
                required
              />
            </div>

            <div className="pt-4">
              <button
                type="submit"
                disabled={loading}
                className="btn-primary"
              >
                {loading ? <LoadingSpinner size="small" /> : 'Doi Mat Khau'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Preferences Tab */}
      {activeTab === 'preferences' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Thong Bao</h2>
            <div className="space-y-4">
              {[
                { id: 'orderUpdates', label: 'Cap nhat don hang', description: 'Nhan thong bao ve don hang cua ban' },
                { id: 'promotions', label: 'Khuyen mai', description: 'Nhan email ve chuong trinh khuyen mai' },
                { id: 'newArrivals', label: 'Sach moi', description: 'Duoc thong bao khi co sach moi' },
                { id: 'recommendations', label: 'Goi y sach', description: 'Goi y sach dua tren so thich cua ban' },
              ].map((item) => (
                <label key={item.id} className="flex items-start cursor-pointer">
                  <input
                    type="checkbox"
                    defaultChecked
                    className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500 mt-1"
                  />
                  <div className="ml-3">
                    <span className="font-medium text-gray-900">{item.label}</span>
                    <p className="text-sm text-gray-500">{item.description}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Danger Zone */}
          <div className="bg-white rounded-xl shadow-md p-6 border-2 border-red-200">
            <h2 className="text-xl font-semibold text-red-600 mb-4">Vung Nguy Hiem</h2>
            <p className="text-gray-600 mb-4">
              Khi xoa tai khoan, ban se khong the khoi phuc lai. Vui long can nhac ky truoc khi thuc hien.
            </p>
            <button
              onClick={handleDeleteAccount}
              className="btn-danger"
            >
              Xoa Tai Khoan
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Profile;
