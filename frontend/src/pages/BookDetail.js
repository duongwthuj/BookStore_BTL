import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import { useAuth } from '../contexts/AuthContext';
import ReviewForm from '../components/ReviewForm';
import ReviewList from '../components/ReviewList';
import LoadingSpinner from '../components/LoadingSpinner';
import BookCard from '../components/BookCard';
import bookService from '../services/bookService';
import reviewService from '../services/reviewService';

const BookDetail = () => {
  const { id } = useParams();
  const { addToCart, loading: cartLoading } = useCart();
  const { isAuthenticated } = useAuth();
  const [book, setBook] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [relatedBooks, setRelatedBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [reviewsLoading, setReviewsLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  const [addedToCart, setAddedToCart] = useState(false);

  const formatPrice = (price) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND',
    }).format(price);
  };

  useEffect(() => {
    fetchBook();
    fetchReviews();
  }, [id]);

  const fetchBook = async () => {
    try {
      setLoading(true);
      const response = await bookService.getBook(id);
      setBook(response.data);

      // Fetch related books
      if (response.data.category) {
        const relatedRes = await bookService.getBooks({
          category_id: response.data.category.id,
          limit: 4,
        });
        const related = (relatedRes.data.results || relatedRes.data || [])
          .filter((b) => b.id !== parseInt(id))
          .slice(0, 4);
        setRelatedBooks(related);
      }
    } catch (error) {
      console.error('Error fetching book:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchReviews = async () => {
    try {
      setReviewsLoading(true);
      const response = await reviewService.getReviews(id);
      setReviews(response.data.results || response.data || []);
    } catch (error) {
      console.error('Error fetching reviews:', error);
    } finally {
      setReviewsLoading(false);
    }
  };

  const handleAddToCart = async () => {
    const result = await addToCart(book, quantity);
    if (result.success) {
      setAddedToCart(true);
      setTimeout(() => setAddedToCart(false), 2000);
    }
  };

  const renderStars = (rating) => {
    return (
      <div className="flex">
        {[1, 2, 3, 4, 5].map((star) => (
          <svg
            key={star}
            className={`w-5 h-5 ${
              star <= Math.round(rating) ? 'text-yellow-400' : 'text-gray-300'
            }`}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
          </svg>
        ))}
      </div>
    );
  };

  if (loading) {
    return <LoadingSpinner fullScreen />;
  }

  if (!book) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Khong Tim Thay Sach</h1>
        <p className="text-gray-500 mb-6">Cuon sach ban dang tim khong ton tai.</p>
        <Link to="/books" className="btn-primary">
          Xem Tat Ca Sach
        </Link>
      </div>
    );
  }

  const discountedPrice = book.discount_percent
    ? book.price * (1 - book.discount_percent / 100)
    : book.price;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Breadcrumb */}
      <nav className="mb-8">
        <ol className="flex items-center space-x-2 text-sm text-gray-500">
          <li>
            <Link to="/" className="hover:text-primary-600">
              Trang chu
            </Link>
          </li>
          <li>/</li>
          <li>
            <Link to="/books" className="hover:text-primary-600">
              Sach
            </Link>
          </li>
          {book.category && (
            <>
              <li>/</li>
              <li>
                <Link
                  to={`/books?category=${book.category.id}`}
                  className="hover:text-primary-600"
                >
                  {book.category.name}
                </Link>
              </li>
            </>
          )}
          <li>/</li>
          <li className="text-gray-900 font-medium truncate max-w-xs">{book.title}</li>
        </ol>
      </nav>

      {/* Book Details */}
      <div className="bg-white rounded-xl shadow-md overflow-hidden mb-12">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 p-6 lg:p-8">
          {/* Image */}
          <div className="relative">
            <div className="aspect-[3/4] bg-gray-100 rounded-lg overflow-hidden">
              {book.image || book.cover_image ? (
                <img
                  src={book.cover_image || book.image}
                  alt={book.title}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-primary-100 to-primary-200">
                  <svg
                    className="w-24 h-24 text-primary-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1}
                      d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                    />
                  </svg>
                </div>
              )}
            </div>
            {book.discount_percent > 0 && (
              <span className="absolute top-4 left-4 bg-red-500 text-white text-sm font-bold px-3 py-1 rounded">
                -{book.discount_percent}%
              </span>
            )}
          </div>

          {/* Details */}
          <div className="flex flex-col">
            <div className="flex-grow">
              {book.category && (
                <Link
                  to={`/books?category=${book.category.id}`}
                  className="text-primary-600 text-sm font-medium uppercase tracking-wide hover:text-primary-700"
                >
                  {book.category.name}
                </Link>
              )}
              <h1 className="text-3xl font-bold text-gray-900 mt-2 mb-2">{book.title}</h1>
              <p className="text-lg text-gray-600 mb-4">Tac gia: {book.author}</p>

              {/* Rating */}
              <div className="flex items-center mb-6">
                {renderStars(book.average_rating || 0)}
                <span className="ml-2 text-gray-600">
                  {(book.average_rating || 0).toFixed(1)} ({book.review_count || 0} danh gia)
                </span>
              </div>

              {/* Price */}
              <div className="mb-6">
                {book.discount_percent > 0 ? (
                  <div className="flex items-center space-x-3">
                    <span className="text-3xl font-bold text-primary-600">
                      {formatPrice(discountedPrice)}
                    </span>
                    <span className="text-xl text-gray-400 line-through">
                      {formatPrice(book.price)}
                    </span>
                    <span className="bg-red-100 text-red-600 text-sm font-medium px-2 py-1 rounded">
                      Tiet kiem {formatPrice(book.price - discountedPrice)}
                    </span>
                  </div>
                ) : (
                  <span className="text-3xl font-bold text-primary-600">
                    {formatPrice(book.price)}
                  </span>
                )}
              </div>

              {/* Stock Status */}
              <div className="mb-6">
                {book.stock > 0 ? (
                  <span className="inline-flex items-center text-green-600">
                    <svg className="w-5 h-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Con hang ({book.stock} cuon)
                  </span>
                ) : (
                  <span className="inline-flex items-center text-red-600">
                    <svg className="w-5 h-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                    Het hang
                  </span>
                )}
              </div>

              {/* Description */}
              <div className="mb-6">
                <h3 className="font-semibold text-gray-900 mb-2">Mo ta</h3>
                <p className="text-gray-600 whitespace-pre-wrap">
                  {book.description || 'Chua co mo ta.'}
                </p>
              </div>

              {/* Book Details */}
              <div className="grid grid-cols-2 gap-4 mb-6 text-sm">
                {book.isbn && (
                  <div>
                    <span className="text-gray-500">ISBN:</span>
                    <span className="ml-2 text-gray-900">{book.isbn}</span>
                  </div>
                )}
                {book.publisher && (
                  <div>
                    <span className="text-gray-500">NXB:</span>
                    <span className="ml-2 text-gray-900">{book.publisher}</span>
                  </div>
                )}
                {book.publication_date && (
                  <div>
                    <span className="text-gray-500">Nam xuat ban:</span>
                    <span className="ml-2 text-gray-900">
                      {new Date(book.publication_date).toLocaleDateString('vi-VN')}
                    </span>
                  </div>
                )}
                {book.pages && (
                  <div>
                    <span className="text-gray-500">So trang:</span>
                    <span className="ml-2 text-gray-900">{book.pages}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Add to Cart */}
            <div className="border-t pt-6">
              <div className="flex items-center space-x-4 mb-4">
                <label className="text-gray-700 font-medium">So luong:</label>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setQuantity((q) => Math.max(1, q - 1))}
                    disabled={quantity <= 1}
                    className="w-8 h-8 flex items-center justify-center rounded-full border border-gray-300 text-gray-600 hover:bg-gray-100 disabled:opacity-50"
                  >
                    -
                  </button>
                  <span className="w-10 text-center font-medium">{quantity}</span>
                  <button
                    onClick={() => setQuantity((q) => Math.min(book.stock || 99, q + 1))}
                    disabled={quantity >= (book.stock || 99)}
                    className="w-8 h-8 flex items-center justify-center rounded-full border border-gray-300 text-gray-600 hover:bg-gray-100 disabled:opacity-50"
                  >
                    +
                  </button>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-4">
                <button
                  onClick={handleAddToCart}
                  disabled={cartLoading || book.stock === 0}
                  className={`flex-1 py-3 px-6 rounded-lg font-semibold transition-colors flex items-center justify-center ${
                    addedToCart
                      ? 'bg-green-600 text-white'
                      : 'bg-primary-600 text-white hover:bg-primary-700'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  {cartLoading ? (
                    <LoadingSpinner size="small" />
                  ) : addedToCart ? (
                    <>
                      <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      Da Them Vao Gio
                    </>
                  ) : (
                    <>
                      <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                      </svg>
                      Them Vao Gio Hang
                    </>
                  )}
                </button>
                <Link
                  to="/cart"
                  className="btn-secondary py-3 px-6 text-center"
                >
                  Xem Gio Hang
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Reviews Section */}
      <div className="mb-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Danh Gia Tu Khach Hang</h2>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <ReviewList reviews={reviews} loading={reviewsLoading} />
          </div>
          <div>
            {isAuthenticated ? (
              <ReviewForm bookId={id} onReviewAdded={fetchReviews} />
            ) : (
              <div className="bg-white rounded-xl shadow-md p-6 text-center">
                <p className="text-gray-600 mb-4">
                  Vui long dang nhap de viet danh gia.
                </p>
                <Link to="/login" className="btn-primary">
                  Dang Nhap
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Related Books */}
      {relatedBooks.length > 0 && (
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Sach Lien Quan</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-6">
            {relatedBooks.map((relatedBook) => (
              <BookCard key={relatedBook.id} book={relatedBook} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default BookDetail;
