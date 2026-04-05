'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../context/AuthContext';
import Link from 'next/link';

const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

const validatePassword = (password: string): { valid: boolean; message: string } => {
  if (password.length < 8) {
    return { valid: false, message: 'Password must be at least 8 characters long' };
  }
  if (password.length > 128) {
    return { valid: false, message: 'Password must not exceed 128 characters' };
  }
  if (!/[a-z]/i.test(password)) {
    return { valid: false, message: 'Password must contain at least one letter (a-z)' };
  }
  if (!/[0-9]/.test(password)) {
    return { valid: false, message: 'Password must contain at least one number (0-9)' };
  }
  if (!/[~!@#$%^&*]/.test(password)) {
    return { valid: false, message: 'Password must contain at least one special character (~!@#$%^&*)' };
  }
  return { valid: true, message: '' };
};

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validate email
    if (!validateEmail(email)) {
      setError('Please enter a valid email address (e.g., user@domain.com)');
      return;
    }

    // Validate password
    const passwordValidation = validatePassword(password);
    if (!passwordValidation.valid) {
      setError(passwordValidation.message);
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      await register(email, username, password);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 flex items-center justify-center">
      <div className="bg-black/30 backdrop-blur-md p-8 rounded-lg border border-green-500/30 w-full max-w-md">
        <h1 className="text-3xl font-bold text-white mb-2">Create Account</h1>
        <p className="text-green-300 mb-6">Start your cybersecurity learning journey</p>

        {error && (
          <div className="bg-red-500 bg-opacity-20 border border-red-500 text-red-200 p-3 rounded-lg mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-white font-semibold mb-2">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 bg-black/30 border border-green-500/30 rounded-lg text-white placeholder-green-300/50 focus:outline-none focus:border-green-400"
              placeholder="you@example.com"
              required
            />
          </div>

          <div>
            <label className="block text-white font-semibold mb-2">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-2 bg-black/30 border border-green-500/30 rounded-lg text-white placeholder-green-300/50 focus:outline-none focus:border-green-400"
              placeholder="your_username"
              required
            />
          </div>

          <div>
            <label className="block text-white font-semibold mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 bg-black/30 border border-green-500/30 rounded-lg text-white placeholder-green-300/50 focus:outline-none focus:border-green-400"
              placeholder="••••••••"
              required
            />
          </div>

          <div>
            <label className="block text-white font-semibold mb-2">Confirm Password</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full px-4 py-2 bg-black/30 border border-green-500/30 rounded-lg text-white placeholder-green-300/50 focus:outline-none focus:border-green-400"
              placeholder="••••••••"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 disabled:opacity-50 text-black font-bold py-2 rounded-lg transition"
          >
            {loading ? 'Creating Account...' : 'Register'}
          </button>
        </form>

        <p className="text-center text-green-300/70 mt-6">
          Already have an account?{' '}
          <Link href="/login" className="text-green-400 hover:text-green-300 font-semibold">
            Sign in here
          </Link>
        </p>
      </div>
    </main>
  );
}
