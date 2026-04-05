'use client';

import { createContext, useContext, useState, ReactNode } from 'react';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface User {
  id: number;
  email: string;
  username: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/auth/login`, {
        email,
        password,
      });
      setToken(response.data.access_token);
      setUser({
        id: response.data.id,
        email: response.data.email,
        username: response.data.username,
      });
      localStorage.setItem('token', response.data.access_token);
    } finally {
      setLoading(false);
    }
  };

  const register = async (email: string, username: string, password: string) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/auth/register`, {
        email,
        username,
        password,
      });
      setToken(response.data.access_token);
      setUser({
        id: response.data.id,
        email: response.data.email,
        username: response.data.username,
      });
      localStorage.setItem('token', response.data.access_token);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
