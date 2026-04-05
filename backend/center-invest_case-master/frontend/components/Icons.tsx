/**
 * Кастомные иконки для сертификатов, статистики и других элементов
 */

export const TrophyIcon = () => (
  <svg className="w-12 h-12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M6 9c0-1 1-2 2-2h8c1 0 2 1 2 2v3c0 1-1 2-2 2H8c-1 0-2-1-2-2V9z" />
    <path d="M8 15v2c0 1 1 2 2 2h4c1 0 2-1 2-2v-2" />
    <path d="M12 19v1M9 22h6" />
    <path d="M5 9h1M18 9h1" />
  </svg>
);

export const CertificateIcon = () => (
  <svg className="w-12 h-12" viewBox="0 0 24 24" fill="currentColor" opacity="0.8">
    <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z" />
    <circle cx="12" cy="10" r="2" fill="rgba(255,255,255,0.3)" />
  </svg>
);

export const PerfectScoreIcon = () => (
  <svg className="w-10 h-10" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
  </svg>
);

export const StatsIcon = () => (
  <svg className="w-12 h-12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <line x1="12" y1="2" x2="12" y2="22" />
    <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
  </svg>
);

export const ShieldIcon = () => (
  <svg className="w-12 h-12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
  </svg>
);

export const PhishingIcon = () => (
  <svg className="w-8 h-8" viewBox="0 0 24 24" fill="currentColor">
    <path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z" />
  </svg>
);

export const SecurityIcon = () => (
  <svg className="w-8 h-8" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z" />
  </svg>
);

export const DangerIcon = () => (
  <svg className="w-8 h-8" viewBox="0 0 24 24" fill="currentColor">
    <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z" />
  </svg>
);

export const SuccessIcon = () => (
  <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
    <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" />
  </svg>
);

export const RankBadge = ({ rank }: { rank: string }) => {
  const colors: Record<string, string> = {
    Beginner: 'from-blue-400 to-blue-600',
    Intermediate: 'from-purple-400 to-purple-600',
    Advanced: 'from-yellow-400 to-yellow-600',
    Expert: 'from-red-400 to-red-600',
  };

  const color = colors[rank] || 'from-gray-400 to-gray-600';

  return (
    <div className={`relative inline-flex items-center justify-center w-24 h-24 rounded-full bg-gradient-to-br ${color} shadow-lg`}>
      <div className="absolute inset-1 rounded-full bg-slate-900 flex items-center justify-center">
        <span className="text-white font-bold text-2xl">{rank[0]}</span>
      </div>
      <span className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 text-xs font-bold text-white bg-slate-800 px-2 py-1 rounded">
        {rank}
      </span>
    </div>
  );
};

export const AccuracyMeter = ({ accuracy }: { accuracy: number }) => {
  const getColor = () => {
    if (accuracy >= 90) return 'from-green-400 to-emerald-600';
    if (accuracy >= 75) return 'from-yellow-400 to-yellow-600';
    if (accuracy >= 50) return 'from-orange-400 to-orange-600';
    return 'from-red-400 to-red-600';
  };

  return (
    <div className="relative w-32 h-32">
      <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
        {/* Background circle */}
        <circle cx="50" cy="50" r="45" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="8" />
        {/* Progress circle */}
        <circle
          cx="50"
          cy="50"
          r="45"
          fill="none"
          stroke="url(#accuracyGradient)"
          strokeWidth="8"
          strokeDasharray={`${(accuracy / 100) * 282.7} 282.7`}
          strokeLinecap="round"
          style={{ transition: 'stroke-dasharray 0.5s ease' }}
        />
        <defs>
          <linearGradient id="accuracyGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#10b981" />
            <stop offset="100%" stopColor="#059669" />
          </linearGradient>
        </defs>
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-bold text-green-400">{accuracy.toFixed(1)}%</span>
        <span className="text-xs text-gray-400">Accuracy</span>
      </div>
    </div>
  );
};
