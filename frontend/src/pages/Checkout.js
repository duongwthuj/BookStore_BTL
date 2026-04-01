import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import { useAuth } from '../contexts/AuthContext';
import orderService from '../services/orderService';
import paymentService from '../services/paymentService';
import LoadingSpinner from '../components/LoadingSpinner';

const Checkout = () => {
  const { cartItems, cartTotal, clearCart } = useCart();
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Debug log on render
  console.log('=== CHECKOUT RENDER ===');
  console.log('isAuthenticated:', isAuthenticated);
  console.log('user:', user);
  console.log('cartItems:', cartItems);
  console.log('cartTotal:', cartTotal);

  const [formData, setFormData] = useState({
    firstName: user?.first_name || '',
    lastName: user?.last_name || '',
    email: user?.email || '',
    phone: user?.phone || '',
    address: '',
    district: '',
    city: '',
    paymentMethod: 'cod',
    saveAddress: false,
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [step, setStep] = useState(1);
  const [paymentInfo, setPaymentInfo] = useState(null); // For MoMo QR code

  // Update formData when user loads
  React.useEffect(() => {
    if (user) {
      setFormData(prev => ({
        ...prev,
        firstName: prev.firstName || user.first_name || '',
        lastName: prev.lastName || user.last_name || '',
        email: prev.email || user.email || '',
        phone: prev.phone || user.phone || '',
      }));
    }
  }, [user]);

  const formatPrice = (price) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND',
    }).format(price);
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const validateShipping = () => {
    if (!formData.firstName || !formData.lastName || !formData.email ||
        !formData.phone || !formData.address || !formData.district || !formData.city) {
      setError('Vui long dien day du thong tin');
      return false;
    }
    return true;
  };

  const handleNextStep = () => {
    setError('');
    if (step === 1 && validateShipping()) {
      setStep(2);
    } else if (step === 2) {
      setStep(3);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('=== CHECKOUT START ===');
    console.log('User:', user);
    console.log('Cart items:', cartItems);
    console.log('Form data:', formData);

    setLoading(true);
    setError('');

    try {
      // Validate cart items
      if (!cartItems || cartItems.length === 0) {
        setError('Giỏ hàng trống. Vui lòng thêm sản phẩm.');
        setLoading(false);
        return;
      }

      // Build full shipping address string
      const shippingAddressStr = `${formData.firstName || ''} ${formData.lastName || ''}, ${formData.address || ''}, ${formData.district || ''}, ${formData.city || ''}`.trim();

      console.log('Shipping address:', shippingAddressStr);
      console.log('Phone:', formData.phone);

      let customerId = user?.id;
      if (!customerId) {
        try {
          const storedUser = JSON.parse(localStorage.getItem('user') || '{}');
          customerId = storedUser.id;
        } catch (e) {
          console.error('Failed to parse user from localStorage');
        }
      }

      console.log('Customer ID:', customerId);

      if (!customerId) {
        setError('Vui lòng đăng nhập lại để tiếp tục.');
        setLoading(false);
        return;
      }

      // Calculate shipping cost
      const currentShippingCost = cartTotal >= 300000 ? 0 : 30000;

      const orderData = {
        customer_id: Number(customerId),
        shipping_address: shippingAddressStr,
        phone: formData.phone || '',
        note: '',
        coupon_code: '',
        payment_method: formData.paymentMethod || 'cod',
        shipping_method: currentShippingCost === 0 ? 'free' : 'standard',
        shipping_fee: currentShippingCost.toString(),
        items: cartItems.map((item) => {
          const bookId = item.book?.id || item.book_id || item.id;
          const bookTitle = item.book?.title || item.title || 'Unknown';
          const bookPrice = item.book?.price || item.price || 0;
          return {
            book_id: Number(bookId),
            book_title: bookTitle,
            quantity: Number(item.quantity),
            price: String(bookPrice),
          };
        }),
      };

      console.log('Order data:', JSON.stringify(orderData, null, 2));
      console.log('Cart items:', JSON.stringify(cartItems, null, 2));
      const response = await orderService.createOrder(orderData);
      const orderId = response.data.id;
      const orderTotal = response.data.total;

      // Handle MoMo payment
      if (formData.paymentMethod === 'momo') {
        console.log('=== MOMO PAYMENT ===');
        console.log('Order ID:', orderId);
        console.log('Order Total:', orderTotal);
        try {
          const paymentResponse = await paymentService.createMoMoPayment(orderId, parseFloat(orderTotal));
          console.log('Payment response:', paymentResponse.data);

          const paymentData = {
            orderId,
            payUrl: paymentResponse.data.pay_url,
            qrCodeUrl: paymentResponse.data.qr_code_url,
            deeplink: paymentResponse.data.deeplink,
          };
          console.log('Payment data:', paymentData);

          setPaymentInfo(paymentData);
          await clearCart();
          setLoading(false);
          setStep(4); // Show payment step
          return; // Don't navigate away
        } catch (paymentErr) {
          console.error('Payment error:', paymentErr);
          console.error('Payment error response:', paymentErr.response?.data);
          // Order created but payment failed - redirect to order page
          await clearCart();
          navigate(`/orders/${orderId}?payment_pending=true`);
          return;
        }
      }

      // COD or other methods - go directly to order page
      await clearCart();
      navigate(`/orders/${orderId}?success=true`);
    } catch (err) {
      console.error('=== ORDER ERROR ===');
      console.error('Full error:', err);
      console.error('Response:', err.response);
      console.error('Response data:', err.response?.data);
      const errorData = err.response?.data;
      let errorMsg = 'Dat hang that bai. Vui long thu lai.';
      if (errorData) {
        if (typeof errorData === 'string') {
          errorMsg = errorData;
        } else if (errorData.error) {
          errorMsg = errorData.error;
        } else if (errorData.message) {
          errorMsg = errorData.message;
        } else {
          // Show field errors
          errorMsg = Object.entries(errorData)
            .map(([key, val]) => `${key}: ${Array.isArray(val) ? val.join(', ') : val}`)
            .join('; ');
        }
      }
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const shippingCost = cartTotal >= 300000 ? 0 : 30000;
  const total = cartTotal + shippingCost;

  if (!isAuthenticated) {
    navigate('/login?redirect=/checkout');
    return null;
  }

  // Only show empty cart message if NOT on payment step
  if (cartItems.length === 0 && step !== 4) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Gio hang trong</h1>
        <p className="text-gray-500 mb-6">Them sach vao gio hang truoc khi thanh toan.</p>
        <Link to="/books" className="btn-primary">
          Xem Sach
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Thanh Toan</h1>

      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-center">
          {[
            { num: 1, label: 'Giao hang' },
            { num: 2, label: 'Thanh toan' },
            { num: 3, label: 'Xac nhan' },
          ].map((s, i) => (
            <React.Fragment key={s.num}>
              <div
                className={`flex items-center ${
                  step >= s.num ? 'text-primary-600' : 'text-gray-400'
                }`}
              >
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                    step >= s.num
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-200 text-gray-500'
                  }`}
                >
                  {step > s.num ? (
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    s.num
                  )}
                </div>
                <span className="ml-2 font-medium hidden sm:block">{s.label}</span>
              </div>
              {i < 2 && (
                <div
                  className={`w-16 sm:w-24 h-1 mx-2 sm:mx-4 ${
                    step > s.num ? 'bg-primary-600' : 'bg-gray-200'
                  }`}
                />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Form Section */}
        <div className="lg:col-span-2">
          <form onSubmit={handleSubmit}>
            {/* Step 1: Shipping */}
            {step === 1 && (
              <div className="bg-white rounded-xl shadow-md p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-6">
                  Thong Tin Giao Hang
                </h2>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Ho *
                    </label>
                    <input
                      type="text"
                      name="firstName"
                      value={formData.firstName}
                      onChange={handleInputChange}
                      className="input-field"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Ten *
                    </label>
                    <input
                      type="text"
                      name="lastName"
                      value={formData.lastName}
                      onChange={handleInputChange}
                      className="input-field"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Email *
                    </label>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      className="input-field"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      So Dien Thoai *
                    </label>
                    <input
                      type="tel"
                      name="phone"
                      value={formData.phone}
                      onChange={handleInputChange}
                      className="input-field"
                      placeholder="0901234567"
                      required
                    />
                  </div>
                  <div className="sm:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Dia Chi *
                    </label>
                    <input
                      type="text"
                      name="address"
                      value={formData.address}
                      onChange={handleInputChange}
                      className="input-field"
                      placeholder="So nha, ten duong"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Quan/Huyen *
                    </label>
                    <input
                      type="text"
                      name="district"
                      value={formData.district}
                      onChange={handleInputChange}
                      className="input-field"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Tinh/Thanh Pho *
                    </label>
                    <select
                      name="city"
                      value={formData.city}
                      onChange={handleInputChange}
                      className="input-field"
                      required
                    >
                      <option value="">Chon tinh/thanh pho</option>
                      <option value="Ho Chi Minh">TP. Ho Chi Minh</option>
                      <option value="Ha Noi">Ha Noi</option>
                      <option value="Da Nang">Da Nang</option>
                      <option value="Hai Phong">Hai Phong</option>
                      <option value="Can Tho">Can Tho</option>
                      <option value="Binh Duong">Binh Duong</option>
                      <option value="Dong Nai">Dong Nai</option>
                      <option value="Khanh Hoa">Khanh Hoa</option>
                      <option value="Lam Dong">Lam Dong</option>
                      <option value="Thua Thien Hue">Thua Thien Hue</option>
                    </select>
                  </div>
                </div>

                <div className="mt-6">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      name="saveAddress"
                      checked={formData.saveAddress}
                      onChange={handleInputChange}
                      className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                    />
                    <span className="ml-2 text-sm text-gray-600">
                      Luu dia chi nay cho don hang sau
                    </span>
                  </label>
                </div>

                <div className="mt-6 flex justify-end">
                  <button
                    type="button"
                    onClick={handleNextStep}
                    className="btn-primary"
                  >
                    Tiep Tuc Thanh Toan
                  </button>
                </div>
              </div>
            )}

            {/* Step 2: Payment */}
            {step === 2 && (
              <div className="bg-white rounded-xl shadow-md p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-6">
                  Phuong Thuc Thanh Toan
                </h2>

                <div className="space-y-4">
                  <label className="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                    <input
                      type="radio"
                      name="paymentMethod"
                      value="cod"
                      checked={formData.paymentMethod === 'cod'}
                      onChange={handleInputChange}
                      className="w-4 h-4 text-primary-600"
                    />
                    <span className="ml-3 font-medium">Thanh toan khi nhan hang (COD)</span>
                  </label>

                  <label className="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                    <input
                      type="radio"
                      name="paymentMethod"
                      value="bank"
                      checked={formData.paymentMethod === 'bank'}
                      onChange={handleInputChange}
                      className="w-4 h-4 text-primary-600"
                    />
                    <span className="ml-3 font-medium">Chuyen khoan ngan hang</span>
                  </label>

                  {formData.paymentMethod === 'bank' && (
                    <div className="ml-7 p-4 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-700">
                        <strong>Ngan hang:</strong> Vietcombank<br />
                        <strong>So tai khoan:</strong> 1234567890<br />
                        <strong>Chu tai khoan:</strong> Nha Sach Online<br />
                        <strong>Noi dung:</strong> [Ma don hang] - [So dien thoai]
                      </p>
                    </div>
                  )}

                  <label className="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                    <input
                      type="radio"
                      name="paymentMethod"
                      value="momo"
                      checked={formData.paymentMethod === 'momo'}
                      onChange={handleInputChange}
                      className="w-4 h-4 text-primary-600"
                    />
                    <span className="ml-3 font-medium">Vi MoMo</span>
                  </label>

                  <label className="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                    <input
                      type="radio"
                      name="paymentMethod"
                      value="vnpay"
                      checked={formData.paymentMethod === 'vnpay'}
                      onChange={handleInputChange}
                      className="w-4 h-4 text-primary-600"
                    />
                    <span className="ml-3 font-medium">VNPay</span>
                  </label>
                </div>

                <div className="mt-6 flex justify-between">
                  <button
                    type="button"
                    onClick={() => setStep(1)}
                    className="btn-secondary"
                  >
                    Quay Lai
                  </button>
                  <button
                    type="button"
                    onClick={handleNextStep}
                    className="btn-primary"
                  >
                    Xem Lai Don Hang
                  </button>
                </div>
              </div>
            )}

            {/* Step 3: Review */}
            {step === 3 && (
              <div className="bg-white rounded-xl shadow-md p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-6">
                  Xac Nhan Don Hang
                </h2>

                {/* Shipping Summary */}
                <div className="mb-6 pb-6 border-b">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-medium text-gray-900">Dia Chi Giao Hang</h3>
                    <button
                      type="button"
                      onClick={() => setStep(1)}
                      className="text-primary-600 text-sm hover:text-primary-700"
                    >
                      Sua
                    </button>
                  </div>
                  <p className="text-gray-600">
                    {formData.firstName} {formData.lastName}<br />
                    {formData.address}<br />
                    {formData.district}, {formData.city}<br />
                    {formData.phone}<br />
                    {formData.email}
                  </p>
                </div>

                {/* Payment Summary */}
                <div className="mb-6 pb-6 border-b">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-medium text-gray-900">Phuong Thuc Thanh Toan</h3>
                    <button
                      type="button"
                      onClick={() => setStep(2)}
                      className="text-primary-600 text-sm hover:text-primary-700"
                    >
                      Sua
                    </button>
                  </div>
                  <p className="text-gray-600">
                    {formData.paymentMethod === 'cod' && 'Thanh toan khi nhan hang (COD)'}
                    {formData.paymentMethod === 'bank' && 'Chuyen khoan ngan hang'}
                    {formData.paymentMethod === 'momo' && 'Vi MoMo'}
                    {formData.paymentMethod === 'vnpay' && 'VNPay'}
                  </p>
                </div>

                {/* Items Summary */}
                <div className="mb-6">
                  <h3 className="font-medium text-gray-900 mb-4">San Pham</h3>
                  <div className="space-y-3">
                    {cartItems.map((item) => (
                      <div key={item.book.id} className="flex items-center justify-between">
                        <div className="flex items-center">
                          <span className="text-gray-600">
                            {item.book.title} x {item.quantity}
                          </span>
                        </div>
                        <span className="font-medium">
                          {formatPrice(item.book.price * item.quantity)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mt-6 flex justify-between">
                  <button
                    type="button"
                    onClick={() => setStep(2)}
                    className="btn-secondary"
                  >
                    Quay Lai
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="btn-primary"
                  >
                    {loading ? <LoadingSpinner size="small" /> : 'Dat Hang'}
                  </button>
                </div>
              </div>
            )}

            {/* Step 4: MoMo Payment */}
            {step === 4 && paymentInfo && (
              <div className="bg-white rounded-xl shadow-md p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-6 text-center">
                  Thanh Toan MoMo
                </h2>

                <div className="text-center">
                  <p className="text-gray-600 mb-4">
                    Quet ma QR bang ung dung MoMo de thanh toan
                  </p>

                  {/* QR Code */}
                  <div className="flex justify-center mb-6">
                    <div className="p-4 bg-white border-2 border-pink-500 rounded-lg">
                      <img
                        src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(paymentInfo.deeplink || paymentInfo.payUrl)}`}
                        alt="MoMo QR Code"
                        className="w-48 h-48"
                      />
                    </div>
                  </div>

                  <p className="text-sm text-gray-500 mb-4">
                    Ma don hang: <span className="font-bold">#{paymentInfo.orderId}</span>
                  </p>

                  {/* Open MoMo App Button */}
                  <a
                    href={paymentInfo.deeplink || paymentInfo.payUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block w-full bg-pink-500 text-white py-3 px-6 rounded-lg font-medium hover:bg-pink-600 mb-3"
                  >
                    Mo Ung Dung MoMo
                  </a>

                  {/* Pay via Web */}
                  <a
                    href={paymentInfo.payUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block w-full border border-pink-500 text-pink-500 py-3 px-6 rounded-lg font-medium hover:bg-pink-50 mb-4"
                  >
                    Thanh Toan Qua Web
                  </a>

                  {/* Demo: Simulate Payment Success */}
                  <div className="bg-yellow-50 border border-yellow-300 rounded-lg p-4 mb-6">
                    <p className="text-sm text-yellow-800 mb-3">
                      <strong>CHE DO DEMO:</strong> Bam nut ben duoi de gia lap thanh toan thanh cong
                    </p>
                    <button
                      onClick={async () => {
                        try {
                          await orderService.updateStatus(paymentInfo.orderId, 'paid');
                          navigate(`/orders/${paymentInfo.orderId}?success=true`);
                        } catch (err) {
                          console.error('Error updating order:', err);
                          alert('Loi cap nhat trang thai don hang');
                        }
                      }}
                      className="w-full bg-green-500 text-white py-3 px-6 rounded-lg font-medium hover:bg-green-600"
                    >
                      Gia Lap Thanh Toan Thanh Cong
                    </button>
                  </div>

                  <div className="border-t pt-4">
                    <button
                      onClick={() => navigate(`/orders/${paymentInfo.orderId}`)}
                      className="text-primary-600 hover:text-primary-700 font-medium"
                    >
                      Xem Chi Tiet Don Hang
                    </button>
                  </div>
                </div>
              </div>
            )}
          </form>
        </div>

        {/* Order Summary Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl shadow-md p-6 sticky top-24">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Tom Tat Don Hang
            </h2>

            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Tam tinh ({cartItems.length} san pham)</span>
                <span className="font-medium">{formatPrice(cartTotal)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Phi van chuyen</span>
                {shippingCost === 0 ? (
                  <span className="text-green-600 font-medium">MIEN PHI</span>
                ) : (
                  <span className="font-medium">{formatPrice(shippingCost)}</span>
                )}
              </div>
              <div className="border-t pt-3 mt-3">
                <div className="flex justify-between text-lg font-semibold">
                  <span>Tong cong</span>
                  <span className="text-primary-600">{formatPrice(total)}</span>
                </div>
              </div>
            </div>

            {/* Cart Items Preview */}
            <div className="mt-6 pt-6 border-t">
              <h3 className="text-sm font-medium text-gray-900 mb-3">
                San pham trong don
              </h3>
              <div className="space-y-3 max-h-60 overflow-y-auto">
                {cartItems.map((item) => (
                  <div key={item.book.id} className="flex items-center space-x-3">
                    <div className="w-12 h-16 bg-gray-100 rounded overflow-hidden flex-shrink-0">
                      {item.book.image ? (
                        <img
                          src={item.book.image}
                          alt={item.book.title}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full bg-primary-100" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {item.book.title}
                      </p>
                      <p className="text-sm text-gray-500">SL: {item.quantity}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Checkout;
