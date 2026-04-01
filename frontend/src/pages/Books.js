import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import BookCard from '../components/BookCard';
import Pagination from '../components/Pagination';
import LoadingSpinner from '../components/LoadingSpinner';
import bookService from '../services/bookService';

const Books = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [books, setBooks] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  const [filters, setFilters] = useState({
    search: searchParams.get('search') || '',
    category: searchParams.get('category') || '',
    minPrice: searchParams.get('minPrice') || '',
    maxPrice: searchParams.get('maxPrice') || '',
    sortBy: searchParams.get('ordering') || searchParams.get('sortBy') || '-created_at',
    page: parseInt(searchParams.get('page')) || 1,
  });

  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    fetchCategories();
  }, []);

  useEffect(() => {
    fetchBooks();
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.set(key, value);
    });
    setSearchParams(params);
  }, [filters]);

  const fetchCategories = async () => {
    try {
      const response = await bookService.getCategories();
      setCategories(response.data.results || response.data || []);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchBooks = async () => {
    try {
      setLoading(true);
      const params = {
        page: filters.page,
        ordering: filters.sortBy,
      };

      if (filters.search) params.search = filters.search;
      if (filters.category) params.category_id = filters.category;
      if (filters.minPrice) params.min_price = filters.minPrice;
      if (filters.maxPrice) params.max_price = filters.maxPrice;

      const response = await bookService.getBooks(params);
      setBooks(response.data.results || response.data || []);
      setTotalCount(response.data.count || response.data.length || 0);
      setTotalPages(Math.ceil((response.data.count || response.data.length || 0) / 12));
    } catch (error) {
      console.error('Error fetching books:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value,
      page: key !== 'page' ? 1 : value,
    }));
  };

  const handleSearch = (e) => {
    e.preventDefault();
    handleFilterChange('search', filters.search);
  };

  const clearFilters = () => {
    setFilters({
      search: '',
      category: '',
      minPrice: '',
      maxPrice: '',
      sortBy: '-created_at',
      page: 1,
    });
  };

  const sortOptions = [
    { value: '-created_at', label: 'Mới nhất' },
    { value: 'created_at', label: 'Cũ nhất' },
    { value: 'price', label: 'Giá: Thấp đến cao' },
    { value: '-price', label: 'Giá: Cao đến thấp' },
    { value: 'title', label: 'Tên: A-Z' },
    { value: '-title', label: 'Tên: Z-A' },
  ];

  const formatPrice = (price) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND',
    }).format(price);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Tất Cả Sách</h1>
        <p className="text-gray-500 mt-1">
          {totalCount} cuốn sách
        </p>
      </div>

      {/* Search and Filters Bar */}
      <div className="bg-white rounded-xl shadow-md p-4 mb-8">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Search */}
          <form onSubmit={handleSearch} className="flex-1">
            <div className="relative">
              <input
                type="text"
                value={filters.search}
                onChange={(e) => setFilters((prev) => ({ ...prev, search: e.target.value }))}
                placeholder="Tìm theo tên sách, tác giả, ISBN..."
                className="input-field pl-10"
              />
              <svg
                className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>
          </form>

          {/* Sort */}
          <select
            value={filters.sortBy}
            onChange={(e) => handleFilterChange('sortBy', e.target.value)}
            className="input-field w-full lg:w-48"
          >
            {sortOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>

          {/* Filter Toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="btn-secondary flex items-center justify-center lg:w-auto"
          >
            <svg
              className="w-5 h-5 mr-2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
              />
            </svg>
            Bộ lọc
          </button>
        </div>

        {/* Expandable Filters */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Category */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Thể loại
              </label>
              <select
                value={filters.category}
                onChange={(e) => handleFilterChange('category', e.target.value)}
                className="input-field"
              >
                <option value="">Tất cả thể loại</option>
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Min Price */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Giá từ
              </label>
              <input
                type="number"
                min="0"
                step="1000"
                value={filters.minPrice}
                onChange={(e) => handleFilterChange('minPrice', e.target.value)}
                placeholder="0đ"
                className="input-field"
              />
            </div>

            {/* Max Price */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Giá đến
              </label>
              <input
                type="number"
                min="0"
                step="1000"
                value={filters.maxPrice}
                onChange={(e) => handleFilterChange('maxPrice', e.target.value)}
                placeholder="500.000đ"
                className="input-field"
              />
            </div>

            {/* Clear Filters */}
            <div className="flex items-end">
              <button
                onClick={clearFilters}
                className="btn-secondary w-full"
              >
                Xóa bộ lọc
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Active Filters */}
      {(filters.search || filters.category || filters.minPrice || filters.maxPrice) && (
        <div className="flex flex-wrap gap-2 mb-6">
          {filters.search && (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-primary-100 text-primary-800">
              Tìm kiếm: {filters.search}
              <button
                onClick={() => handleFilterChange('search', '')}
                className="ml-2 hover:text-primary-600"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </span>
          )}
          {filters.category && (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-primary-100 text-primary-800">
              Thể loại: {categories.find((c) => String(c.id) === String(filters.category))?.name || filters.category}
              <button
                onClick={() => handleFilterChange('category', '')}
                className="ml-2 hover:text-primary-600"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </span>
          )}
          {(filters.minPrice || filters.maxPrice) && (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-primary-100 text-primary-800">
              Giá: {filters.minPrice ? formatPrice(filters.minPrice) : '0đ'} - {filters.maxPrice ? formatPrice(filters.maxPrice) : 'không giới hạn'}
              <button
                onClick={() => {
                  handleFilterChange('minPrice', '');
                  handleFilterChange('maxPrice', '');
                }}
                className="ml-2 hover:text-primary-600"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </span>
          )}
        </div>
      )}

      {/* Books Grid */}
      {loading ? (
        <LoadingSpinner />
      ) : books.length > 0 ? (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-6 mb-8">
            {books.map((book) => (
              <BookCard key={book.id} book={book} />
            ))}
          </div>
          <Pagination
            currentPage={filters.page}
            totalPages={totalPages}
            onPageChange={(page) => handleFilterChange('page', page)}
          />
        </>
      ) : (
        <div className="text-center py-16 bg-white rounded-xl">
          <svg
            className="w-16 h-16 text-gray-300 mx-auto mb-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1}
              d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Không tìm thấy sách</h3>
          <p className="text-gray-500 mb-4">
            Hãy thử điều chỉnh bộ lọc hoặc tìm kiếm với từ khóa khác.
          </p>
          <button onClick={clearFilters} className="btn-primary">
            Xóa bộ lọc
          </button>
        </div>
      )}
    </div>
  );
};

export default Books;
