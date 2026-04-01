import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { CartProvider } from './contexts/CartContext';

// Layout Components
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ChatWidget from './components/ChatWidget';

// Customer Pages
import Home from './pages/Home';
import Books from './pages/Books';
import BookDetail from './pages/BookDetail';
import Cart from './pages/Cart';
import Checkout from './pages/Checkout';
import Orders from './pages/Orders';
import OrderDetail from './pages/OrderDetail';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';

// Admin Pages
import StaffDashboard from './pages/StaffDashboard';
import StaffBooks from './pages/StaffBooks';
import ManagerDashboard from './pages/ManagerDashboard';

// Layout wrapper for customer pages
const CustomerLayout = ({ children }) => (
  <div className="min-h-screen flex flex-col bg-gray-50">
    <Navbar />
    <main className="flex-grow">
      {children}
    </main>
    <Footer />
    <ChatWidget />
  </div>
);

// Route wrapper to conditionally apply layout
const AppRoutes = () => {
  const location = useLocation();
  const isAdminRoute = location.pathname.startsWith('/staff') || location.pathname.startsWith('/manager');

  if (isAdminRoute) {
    return (
      <Routes>
        <Route path="/staff" element={<StaffDashboard />} />
        <Route path="/staff/books" element={<StaffBooks />} />
        <Route path="/manager" element={<ManagerDashboard />} />
        <Route path="/manager/users" element={<ManagerDashboard />} />
      </Routes>
    );
  }

  return (
    <CustomerLayout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/books" element={<Books />} />
        <Route path="/books/:id" element={<BookDetail />} />
        <Route path="/cart" element={<Cart />} />
        <Route path="/checkout" element={<Checkout />} />
        <Route path="/orders" element={<Orders />} />
        <Route path="/orders/:id" element={<OrderDetail />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/profile" element={<Profile />} />
      </Routes>
    </CustomerLayout>
  );
};

function App() {
  return (
    <AuthProvider>
      <CartProvider>
        <Router>
          <AppRoutes />
        </Router>
      </CartProvider>
    </AuthProvider>
  );
}

export default App;
