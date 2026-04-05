'use client';

import Link from 'next/link';
import { useAuth } from './context/AuthContext';

export default function Home() {
  const { user } = useAuth();

  return (
    <main className="min-h-screen bg-slate-950">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-slate-950/80 backdrop-blur-xl border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-green-400 to-emerald-600 rounded-lg flex items-center justify-center text-black font-bold">⚔️</div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-green-400 via-emerald-400 to-green-300 bg-clip-text text-transparent">CyberShield Pro</h1>
          </div>
          <div className="flex gap-4 items-center">
            {user ? (
              <>
                <span className="text-slate-300 text-sm font-medium">Welcome, <span className="text-green-400 font-semibold">{user.username}</span></span>
                <Link href="/dashboard" className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-black px-4 py-2 rounded-lg font-semibold transition-all duration-200 shadow-lg hover:shadow-green-500/50">
                  Dashboard
                </Link>
              </>
            ) : (
              <>
                <Link href="/login" className="text-slate-300 hover:text-white transition-colors duration-200 font-medium">
                  Sign In
                </Link>
                <Link href="/register" className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-black px-4 py-2 rounded-lg font-semibold transition-all duration-200 shadow-lg hover:shadow-green-500/50">
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Animated background elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-green-500/20 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-emerald-500/20 rounded-full blur-3xl animate-pulse delay-700"></div>
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 text-center">
          <div className="mb-6 inline-block">
            <span className="px-4 py-2 bg-green-500/20 border border-green-500/50 rounded-full text-green-300 text-sm font-semibold backdrop-blur-sm">
              🎯 Learn Cybersecurity the Right Way
            </span>
          </div>
          <h2 className="text-6xl font-bold text-white mb-6 leading-tight">
            Master Digital Defense Through<br />
            <span className="bg-gradient-to-r from-green-400 via-emerald-400 to-green-300 bg-clip-text text-transparent">Interactive Scenarios</span>
          </h2>
          <p className="text-xl text-slate-400 mb-10 max-w-2xl mx-auto leading-relaxed">
            Experience real-world cyber threats in a safe environment. Make critical decisions, learn from consequences, and earn certifications that prove your cybersecurity expertise.
          </p>
        
          {!user ? (
            <div className="flex gap-4 justify-center mb-16 flex-col sm:flex-row">
              <Link
                href="/register"
                className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-black px-8 py-4 rounded-lg font-bold text-lg transition-all duration-200 shadow-lg hover:shadow-green-500/50"
              >
                Start Free Trial
              </Link>
              <Link
                href="/login"
                className="border-2 border-green-500/50 text-white hover:border-green-400 hover:bg-green-500/10 px-8 py-4 rounded-lg font-bold text-lg transition-all duration-200 backdrop-blur-sm"
              >
                Sign In
              </Link>
            </div>
          ) : (
            <Link
              href="/scenarios"
              className="inline-block bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-black px-8 py-4 rounded-lg font-bold text-lg transition-all duration-200 shadow-lg hover:shadow-green-500/50"
            >
              Explore Scenarios
            </Link>
          )}
        </div>
      </div>

      {/* Features Grid */}
      <div className="relative py-24 bg-slate-900/50 border-y border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h3 className="text-4xl font-bold text-white mb-4">Why Choose CyberShield?</h3>
            <p className="text-slate-400 text-lg max-w-2xl mx-auto">Everything you need to become a cybersecurity expert</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="group relative bg-gradient-to-br from-black/40 to-black/60 backdrop-blur-xl p-8 rounded-xl border border-green-500/30 hover:border-green-400/50 transition-all duration-300 hover:shadow-lg hover:shadow-green-500/10">
              <div className="absolute inset-0 bg-gradient-to-br from-green-500/10 to-emerald-500/10 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              <div className="relative">
                <div className="text-5xl mb-4">🎮</div>
                <h4 className="text-xl font-bold text-white mb-3">Gamified Learning</h4>
                <p className="text-slate-400 leading-relaxed">
                  Track your progress with a security level system, earn achievements, and climb the ranks from Novice to Expert.
                </p>
              </div>
            </div>

            <div className="group relative bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-xl p-8 rounded-xl border border-slate-700/50 hover:border-purple-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-purple-500/10">
              <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              <div className="relative">
                <div className="text-5xl mb-4">⚡</div>
                <h4 className="text-xl font-bold text-white mb-3">Real-World Scenarios</h4>
                <p className="text-slate-400 leading-relaxed">
                  Encounter phishing, social engineering, brute force attacks in realistic office, home, and public WiFi environments.
                </p>
              </div>
            </div>

            <div className="group relative bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-xl p-8 rounded-xl border border-slate-700/50 hover:border-pink-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-pink-500/10">
              <div className="absolute inset-0 bg-gradient-to-br from-pink-500/10 to-rose-500/10 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              <div className="relative">
                <div className="text-5xl mb-4">🏆</div>
                <h4 className="text-xl font-bold text-white mb-3">Verifiable Certificates</h4>
                <p className="text-slate-400 leading-relaxed">
                  Earn QR-coded certificates proving your cybersecurity expertise to employers, schools, and clients.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Attack Types */}
      <div className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h3 className="text-4xl font-bold text-white mb-4">Defend Against These Threats</h3>
            <p className="text-slate-400 text-lg">Master 5 different attack types across difficulty levels</p>
          </div>
          <div className="grid md:grid-cols-5 gap-4">
            {[
              { name: 'Phishing', icon: '📧', color: 'from-red-500/20 to-red-600/20 border-red-500/50' },
              { name: 'Skimming', icon: '💳', color: 'from-orange-500/20 to-orange-600/20 border-orange-500/50' },
              { name: 'Password Attacks', icon: '🔑', color: 'from-yellow-500/20 to-yellow-600/20 border-yellow-500/50' },
              { name: 'Social Engineering', icon: '🎭', color: 'from-pink-500/20 to-pink-600/20 border-pink-500/50' },
              { name: 'Deepfakes', icon: '🎬', color: 'from-purple-500/20 to-purple-600/20 border-purple-500/50' }
            ].map((attack) => (
              <div key={attack.name} className={`group bg-gradient-to-br ${attack.color} backdrop-blur-xl p-6 rounded-lg border transition-all duration-300 hover:shadow-lg cursor-default`}>
                <div className="text-4xl mb-3 group-hover:scale-110 transition-transform duration-300">{attack.icon}</div>
                <p className="text-white font-semibold text-sm">{attack.name}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-24 px-4">
        <div className="max-w-4xl mx-auto bg-gradient-to-r from-indigo-500/10 to-purple-500/10 backdrop-blur-xl rounded-2xl border border-indigo-500/30 p-12 text-center">
          <h3 className="text-3xl font-bold text-white mb-4">Ready to Become a Cybersecurity Expert?</h3>
          <p className="text-slate-300 mb-8 text-lg">Join thousands learning to defend themselves against real cyber threats</p>
          {!user && (
            <Link
              href="/register"
              className="inline-block bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white px-8 py-4 rounded-lg font-bold text-lg transition-all duration-200 shadow-lg hover:shadow-indigo-500/50"
            >
              Get Started Now
            </Link>
          )}
        </div>
      </div>
    </main>
  );
}
