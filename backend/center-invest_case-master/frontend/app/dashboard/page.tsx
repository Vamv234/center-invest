'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '../context/AuthContext';
import { TrophyIcon, StatsIcon, RankBadge, AccuracyMeter } from '../../components/Icons';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface Stats {
  total_scenarios_completed: number;
  total_scenarios_attempted: number;
  average_security_level: number;
  total_correct_choices: number;
  total_choices: number;
  accuracy: number;
  certificates_earned: number;
  rank: string;
}

export default function DashboardPage() {
  const { user, token, logout } = useAuth();
  const router = useRouter();
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user || !token) {
      router.push('/login');
      return;
    }

    const fetchStats = async () => {
      try {
        const response = await axios.get(`${API_BASE}/user/stats`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setStats(response.data);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [user, token, router]);

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-white text-2xl">Loading...</div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950">
      {/* Navigation */}
      <nav className="bg-black/30 backdrop-blur-md border-b border-green-500/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <Link href="/" className="text-2xl font-bold text-white">🛡️ DPS</Link>
          <div className="flex gap-4 items-center">
            <span className="text-green-300">Welcome, <span className="font-bold">{user?.username}</span>!</span>
            <button
              onClick={handleLogout}
              className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-white mb-2">Your Security Dashboard</h1>
          <p className="text-green-300">Track your progress and improve your cybersecurity skills</p>
        </div>

        {/* Stats Grid */}
        <div className="grid md:grid-cols-4 gap-6 mb-12">
          <div className="bg-black/30 backdrop-blur-sm p-6 rounded-lg border border-green-500/30">
            <div className="flex items-center gap-4">
              <div className="text-green-400">
                <RankBadge rank={stats?.rank || 'Beginner'} />
              </div>
              <div>
                <p className="text-green-300/70 text-sm">Current Rank</p>
              </div>
            </div>
          </div>

          <div className="bg-black/30 backdrop-blur-sm p-6 rounded-lg border border-green-500/30">
            <div className="flex items-center gap-4">
              <div className="text-green-400">
                <TrophyIcon />
              </div>
              <div>
                <div className="text-2xl font-bold text-green-400">{stats?.total_scenarios_completed}</div>
                <p className="text-green-300/70 text-sm">Completed</p>
              </div>
            </div>
          </div>

          <div className="bg-black/30 backdrop-blur-sm p-6 rounded-lg border border-yellow-500/30">
            <div className="flex items-center gap-4">
              <div className="text-yellow-400">
                <StatsIcon />
              </div>
              <div>
                <div className="text-2xl font-bold text-yellow-400">{stats?.accuracy.toFixed(1)}%</div>
                <p className="text-yellow-300/70 text-sm">Accuracy</p>
              </div>
            </div>
          </div>

          <div className="bg-black/30 backdrop-blur-sm p-6 rounded-lg border border-pink-500/30">
            <div className="text-2xl font-bold text-pink-400">{stats?.certificates_earned}</div>
            <p className="text-pink-300/70 text-sm">Certificates</p>
          </div>
        </div>

        {/* Detailed Stats */}
        <div className="grid md:grid-cols-2 gap-6 mb-12">
          <div className="bg-black/30 backdrop-blur-sm p-6 rounded-lg border border-green-500/30">
            <h2 className="text-xl font-bold text-white mb-4">Performance Metrics</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-green-300/70">Average Security Level</span>
                <span className="font-bold text-white">{stats?.average_security_level.toFixed(1)}/100</span>
              </div>
              <div className="flex justify-between">
                <span className="text-green-300/70">Correct Answers</span>
                <span className="font-bold text-white">{stats?.total_correct_choices}/{stats?.total_choices}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-green-300/70">Scenarios Attempted</span>
                <span className="font-bold text-white">{stats?.total_scenarios_attempted}</span>
              </div>
            </div>
          </div>

          <div className="bg-black/30 backdrop-blur-sm p-6 rounded-lg border border-green-500/30">
            <h2 className="text-xl font-bold text-white mb-4">Your Progress</h2>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-green-300/70">Overall Progress</span>
                  <span className="text-white font-bold">{((stats?.total_scenarios_completed || 0) / 5 * 100).toFixed(0)}%</span>
                </div>
                <div className="h-3 bg-black/40 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-green-500 to-emerald-500"
                    style={{ width: `${((stats?.total_scenarios_completed || 0) / 5 * 100).toFixed(0)}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="grid md:grid-cols-3 gap-6">
          <Link
            href="/scenarios"
            className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-black px-6 py-4 rounded-lg font-bold text-center transition block flex items-center justify-center gap-2"
          >
            <span>🎮</span> Continue Learning
          </Link>
          <Link
            href="/certificates"
            className="bg-gradient-to-r from-pink-500 to-rose-600 hover:from-pink-600 hover:to-rose-700 text-black px-6 py-4 rounded-lg font-bold text-center transition block flex items-center justify-center gap-2"
          >
            <TrophyIcon /> View Certificates
          </Link>
          <Link
            href="/progress"
            className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-black px-6 py-4 rounded-lg font-bold text-center transition block flex items-center justify-center gap-2"
          >
            <StatsIcon /> Detailed Progress
          </Link>
        </div>
      </div>
    </main>
  );
}
