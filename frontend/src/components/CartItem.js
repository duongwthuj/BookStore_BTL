import React from 'react';
import { Link } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';

const CartItem = ({ item }) => {
  const { updateQuantity, removeFromCart, loading } = useCart();
  const { book, quantity } = item;
  // Use item.id (cart item ID) for authenticated users, or book.id for guest cart
  const itemId = item.id || book.id;

  const formatPrice = (price) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND',
    }).format(price);
  };

  const handleQuantityChange = async (newQuantity) => {
    if (newQuantity >= 1 && newQuantity <= (book.stock || 99)) {
      await updateQuantity(itemId, newQuantity);
    }
  };

  const handleRemove = async () => {
    await removeFromCart(itemId);
  };

  const itemTotal = parseFloat(book.price) * quantity;

  return (
    <div className="flex items-center gap-4 py-4 border-b border-gray-200">
      {/* Book Image */}
      <Link to={`/books/${book.id}`} className="flex-shrink-0">
        <div className="w-20 h-28 bg-gray-100 rounded-lg overflow-hidden">
          {book.image ? (
            <img
              src={book.image}
              alt={book.title}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-primary-100 to-primary-200">
              <svg
                className="w-8 h-8 text-primary-400"
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
      </Link>

      {/* Book Details */}
      <div className="flex-grow min-w-0">
        <Link to={`/books/${book.id}`}>
          <h3 className="font-semibold text-gray-900 hover:text-primary-600 transition-colors line-clamp-1">
            {book.title}
          </h3>
        </Link>
        <p className="text-sm text-gray-500">{book.author}</p>
        <p className="text-primary-600 font-medium mt-1">
          {formatPrice(book.price)}
        </p>
      </div>

      {/* Quantity Controls */}
      <div className="flex items-center space-x-2">
        <button
          onClick={() => handleQuantityChange(quantity - 1)}
          disabled={loading || quantity <= 1}
          className="w-8 h-8 flex items-center justify-center rounded-full border border-gray-300 text-gray-600 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
          </svg>
        </button>
        <span className="w-10 text-center font-medium">{quantity}</span>
        <button
          onClick={() => handleQuantityChange(quantity + 1)}
          disabled={loading || quantity >= (book.stock || 99)}
          className="w-8 h-8 flex items-center justify-center rounded-full border border-gray-300 text-gray-600 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
        </button>
      </div>

      {/* Item Total */}
      <div className="text-right min-w-[100px]">
        <p className="font-semibold text-gray-900">{formatPrice(itemTotal)}</p>
      </div>

      {/* Remove Button */}
      <button
        onClick={handleRemove}
        disabled={loading}
        className="p-2 text-gray-400 hover:text-red-500 transition-colors disabled:opacity-50"
        title="Xoa"
      >
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
          />
        </svg>
      </button>
    </div>
  );
};

export default CartItem;
