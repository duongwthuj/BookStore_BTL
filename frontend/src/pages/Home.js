import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import BookCard from '../components/BookCard';
import LoadingSpinner from '../components/LoadingSpinner';
import bookService from '../services/bookService';

const Home = () => {
  const [featuredBooks, setFeaturedBooks] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [booksRes, categoriesRes] = await Promise.all([
        bookService.getBooks({ limit: 8 }),
        bookService.getCategories().catch(() => ({ data: { results: [] } })),
      ]);

      setFeaturedBooks(booksRes.data.results || booksRes.data || []);
      setCategories(categoriesRes.data.results || categoriesRes.data || []);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner fullScreen />;
  }

  return (
    <div>
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-primary-600 to-primary-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-4xl md:text-5xl font-bold mb-6">
                Khám Phá Cuốn Sách <br />
                <span className="text-primary-200">Yêu Thích Tiếp Theo</span>
              </h1>
              <p className="text-lg text-primary-100 mb-8">
                Khám phá hàng ngàn cuốn sách đa dạng thể loại. Từ sách bán chạy đến những viên ngọc ẩn,
                tìm cuốn sách hoàn hảo cho mọi tâm trạng và khoảnh khắc.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link
                  to="/books"
                  className="bg-white text-primary-600 font-semibold py-3 px-8 rounded-lg hover:bg-primary-50 transition-colors text-center"
                >
                  Xem Tất Cả Sách
                </Link>
                <Link
                  to="/books?ordering=-created_at"
                  className="border-2 border-white text-white font-semibold py-3 px-8 rounded-lg hover:bg-white hover:text-primary-600 transition-colors text-center"
                >
                  Sách Mới Nhất
                </Link>
              </div>
            </div>
            <div className="hidden lg:block">
              <div className="relative">
                <div className="grid grid-cols-3 gap-4 transform rotate-6">
                  {[1, 2, 3].map((i) => (
                    <div
                      key={i}
                      className={`w-32 h-48 bg-white bg-opacity-10 rounded-lg shadow-xl ${
                        i === 2 ? '-mt-8' : ''
                      }`}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="bg-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {[
              {
                icon: (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"
                  />
                ),
                title: 'Miễn Phí Vận Chuyển',
                description: 'Đơn hàng từ 300.000đ',
              },
              {
                icon: (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                  />
                ),
                title: 'Thanh Toán An Toàn',
                description: 'Bảo mật 100%',
              },
              {
                icon: (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  />
                ),
                title: 'Đổi Trả Dễ Dàng',
                description: 'Trong vòng 30 ngày',
              },
              {
                icon: (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z"
                  />
                ),
                title: 'Hỗ Trợ 24/7',
                description: 'Luôn sẵn sàng giúp đỡ',
              },
            ].map((feature, index) => (
              <div key={index} className="text-center">
                <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg
                    className="w-6 h-6 text-primary-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    {feature.icon}
                  </svg>
                </div>
                <h3 className="font-semibold text-gray-900 mb-1">{feature.title}</h3>
                <p className="text-sm text-gray-500">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Books */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-3xl font-bold text-gray-900">Sách Nổi Bật</h2>
              <p className="text-gray-500 mt-1">Được chọn lọc dành riêng cho bạn</p>
            </div>
            <Link
              to="/books"
              className="text-primary-600 hover:text-primary-700 font-medium flex items-center"
            >
              Xem tất cả
              <svg className="w-5 h-5 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </Link>
          </div>
          {featuredBooks.length > 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-6">
              {featuredBooks.slice(0, 8).map((book) => (
                <BookCard key={book.id} book={book} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12 bg-white rounded-xl">
              <p className="text-gray-500">Chưa có sách nổi bật</p>
            </div>
          )}
        </div>
      </section>

      {/* Categories */}
      {categories.length > 0 && (
        <section className="bg-white py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900">Danh Mục Sách</h2>
              <p className="text-gray-500 mt-2">Tìm sách theo thể loại yêu thích</p>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
              {categories.slice(0, 10).map((category) => (
                <Link
                  key={category.id}
                  to={`/books?category=${category.id}`}
                  className="group p-6 bg-gray-50 rounded-xl hover:bg-primary-50 transition-colors text-center"
                >
                  <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-3 group-hover:bg-primary-200 transition-colors">
                    <svg
                      className="w-6 h-6 text-primary-600"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                      />
                    </svg>
                  </div>
                  <h3 className="font-medium text-gray-900 group-hover:text-primary-600 transition-colors">
                    {category.name}
                  </h3>
                </Link>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Newsletter */}
      <section className="bg-primary-600 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="text-3xl font-bold text-white mb-4">
              Đăng Ký Nhận Tin
            </h2>
            <p className="text-primary-100 mb-8">
              Nhận thông tin mới nhất về sách mới, khuyến mãi và nhiều hơn nữa!
            </p>
            <form className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
              <input
                type="email"
                placeholder="Nhập email của bạn"
                className="flex-1 px-4 py-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-white"
              />
              <button
                type="submit"
                className="bg-white text-primary-600 font-semibold px-6 py-3 rounded-lg hover:bg-primary-50 transition-colors"
              >
                Đăng ký
              </button>
            </form>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
