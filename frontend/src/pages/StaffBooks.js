import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import AdminLayout from '../components/AdminLayout';
import bookService from '../services/bookService';
import LoadingSpinner from '../components/LoadingSpinner';

const formatPrice = (price) => {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(price);
};

const StaffBooks = () => {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [books, setBooks] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [bookForm, setBookForm] = useState({
    title: '',
    author: '',
    description: '',
    price: '',
    stock: '',
    category_id: '',
    isbn: '',
  });

  useEffect(() => {
    if (!isAuthenticated || (user?.role !== 'staff' && user?.role !== 'manager')) {
      navigate('/login');
      return;
    }
    fetchData();
  }, [isAuthenticated, user, navigate]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [booksRes, categoriesRes] = await Promise.all([
        bookService.getBooks(),
        bookService.getCategories()
      ]);

      // Handle different response structures
      const booksData = booksRes.data?.results || booksRes.results || booksRes.data || booksRes || [];
      const categoriesData = categoriesRes.data?.results || categoriesRes.results || categoriesRes.data || categoriesRes || [];

      setBooks(Array.isArray(booksData) ? booksData : []);
      setCategories(Array.isArray(categoriesData) ? categoriesData : []);
    } catch (error) {
      console.error('Error fetching data:', error);
      setBooks([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (bookForm.id) {
        await bookService.updateBook(bookForm.id, bookForm);
      } else {
        await bookService.createBook(bookForm);
      }
      setShowModal(false);
      setBookForm({ title: '', author: '', description: '', price: '', stock: '', category_id: '', isbn: '' });
      fetchData();
    } catch (error) {
      alert('Lưu sách thất bại: ' + (error.response?.data?.message || error.message));
    }
  };

  const handleEdit = (book) => {
    setBookForm({
      id: book.id,
      title: book.title || '',
      author: book.author || '',
      description: book.description || '',
      price: book.price || '',
      stock: book.stock || '',
      category_id: book.category_id || '',
      isbn: book.isbn || '',
    });
    setShowModal(true);
  };

  const handleDelete = async (bookId) => {
    if (window.confirm('Bạn có chắc muốn xóa sách này?')) {
      try {
        await bookService.deleteBook(bookId);
        fetchData();
      } catch (error) {
        alert('Xóa sách thất bại');
      }
    }
  };

  const getCategoryName = (categoryId) => {
    const category = categories.find(c => c.id === categoryId);
    return category?.name || '-';
  };

  const filteredBooks = books.filter(book =>
    book.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    book.author?.toLowerCase().includes(searchTerm.toLowerCase())
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
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <h1 className="text-2xl font-bold text-gray-900">Quản lý sách</h1>
          <button
            onClick={() => {
              setBookForm({ title: '', author: '', description: '', price: '', stock: '', category_id: '', isbn: '' });
              setShowModal(true);
            }}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center"
          >
            <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Thêm sách mới
          </button>
        </div>

        {/* Search */}
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="relative">
            <input
              type="text"
              placeholder="Tìm kiếm theo tên sách hoặc tác giả..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <svg className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-2xl font-bold text-indigo-600">{books.length}</div>
            <div className="text-sm text-gray-500">Tổng số sách</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-2xl font-bold text-green-600">
              {books.filter(b => b.stock > 10).length}
            </div>
            <div className="text-sm text-gray-500">Còn hàng</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-2xl font-bold text-yellow-600">
              {books.filter(b => b.stock > 0 && b.stock <= 10).length}
            </div>
            <div className="text-sm text-gray-500">Sắp hết</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-2xl font-bold text-red-600">
              {books.filter(b => b.stock === 0).length}
            </div>
            <div className="text-sm text-gray-500">Hết hàng</div>
          </div>
        </div>

        {/* Books Table */}
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sách</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tác giả</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Danh mục</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Giá</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tồn kho</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Thao tác</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredBooks.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="px-6 py-8 text-center text-gray-500">
                      {searchTerm ? 'Không tìm thấy sách phù hợp' : 'Chưa có sách nào'}
                    </td>
                  </tr>
                ) : (
                  filteredBooks.map(book => (
                    <tr key={book.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <div className="h-12 w-10 flex-shrink-0 bg-gray-200 rounded overflow-hidden">
                            {book.cover_image ? (
                              <img src={book.cover_image} alt={book.title} className="h-full w-full object-cover" />
                            ) : (
                              <div className="h-full w-full flex items-center justify-center text-gray-400">
                                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                                </svg>
                              </div>
                            )}
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900 line-clamp-1">{book.title}</div>
                            <div className="text-xs text-gray-500">ID: {book.id}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{book.author}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{getCategoryName(book.category_id)}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {formatPrice(book.price)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          book.stock === 0 ? 'bg-red-100 text-red-800' :
                          book.stock <= 10 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {book.stock}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                        <button
                          onClick={() => handleEdit(book)}
                          className="text-indigo-600 hover:text-indigo-900 font-medium"
                        >
                          Sửa
                        </button>
                        <button
                          onClick={() => handleDelete(book.id)}
                          className="text-red-600 hover:text-red-900 font-medium"
                        >
                          Xóa
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Book Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-medium mb-4">{bookForm.id ? 'Chỉnh sửa sách' : 'Thêm sách mới'}</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tên sách *</label>
                <input
                  type="text"
                  value={bookForm.title}
                  onChange={(e) => setBookForm({ ...bookForm, title: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tác giả *</label>
                <input
                  type="text"
                  value={bookForm.author}
                  onChange={(e) => setBookForm({ ...bookForm, author: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Mô tả</label>
                <textarea
                  value={bookForm.description}
                  onChange={(e) => setBookForm({ ...bookForm, description: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  rows={3}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Giá (VND) *</label>
                  <input
                    type="number"
                    value={bookForm.price}
                    onChange={(e) => setBookForm({ ...bookForm, price: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Số lượng *</label>
                  <input
                    type="number"
                    value={bookForm.stock}
                    onChange={(e) => setBookForm({ ...bookForm, stock: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    required
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Danh mục</label>
                <select
                  value={bookForm.category_id}
                  onChange={(e) => setBookForm({ ...bookForm, category_id: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">-- Chọn danh mục --</option>
                  {categories.map(cat => (
                    <option key={cat.id} value={cat.id}>{cat.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">ISBN</label>
                <input
                  type="text"
                  value={bookForm.isbn}
                  onChange={(e) => setBookForm({ ...bookForm, isbn: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <div className="flex gap-4 pt-4">
                <button
                  type="submit"
                  className="flex-1 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  {bookForm.id ? 'Cập nhật' : 'Tạo mới'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 py-2 border rounded-lg hover:bg-gray-50"
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

export default StaffBooks;
