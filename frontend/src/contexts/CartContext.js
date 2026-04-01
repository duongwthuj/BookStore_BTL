import React, { createContext, useContext, useState, useEffect } from 'react';
import cartService from '../services/cartService';
import { useAuth } from './AuthContext';

const CartContext = createContext(null);

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};

export const CartProvider = ({ children }) => {
  const [cartItems, setCartItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      fetchCart();
    } else {
      // Load from localStorage for guests
      const localCart = localStorage.getItem('cart');
      if (localCart) {
        try {
          setCartItems(JSON.parse(localCart));
        } catch (e) {
          setCartItems([]);
        }
      }
    }
  }, [isAuthenticated]);

  const fetchCart = async () => {
    try {
      setLoading(true);
      const response = await cartService.getCart();
      setCartItems(response.data.items || []);
    } catch (error) {
      console.error('Error fetching cart:', error);
    } finally {
      setLoading(false);
    }
  };

  const addToCart = async (book, quantity = 1) => {
    if (isAuthenticated) {
      try {
        setLoading(true);
        await cartService.addItem(book.id, quantity);
        await fetchCart();
        return { success: true };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.message || 'Failed to add to cart'
        };
      } finally {
        setLoading(false);
      }
    } else {
      // Guest cart - store in localStorage
      const existingItem = cartItems.find(item => item.book.id === book.id);
      let newItems;

      if (existingItem) {
        newItems = cartItems.map(item =>
          item.book.id === book.id
            ? { ...item, quantity: item.quantity + quantity }
            : item
        );
      } else {
        newItems = [...cartItems, { book, quantity }];
      }

      setCartItems(newItems);
      localStorage.setItem('cart', JSON.stringify(newItems));
      return { success: true };
    }
  };

  const updateQuantity = async (itemId, quantity) => {
    if (quantity < 1) return removeFromCart(itemId);

    if (isAuthenticated) {
      try {
        setLoading(true);
        await cartService.updateItem(itemId, quantity);
        await fetchCart();
        return { success: true };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.message || 'Failed to update cart'
        };
      } finally {
        setLoading(false);
      }
    } else {
      const newItems = cartItems.map(item =>
        item.book.id === itemId ? { ...item, quantity } : item
      );
      setCartItems(newItems);
      localStorage.setItem('cart', JSON.stringify(newItems));
      return { success: true };
    }
  };

  const removeFromCart = async (itemId) => {
    if (isAuthenticated) {
      try {
        setLoading(true);
        await cartService.removeItem(itemId);
        await fetchCart();
        return { success: true };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.message || 'Failed to remove from cart'
        };
      } finally {
        setLoading(false);
      }
    } else {
      const newItems = cartItems.filter(item => item.book.id !== itemId);
      setCartItems(newItems);
      localStorage.setItem('cart', JSON.stringify(newItems));
      return { success: true };
    }
  };

  const clearCart = async () => {
    if (isAuthenticated) {
      try {
        setLoading(true);
        await cartService.clearCart();
        setCartItems([]);
        return { success: true };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.message || 'Failed to clear cart'
        };
      } finally {
        setLoading(false);
      }
    } else {
      setCartItems([]);
      localStorage.removeItem('cart');
      return { success: true };
    }
  };

  const cartTotal = cartItems.reduce(
    (total, item) => total + (parseFloat(item.book?.price || 0) * item.quantity),
    0
  );

  const cartCount = cartItems.reduce((count, item) => count + item.quantity, 0);

  const value = {
    cartItems,
    loading,
    addToCart,
    updateQuantity,
    removeFromCart,
    clearCart,
    fetchCart,
    cartTotal,
    cartCount,
  };

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
};

export default CartContext;
