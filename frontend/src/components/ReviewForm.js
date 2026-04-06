import React, { useState } from 'react';
import reviewService from '../services/reviewService';

const ReviewForm = ({ bookId, onReviewAdded }) => {
  const [rating, setRating] = useState(5);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [comment, setComment] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await reviewService.createReview(bookId, {
        rating,
        comment,
      });
      setComment('');
      setRating(5);
      if (onReviewAdded) {
        onReviewAdded();
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Gửi đánh giá thất bại');
    } finally {
      setLoading(false);
    }
  };

  const renderStar = (starIndex) => {
    const isActive = (hoveredRating || rating) >= starIndex;
    return (
      <button
        key={starIndex}
        type="button"
        onClick={() => setRating(starIndex)}
        onMouseEnter={() => setHoveredRating(starIndex)}
        onMouseLeave={() => setHoveredRating(0)}
        className="focus:outline-none"
      >
        <svg
          className={`w-8 h-8 transition-colors ${
            isActive ? 'text-yellow-400' : 'text-gray-300'
          }`}
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
        </svg>
      </button>
    );
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Viết đánh giá</h3>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {/* Rating Stars */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Đánh giá của bạn
          </label>
          <div className="flex space-x-1">
            {[1, 2, 3, 4, 5].map((star) => renderStar(star))}
          </div>
        </div>

        {/* Comment */}
        <div className="mb-4">
          <label
            htmlFor="comment"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Nhận xét của bạn
          </label>
          <textarea
            id="comment"
            rows={4}
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Chia sẻ suy nghĩ của bạn về cuốn sách này..."
            className="input-field resize-none"
            required
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || !comment.trim()}
          className="btn-primary w-full sm:w-auto disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <svg
                className="animate-spin -ml-1 mr-2 h-5 w-5 text-white"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Đang gửi...
            </span>
          ) : (
            'Gửi đánh giá'
          )}
        </button>
      </form>
    </div>
  );
};

export default ReviewForm;
