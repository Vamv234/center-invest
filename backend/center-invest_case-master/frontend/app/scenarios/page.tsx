'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface Scenario {
  id: number;
  title: string;
  description: string;
  context: string;
  attack_type: string;
  difficulty: string;
}

export default function ScenariosPage() {
  const { user, token } = useAuth();
  const router = useRouter();
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    if (!user || !token) {
      router.push('/login');
      return;
    }

    const fetchScenarios = async () => {
      try {
        const response = await axios.get(`${API_BASE}/scenarios`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setScenarios(response.data);
      } catch (error) {
        console.error('Failed to fetch scenarios:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchScenarios();
  }, [user, token, router]);

  const filteredScenarios = filter
    ? scenarios.filter((s) => s.difficulty === filter)
    : scenarios;

  const difficultyColors: Record<string, string> = {
    beginner: 'bg-green-500',
    intermediate: 'bg-yellow-500',
    advanced: 'bg-red-500',
  };

  const attackTypeEmojis: Record<string, string> = {
    phishing: '🎣',
    skimming: '💳',
    brute_force: '🔓',
    social_engineering: '👥',
    deepfake: '🎭',
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-white text-2xl">Loading scenarios...</div>
      </main>
    );
  }

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
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-white mb-2">Attack Scenarios</h1>
          <p className="text-green-300">Choose a scenario and test your cybersecurity knowledge</p>
        </div>

        {/* Filter */}
        <div className="mb-8 flex gap-4">
          <button
            onClick={() => setFilter('')}
            className={`px-4 py-2 rounded-lg font-semibold transition ${
              filter === ''
                ? 'bg-green-500 text-black'
                : 'bg-black/30 border border-green-500/30 text-green-300 hover:border-green-500/50'
            }`}
          >
            All Levels
          </button>
          {['beginner', 'intermediate', 'advanced'].map((d) => (
            <button
              key={d}
              onClick={() => setFilter(d)}
              className={`px-4 py-2 rounded-lg font-semibold transition capitalize ${
                filter === d
                  ? 'bg-green-500 text-black'
                  : 'bg-black/30 border border-green-500/30 text-green-300 hover:border-green-500/50'
              }`}
            >
              {d}
            </button>
          ))}
        </div>

        {/* Scenarios Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredScenarios.map((scenario) => (
            <div
              key={scenario.id}
              className="bg-black/30 backdrop-blur-sm p-6 rounded-lg border border-green-500/30 hover:border-green-500/50 transition"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="text-3xl">
                  {attackTypeEmojis[scenario.attack_type] || '⚠️'}
                </div>
                <span className={`${difficultyColors[scenario.difficulty]} text-black text-xs font-bold px-2 py-1 rounded capitalize`}>
                  {scenario.difficulty}
                </span>
              </div>

              <h2 className="text-xl font-bold text-white mb-2">{scenario.title}</h2>
              <p className="text-green-300/70 mb-4">{scenario.description}</p>

              <div className="flex gap-2 mb-4">
                <span className="inline-block bg-black/30 border border-green-500/30 text-green-300/70 text-xs px-3 py-1 rounded">
                  {scenario.context}
                </span>
                <span className="inline-block bg-black/30 border border-green-500/30 text-green-300/70 text-xs px-3 py-1 rounded">
                  {scenario.attack_type}
                </span>
              </div>

              <Link
                href={`/game/${scenario.id}`}
                className="w-full bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-black font-bold py-2 rounded-lg text-center transition block"
              >
                Start Scenario →
              </Link>
            </div>
          ))}
        </div>

        {filteredScenarios.length === 0 && (
          <div className="text-center py-12">
            <p className="text-cyan-100 text-xl">No scenarios found for this difficulty level</p>
          </div>
        )}
      </div>
    </main>
  );
}
