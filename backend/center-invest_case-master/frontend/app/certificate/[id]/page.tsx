'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { CertificateIcon, TrophyIcon } from '../../../components/Icons';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface CertificateData {
  id: number;
  user: {
    id: number;
    username: string;
    email: string;
  };
  scenario: {
    id: number;
    title: string;
    description: string;
    attack_type: string;
    difficulty: string;
  };
  achievement: string;
  created_at: string;
  verified: boolean;
}

const difficultyColors: Record<string, string> = {
  beginner: 'from-blue-400 to-blue-600',
  intermediate: 'from-purple-400 to-purple-600',
  advanced: 'from-orange-400 to-orange-600',
  expert: 'from-red-400 to-red-600',
};

const difficultyLabels: Record<string, string> = {
  beginner: 'Beginner',
  intermediate: 'Intermediate',
  advanced: 'Advanced',
  expert: 'Expert',
};

const attackTypeEmojis: Record<string, string> = {
  phishing: '🎣',
  social_engineering: '🎭',
  brute_force: '🔐',
  malware: '🦠',
  default: '🛡️',
};

export default function CertificateVerificationPage() {
  const params = useParams();
  const certificateId = params.id as string;
  
  const [certificate, setCertificate] = useState<CertificateData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCertificate = async () => {
      try {
        const response = await axios.get(`${API_BASE}/certificates/${certificateId}`);
        setCertificate(response.data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch certificate:', err);
        setError('Certificate not found or invalid');
      } finally {
        setLoading(false);
      }
    };

    if (certificateId) {
      fetchCertificate();
    }
  }, [certificateId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-400"></div>
          <p className="text-emerald-400 mt-4">Loading certificate...</p>
        </div>
      </div>
    );
  }

  if (error || !certificate) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-400 text-6xl mb-4">⚠️</div>
          <h1 className="text-3xl font-bold text-white mb-2">Certificate Not Found</h1>
          <p className="text-slate-400 mb-6">{error || 'Unable to verify this certificate'}</p>
          <Link
            href="/"
            className="inline-block px-6 py-2 bg-gradient-to-r from-emerald-400 to-green-500 text-slate-900 font-bold rounded-lg hover:shadow-lg hover:shadow-emerald-400/50 transition-all duration-300"
          >
            Return Home
          </Link>
        </div>
      </div>
    );
  }

  const difficulty = certificate.scenario.difficulty || 'beginner';
  const gradientClass = difficultyColors[difficulty] || difficultyColors.beginner;
  const difficultyLabel = difficultyLabels[difficulty] || 'Beginner';
  const attackEmoji = attackTypeEmojis[certificate.scenario.attack_type] || attackTypeEmojis.default;

  const formattedDate = new Date(certificate.created_at).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4 sm:p-6 lg:p-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <Link
            href="/"
            className="inline-block text-emerald-400 hover:text-emerald-300 transition-colors text-sm"
          >
            ← Back to Home
          </Link>
        </div>

        {/* Certificate Card */}
        <div className="relative bg-gradient-to-b from-slate-800 to-slate-900 rounded-2xl border-2 border-emerald-500/50 shadow-2xl shadow-emerald-400/20 overflow-hidden mb-8">
          {/* Background decoration */}
          <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-bl from-emerald-500/10 to-transparent rounded-full transform translate-x-32 -translate-y-32 pointer-events-none"></div>
          <div className="absolute bottom-0 left-0 w-96 h-96 bg-gradient-to-tr from-emerald-500/10 to-transparent rounded-full transform -translate-x-32 translate-y-32 pointer-events-none"></div>

          {/* Content */}
          <div className="relative z-10 p-8 sm:p-12">
            {/* Certificate Icon and Title */}
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-emerald-400 to-green-500 rounded-full mb-4 shadow-lg shadow-emerald-400/50">
                <CertificateIcon />
              </div>
              <h1 className="text-4xl font-bold text-white mb-2">Achievement Unlocked</h1>
              <div className="h-1 w-12 bg-gradient-to-r from-emerald-400 to-green-500 mx-auto rounded-full"></div>
            </div>

            {/* Main Info */}
            <div className="bg-slate-900/50 rounded-xl p-6 mb-8 border border-slate-700/50">
              <div className="mb-6">
                <p className="text-slate-400 text-sm uppercase tracking-wider mb-2">Scenario Completed</p>
                <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                  <span className="text-3xl">{attackEmoji}</span>
                  {certificate.scenario.title}
                </h2>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <p className="text-slate-400 text-xs uppercase tracking-wider mb-1">Achievement Type</p>
                  <p className="text-emerald-400 font-semibold">
                    {certificate.achievement === 'perfect_score' && '🏆 Perfect Score'}
                    {certificate.achievement === 'first_completion' && '🌟 First Completion'}
                    {certificate.achievement === 'completion' && '✅ Completed'}
                    {!['perfect_score', 'first_completion', 'completion'].includes(certificate.achievement) && certificate.achievement}
                  </p>
                </div>
                <div>
                  <p className="text-slate-400 text-xs uppercase tracking-wider mb-1">Difficulty Level</p>
                  <div className={`inline-block px-3 py-1 rounded-full text-sm font-bold text-white bg-gradient-to-r ${gradientClass}`}>
                    {difficultyLabel}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-slate-400 text-xs uppercase tracking-wider mb-1">Date Earned</p>
                  <p className="text-white font-semibold">{formattedDate}</p>
                </div>
                <div>
                  <p className="text-slate-400 text-xs uppercase tracking-wider mb-1">Certificate ID</p>
                  <p className="text-emerald-400 font-mono text-sm">{certificate.id}</p>
                </div>
              </div>
            </div>

            {/* User Info */}
            <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700/50">
              <p className="text-slate-400 text-xs uppercase tracking-wider mb-3">Awarded To</p>
              <div className="flex items-center gap-3 mb-3">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-emerald-400 to-green-500 flex items-center justify-center text-white font-bold text-lg">
                  {certificate.user.username.charAt(0).toUpperCase()}
                </div>
                <div>
                  <p className="text-white font-bold">{certificate.user.username}</p>
                  <p className="text-slate-400 text-sm">{certificate.user.email}</p>
                </div>
              </div>
            </div>

            {/* Verification Badge */}
            <div className="mt-8 flex items-center justify-center gap-2 text-emerald-400">
              <div className="w-5 h-5 rounded-full bg-emerald-400 flex items-center justify-center">
                <svg className="w-3 h-3 text-slate-900" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </div>
              <span className="font-semibold">Certificate Verified</span>
            </div>
          </div>
        </div>

        {/* Scenario Description */}
        <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700/50 mb-8">
          <h3 className="text-lg font-bold text-white mb-3">Scenario Description</h3>
          <p className="text-slate-300 leading-relaxed">{certificate.scenario.description}</p>
        </div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/dashboard"
            className="px-6 py-3 bg-gradient-to-r from-emerald-400 to-green-500 text-slate-900 font-bold rounded-lg hover:shadow-lg hover:shadow-emerald-400/50 transition-all duration-300 text-center"
          >
            View Dashboard
          </Link>
          <Link
            href="/certificates"
            className="px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white font-bold rounded-lg transition-colors duration-300 text-center"
          >
            All Certificates
          </Link>
        </div>
      </div>
    </div>
  );
}
