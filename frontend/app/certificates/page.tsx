'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '../context/AuthContext';
import { CertificateIcon, TrophyIcon } from '../../components/Icons';
import axios from 'axios';
import QRCode from 'qrcode.react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface Certificate {
  id: number;
  user_id: number;
  scenario_id: number;
  achievement: string;
  qr_code?: string;
  created_at: string;
}

export default function CertificatesPage() {
  const { user, token } = useAuth();
  const router = useRouter();
  const [certificates, setCertificates] = useState<Certificate[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user || !token) {
      router.push('/login');
      return;
    }

    const fetchCertificates = async () => {
      try {
        const response = await axios.get(`${API_BASE}/user/certificates`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setCertificates(response.data);
      } catch (error) {
        console.error('Failed to fetch certificates:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCertificates();
  }, [user, token, router]);

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-white text-2xl">Loading certificates...</div>
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
        <div className="flex items-center gap-4 mb-8">
          <div className="text-amber-400">
            <TrophyIcon />
          </div>
          <h1 className="text-4xl font-bold text-white">Your Certificates</h1>
        </div>

        {certificates.length === 0 ? (
          <div className="bg-black/30 backdrop-blur-sm p-12 rounded-lg border border-green-500/30 text-center">
            <div className="text-6xl mb-4 inline-block">📜</div>
            <p className="text-green-300 text-lg">No certificates yet!</p>
            <p className="text-green-300/70 mb-6">Complete scenarios with perfect scores to earn certificates.</p>
            <Link href="/scenarios" className="inline-block bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-black px-6 py-2 rounded-lg font-bold">
              Start Learning
            </Link>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {certificates.map((cert) => (
              <div
                key={cert.id}
                className="group relative bg-gradient-to-br from-green-400 via-emerald-500 to-emerald-600 p-1 rounded-xl shadow-2xl shadow-green-500/50 hover:shadow-green-400/70 transition-all duration-300"
              >
                <div className="bg-slate-950 rounded-lg p-6 relative z-10 h-full flex flex-col">
                  {/* Certificate Header */}
                  <div className="bg-gradient-to-r from-amber-100 to-amber-50 rounded-lg p-6 mb-4 text-center">
                    <div className="text-5xl mb-2 animate-bounce">🏅</div>
                    <h3 className="text-xl font-bold text-gray-900 mb-1">Certificate of Achievement</h3>
                    <p className="text-sm text-gray-600">Data Protection Simulator</p>
                  </div>

                  {/* Achievement Details */}
                  <div className="flex-1 mb-4">
                    <div className="bg-white/10 backdrop-blur-sm p-4 rounded-lg mb-3">
                      <p className="text-white/70 text-sm mb-1">Achievement</p>
                      <p className="text-green-400 font-bold capitalize text-lg">{cert.achievement.replace('_', ' ')}</p>
                    </div>
                    <div className="bg-white/10 backdrop-blur-sm p-4 rounded-lg">
                      <p className="text-white/70 text-sm mb-1">Earned On</p>
                      <p className="text-green-400 font-bold">{new Date(cert.created_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}</p>
                    </div>
                  </div>

                  {/* QR Code */}
                  <div className="bg-white p-4 rounded-lg flex justify-center items-center">
                    <QRCode
                      value={`${window.location.origin}/certificate/${cert.id}`}
                      size={140}
                      level="H"
                      includeMargin={true}
                    />
                  </div>
                  <p className="text-white/50 text-xs text-center mt-3">Scan to verify certificate</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
