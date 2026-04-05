'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '../../context/AuthContext';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface Choice {
  id: number;
  text: string;
  is_safe: boolean;
  consequence: string;
}

interface Step {
  id: number;
  title: string;
  description: string;
  choices: Choice[];
}

interface Scenario {
  id: number;
  title: string;
  description: string;
  context: string;
  attack_type: string;
  difficulty: string;
  attack_steps: Step[];
}

export default function GamePage() {
  const { user, token } = useAuth();
  const router = useRouter();
  const params = useParams();
  const scenarioId = parseInt(params.id as string);

  const [scenario, setScenario] = useState<Scenario | null>(null);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [progressId, setProgressId] = useState<number | null>(null);
  const [securityLevel, setSecurityLevel] = useState(100);
  const [correctChoices, setCorrectChoices] = useState(0);
  const [totalChoices, setTotalChoices] = useState(0);
  const [feedback, setFeedback] = useState<{ isCorrect: boolean; message: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [gameEnded, setGameEnded] = useState(false);

  useEffect(() => {
    if (!user || !token) {
      router.push('/login');
      return;
    }

    const initGame = async () => {
      try {
        // Fetch scenario details
        const scenarioResponse = await axios.get(`${API_BASE}/scenarios/${scenarioId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setScenario(scenarioResponse.data);

        // Start progress for this scenario
        const progressResponse = await axios.post(
          `${API_BASE}/progress/start`,
          { scenario_id: scenarioId },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setProgressId(progressResponse.data.id);
      } catch (error) {
        console.error('Failed to initialize game:', error);
      } finally {
        setLoading(false);
      }
    };

    initGame();
  }, [scenarioId, user, token, router]);

  const handleChoiceClick = async (choiceId: number) => {
    if (!progressId || !scenario) return;

    try {
      const isLastStep = currentStepIndex === scenario.attack_steps.length - 1;
      const response = await axios.post(
        `${API_BASE}/progress/${progressId}/choice`,
        {
          step_id: scenario.attack_steps[currentStepIndex].id,
          choice_id: choiceId,
          is_final: isLastStep,
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      const result = response.data;
      setSecurityLevel(result.security_level);
      setCorrectChoices(result.correct_choices);
      setTotalChoices(result.total_choices);

      const currentChoice = scenario.attack_steps[currentStepIndex].choices.find(
        (c) => c.id === choiceId
      );
      setFeedback({
        isCorrect: result.is_correct,
        message: currentChoice?.consequence || '',
      });

      if (isLastStep) {
        setGameEnded(true);
      } else {
        setTimeout(() => {
          setCurrentStepIndex(currentStepIndex + 1);
          setFeedback(null);
        }, 3000);
      }
    } catch (error) {
      console.error('Failed to submit choice:', error);
    }
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-300 text-lg">Loading scenario...</p>
        </div>
      </main>
    );
  }

  if (!scenario) {
    return (
      <main className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <p className="text-slate-300 text-lg mb-4">Scenario not found</p>
          <Link href="/scenarios" className="text-indigo-400 hover:text-indigo-300">Go back to scenarios</Link>
        </div>
      </main>
    );
  }

  const currentStep = scenario.attack_steps[currentStepIndex];
  const accuracy = totalChoices > 0 ? ((correctChoices / totalChoices) * 100).toFixed(1) : 0;

  return (
    <main className="min-h-screen bg-slate-950">
      {/* Header */}
      <div className="sticky top-0 z-40 bg-slate-950/80 backdrop-blur-xl border-b border-green-500/30">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div>
            <div className="text-xs font-semibold text-green-400 uppercase mb-1">🔓 {scenario.attack_type}</div>
            <h1 className="text-2xl font-bold text-white">{scenario.title}</h1>
          </div>
          <Link href="/scenarios" className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
            Back
          </Link>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Game Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl blur opacity-20 group-hover:opacity-40 transition-opacity"></div>
            <div className="relative bg-black/30 backdrop-blur-xl p-6 rounded-xl border border-green-500/30">
              <div className="flex items-end justify-between mb-2">
                <p className="text-green-300/70 text-sm font-medium">Security Level</p>
                <span className="text-xs">🛡️</span>
              </div>
              <div className="text-3xl font-bold text-white mb-2">{securityLevel}%</div>
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div className="bg-gradient-to-r from-green-500 to-emerald-600 h-2 rounded-full transition-all duration-300" style={{width: `${securityLevel}%`}}></div>
              </div>
            </div>
          </div>

          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl blur opacity-20 group-hover:opacity-40 transition-opacity"></div>
            <div className="relative bg-black/30 backdrop-blur-xl p-6 rounded-xl border border-green-500/30">
              <div className="flex items-end justify-between mb-2">
                <p className="text-green-300/70 text-sm font-medium">Correct Choices</p>
                <span className="text-xs">✅</span>
              </div>
              <div className="text-3xl font-bold text-green-400">{correctChoices}</div>
              <p className="text-xs text-slate-500 mt-2">Out of {totalChoices}</p>
            </div>
          </div>

          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-r from-yellow-500 to-orange-600 rounded-xl blur opacity-20 group-hover:opacity-40 transition-opacity"></div>
            <div className="relative bg-black/30 backdrop-blur-xl p-6 rounded-xl border border-yellow-500/30">
              <div className="flex items-end justify-between mb-2">
                <p className="text-yellow-300/70 text-sm font-medium">Accuracy</p>
                <span className="text-xs">🎯</span>
              </div>
              <div className="text-3xl font-bold text-yellow-400">{accuracy}%</div>
            </div>
          </div>

          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-r from-pink-500 to-rose-600 rounded-xl blur opacity-20 group-hover:opacity-40 transition-opacity"></div>
            <div className="relative bg-black/30 backdrop-blur-xl p-6 rounded-xl border border-pink-500/30">
              <div className="flex items-end justify-between mb-2">
                <p className="text-pink-300/70 text-sm font-medium">Progress</p>
                <span className="text-xs">📍</span>
              </div>
              <div className="text-3xl font-bold text-pink-400">{currentStepIndex + 1}/{scenario.attack_steps.length}</div>
            </div>
          </div>
        </div>

        {/* Game Content */}
        <div className="bg-gradient-to-br from-black/40 to-black/60 backdrop-blur-xl rounded-2xl border border-green-500/30 p-8">
          <div className="mb-8">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-lg flex items-center justify-center text-xl">⚙️</div>
              <div>
                <h2 className="text-3xl font-bold text-white">{currentStep.title}</h2>
                <p className="text-green-300/70 text-sm mt-1">Step {currentStepIndex + 1} of {scenario.attack_steps.length}</p>
              </div>
            </div>
            <p className="text-white text-lg leading-relaxed bg-black/30 p-6 rounded-lg border border-green-500/30">{currentStep.description}</p>
          </div>

          {!gameEnded && !feedback && (
            <div>
              <p className="text-green-300 font-semibold mb-4 text-lg">What do you choose to do?</p>
              <div className="space-y-3">
                {currentStep.choices.map((choice, index) => (
                  <button
                    key={choice.id}
                    onClick={() => handleChoiceClick(choice.id)}
                    className="w-full group relative overflow-hidden text-left"
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-green-500/0 via-green-500/0 to-green-500/0 group-hover:from-green-500/20 group-hover:via-green-500/10 group-hover:to-green-500/5 transition-all duration-300"></div>
                    <div className="relative bg-black/40 hover:bg-black/50 backdrop-blur-sm border border-green-500/30 group-hover:border-green-400/50 p-4 rounded-lg transition-all duration-300">
                      <div className="flex items-start gap-4">
                        <div className="flex items-center justify-center w-8 h-8 rounded-full bg-green-500/20 group-hover:bg-green-500/40 text-green-300 font-semibold text-sm flex-shrink-0 transition-all duration-300">
                          {String.fromCharCode(65 + index)}
                        </div>
                        <p className="text-white text-sm font-medium group-hover:text-green-200 transition-colors flex-1 pt-1">{choice.text}</p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {feedback && (
            <div className={`animated-fade-in p-6 rounded-xl border-2 ${
              feedback.isCorrect
                ? 'bg-emerald-500/10 border-emerald-500/50'
                : 'bg-red-500/10 border-red-500/50'
            }`}>
              <div className="flex items-start gap-4">
                <div className="text-4xl flex-shrink-0">{feedback.isCorrect ? '✨' : '⚠️'}</div>
                <div className="flex-1">
                  <p className={`text-lg font-bold mb-2 ${
                    feedback.isCorrect ? 'text-green-300' : 'text-red-300'
                  }`}>
                    {feedback.isCorrect ? 'Excellent Choice!' : 'Unfortunate Decision'}
                  </p>
                  <p className="text-slate-300 leading-relaxed">{feedback.message}</p>
                </div>
              </div>
            </div>
          )}

          {gameEnded && (
            <div className="bg-gradient-to-br from-amber-500/10 to-orange-500/10 border-2 border-amber-500/50 p-8 rounded-xl">
              <div className="flex items-start gap-4 mb-6">
                <div className="text-5xl">🎉</div>
                <div>
                  <h3 className="text-3xl font-bold text-white mb-2">Scenario Complete!</h3>
                  <p className="text-slate-300">You've completed this security scenario. Great job!</p>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 mb-8 bg-black/30 p-6 rounded-lg border border-green-500/30">
                <div className="text-center">
                  <div className="text-2xl font-bold text-amber-400 mb-1">{securityLevel}%</div>
                  <p className="text-xs text-green-300/70">Security Level</p>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-emerald-400 mb-1">{accuracy}%</div>
                  <p className="text-xs text-green-300/70">Accuracy</p>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-indigo-400 mb-1">{correctChoices}/{totalChoices}</div>
                  <p className="text-xs text-green-300/70">Correct Choices</p>
                </div>
              </div>

              {securityLevel === 100 && (
                <div className="bg-gradient-to-r from-yellow-500/20 to-yellow-600/20 border border-yellow-500/50 p-4 rounded-lg mb-6 text-center">
                  <p className="text-yellow-300 font-bold text-lg">⭐ Perfect Score!</p>
                  <p className="text-yellow-200 text-sm">You earned a certificate for your expertise!</p>
                </div>
              )}

              <Link
                href="/scenarios"
                className="inline-flex items-center gap-2 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-black px-6 py-3 rounded-lg font-semibold transition-all duration-200 shadow-lg hover:shadow-green-500/50"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
                Back to Scenarios
              </Link>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
