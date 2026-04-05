'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '../context/AuthContext';
import { StatsIcon } from '../../components/Icons';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface Progress {
  id: number;
  user_id: number;
  scenario_id: number;
  status: string;
  security_level: number;
  correct_choices: number;
  total_choices: number;
  started_at: string;
  completed_at?: string;
}

export default function ProgressPage() {
  const { user, token } = useAuth();
  const router = useRouter();
  const [progress, setProgress] = useState<Progress[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user || !token) {
      router.push('/login');
      return;
    }

    const fetchProgress = async () => {
      try {
        const response = await axios.get(`${API_BASE}/user/progress`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setProgress(response.data);
      } catch (error) {
        console.error('Failed to fetch progress:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchProgress();
  }, [user, token, router]);

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-white text-2xl">Loading progress...</div>
      </main>
    );
  }

  const statusColors: Record<string, string> = {
    completed: 'bg-green-500',
    in_progress: 'bg-yellow-500',
    failed: 'bg-red-500',
  };

  return (
    <main className="min-h-screen bg-slate-950">
      {/* Navigation */}
      <nav className="bg-black/30 backdrop-blur-md border-b border-green-500/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <Link href="/dashboard" className="text-2xl font-bold text-white">🛡️ DPS</Link>
          <Link href="/dashboard" className="text-green-400 hover:text-green-300">← Back to Dashboard</Link>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex items-center gap-4 mb-8">
          <div className="text-blue-400">
            <StatsIcon />
          </div>
          <h1 className="text-4xl font-bold text-white">Your Progress</h1>
        </div>

        {progress.length === 0 ? (
          <div className="bg-black/30 backdrop-blur-sm p-12 rounded-lg border border-green-500/30 text-center">
            <div className="text-4xl mb-4">📋</div>
            <p className="text-green-300 text-lg">No progress yet!</p>
            <p className="text-green-300/70 mb-6">Start your first scenario to see your progress here.</p>
            <Link href="/scenarios" className="inline-block bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-black px-6 py-2 rounded-lg font-bold">
              Start Learning
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {progress.map((p) => {
              const accuracy = p.total_choices > 0 ? (p.correct_choices / p.total_choices * 100).toFixed(1) : 0;
              return (
                <div key={p.id} className="bg-black/30 backdrop-blur-sm p-6 rounded-lg border border-green-500/30 hover:border-green-500/50 transition">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-xl font-bold text-white">Scenario #{p.scenario_id}</h3>
                      <p className="text-green-300/70">Started: {new Date(p.started_at).toLocaleDateString()}</p>
                    </div>
                    <span className={`${statusColors[p.status]} text-black text-xs font-bold px-3 py-1 rounded capitalize`}>
                      {p.status}
                    </span>
                  </div>

                  <div className="grid grid-cols-4 gap-4">
                    <div className="bg-black/30 border border-green-500/30 p-3 rounded">
                      <div className="text-2xl font-bold text-green-400">{p.security_level}%</div>
                      <p className="text-green-300/70 text-sm">Security Level</p>
                    </div>
                    <div className="bg-black/30 border border-green-500/30 p-3 rounded">
                      <div className="text-2xl font-bold text-green-400">{p.correct_choices}</div>
                      <p className="text-green-300/70 text-sm">Correct Choices</p>
                    </div>
                    <div className="bg-black/30 border border-yellow-500/30 p-3 rounded">
                      <div className="text-2xl font-bold text-yellow-400">{accuracy}%</div>
                      <p className="text-yellow-300/70 text-sm">Accuracy</p>
                    </div>
                    <div className="bg-black/30 border border-green-500/30 p-3 rounded">
                      <div className="text-2xl font-bold text-white">{p.total_choices}</div>
                      <p className="text-green-300/70 text-sm">Total Choices</p>
                    </div>
                  </div>

                  {p.completed_at && (
                    <p className="text-green-300/70 mt-3 text-sm">Completed: {new Date(p.completed_at).toLocaleString()}</p>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </main>
  );
}
