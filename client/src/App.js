import React, { useState, useEffect } from 'react';
import { Calendar, X, ExternalLink } from 'lucide-react';

function App() {
  const [summaries, setSummaries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showHero, setShowHero] = useState(true);
  const [fadeOut, setFadeOut] = useState(false);
  const [selectedSummary, setSelectedSummary] = useState(null);

  useEffect(() => {
    const fadeTimer = setTimeout(() => setFadeOut(true), 3500);
    const hideTimer = setTimeout(() => setShowHero(false), 4500);

    fetchSummaries();
    return () => {
      clearTimeout(fadeTimer);
      clearTimeout(hideTimer);
    };
  }, []);

  const fetchSummaries = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:5000/summaries');
      const data = await response.json();
      
      if (data.success) {
        setSummaries(data.data);
      }
    } catch (err) {
      console.error('Error fetching summaries:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Date not available';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  const parseSummary = (text) => {
    if (!text) return { intro: '', bullets: [] };
    
    // Split by bullet point symbol •
    const parts = text.split('•').map(p => p.trim()).filter(p => p.length > 0);
    
    if (parts.length === 0) {
      return { intro: text, bullets: [] };
    }
    
    // First part is intro sentence, rest are bullet points
    return {
      intro: parts[0],
      bullets: parts.slice(1)
    };
  };

  if (showHero) {
    return (
      <div className={`hero-container ${fadeOut ? 'fade-out' : ''}`}>
        <div className="liquid-bg"></div>
        <div className="glow-effect"></div>
        <div className="hero-content">
          <h1 className="hero-title">CityScope</h1>
          <div className="hero-glow"></div>
        </div>
        
        <style>{`
          .hero-container {
            position: fixed;
            inset: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #0a0a0a 100%);
            transition: opacity 1s ease-out;
          }

          .hero-container.fade-out {
            opacity: 0;
          }

          .liquid-bg {
            position: absolute;
            inset: 0;
            background: 
              radial-gradient(circle at 20% 50%, rgba(14, 165, 233, 0.15) 0%, transparent 50%),
              radial-gradient(circle at 80% 80%, rgba(6, 182, 212, 0.15) 0%, transparent 50%),
              radial-gradient(circle at 40% 80%, rgba(56, 189, 248, 0.15) 0%, transparent 50%),
              radial-gradient(circle at 60% 20%, rgba(34, 211, 238, 0.15) 0%, transparent 50%);
            filter: blur(80px);
            animation: liquidMove 10s ease-in-out infinite;
          }

          .glow-effect {
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at center, rgba(14, 165, 233, 0.1) 0%, transparent 70%);
            animation: pulse 3s ease-in-out infinite;
          }

          @keyframes pulse {
            0%, 100% { opacity: 0.5; transform: scale(1); }
            50% { opacity: 1; transform: scale(1.05); }
          }

          @keyframes liquidMove {
            0%, 100% { transform: scale(1) translate(0, 0); }
            33% { transform: scale(1.1) translate(2%, -2%); }
            66% { transform: scale(0.9) translate(-2%, 2%); }
          }

          .hero-content {
            position: relative;
            z-index: 10;
            text-align: center;
          }

          .hero-title {
            font-size: 8rem;
            font-weight: 800;
            background: linear-gradient(135deg, #ffffff 0%, #e0f2fe 50%, #bae6fd 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 0;
            letter-spacing: -0.03em;
            opacity: 0;
            animation: titleAppear 1.5s ease-out 0.8s forwards;
            text-shadow: 0 0 80px rgba(14, 165, 233, 0.5);
            position: relative;
          }

          .hero-glow {
            position: absolute;
            inset: -50%;
            background: radial-gradient(circle, rgba(14, 165, 233, 0.3) 0%, transparent 70%);
            filter: blur(60px);
            animation: glowPulse 2s ease-in-out infinite 2s;
            z-index: -1;
          }

          @keyframes glowPulse {
            0%, 100% { opacity: 0.3; transform: scale(0.8); }
            50% { opacity: 0.6; transform: scale(1.2); }
          }

          @keyframes titleAppear {
            from { opacity: 0; transform: translateY(30px) scale(0.9); filter: blur(10px); }
            to { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }
          }

          @media (max-width: 768px) {
            .hero-title { font-size: 4rem; }
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50 animate-page-in">
      <header className="sticky top-0 z-40 backdrop-blur-xl bg-white/70 border-b border-gray-200/50 shadow-sm animate-slide-down">
        <div className="max-w-5xl mx-auto px-6 py-6">
          <div className="text-center">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-600 via-blue-600 to-sky-600 bg-clip-text text-transparent">
              CityScope
            </h1>
            <p className="text-gray-600 mt-2">London Council Meetings</p>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-12">
        <div className="mb-8 text-center">
          <p className="text-gray-600 text-lg">
            <span className="text-3xl font-bold text-gray-900">{summaries.length}</span>
            {' '}meeting summaries
          </p>
        </div>

        {loading && (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-cyan-600"></div>
            <p className="text-gray-600 mt-4">Loading meetings...</p>
          </div>
        )}

        {!loading && (
          <div className="space-y-4">
            {summaries.map((summary) => (
              <button
                key={summary.id || summary.document_id}
                onClick={() => setSelectedSummary(summary)}
                className="w-full bg-white/80 backdrop-blur-sm rounded-2xl shadow-md hover:shadow-2xl transition-all duration-300 p-6 text-left border border-gray-200/50 hover:border-cyan-300 hover:scale-[1.01] group"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-bold text-xl text-gray-900 mb-2 group-hover:text-cyan-600 transition-colors">
                      {summary.meeting_title || 'Council Meeting'}
                    </h3>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Calendar size={16} className="flex-shrink-0" />
                      <span>{formatDate(summary.meeting_date || summary.created_at)}</span>
                    </div>
                  </div>
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 rounded-full bg-cyan-100 group-hover:bg-cyan-200 flex items-center justify-center transition-colors">
                      <svg className="w-5 h-5 text-cyan-600 transform group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}

        {!loading && summaries.length === 0 && (
          <div className="text-center py-20">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-100 flex items-center justify-center">
              <Calendar className="text-gray-400" size={32} />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Meetings Found</h3>
            <p className="text-gray-600">Check back later for new council meeting summaries</p>
          </div>
        )}
      </main>

      {selectedSummary && (
        <div 
          className="fixed inset-0 bg-black/60 backdrop-blur-md z-50 flex items-center justify-center p-4 animate-fade-in"
          onClick={() => setSelectedSummary(null)}
        >
          <div 
            className="bg-white rounded-3xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden animate-scale-in"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="relative bg-gradient-to-r from-cyan-600 via-blue-600 to-sky-600 px-8 py-8">
              <button
                onClick={() => setSelectedSummary(null)}
                className="absolute top-6 right-6 text-white/80 hover:text-white bg-white/20 hover:bg-white/30 rounded-full p-2.5 transition-all hover:rotate-90 duration-300"
              >
                <X size={24} />
              </button>
              
              <h2 className="text-3xl font-bold text-white pr-16 mb-3 leading-tight">
                {selectedSummary.meeting_title || 'Council Meeting'}
              </h2>
              <div className="flex items-center gap-2 text-white/90">
                <Calendar size={18} />
                <span className="text-lg">{formatDate(selectedSummary.meeting_date || selectedSummary.created_at)}</span>
              </div>
            </div>

            <div className="p-8 overflow-y-auto max-h-[calc(90vh-250px)]">
              <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-6">
                Meeting Summary
              </h3>
              
              {(() => {
                const { intro, bullets } = parseSummary(selectedSummary.summary);
                return (
                  <div>
                    <p className="text-gray-700 leading-relaxed text-lg mb-6">
                      {intro}
                    </p>
                    
                    {bullets.length > 0 && (
                      <ul className="space-y-3">
                        {bullets.map((bullet, idx) => (
                          <li key={idx} className="flex items-start gap-3">
                            <div className="flex-shrink-0 w-2 h-2 bg-cyan-600 rounded-full mt-2"></div>
                            <span className="text-gray-700 leading-relaxed flex-1">{bullet}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                );
              })()}

              <div className="mt-10 pt-8 border-t border-gray-200 flex items-center justify-between">
                <p className="text-sm text-gray-500">
                  Want more details? View the complete official document
                </p>
                <a
                  href={selectedSummary.original_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 text-white rounded-xl hover:from-cyan-700 hover:to-blue-700 transition-all font-medium shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                >
                  View Original PDF
                  <ExternalLink size={18} />
                </a>
              </div>
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        
        @keyframes scaleIn {
          from { opacity: 0; transform: scale(0.95); }
          to { opacity: 1; transform: scale(1); }
        }

        @keyframes pageIn {
          from { opacity: 0; transform: scale(1.02); }
          to { opacity: 1; transform: scale(1); }
        }

        @keyframes slideDown {
          from { opacity: 0; transform: translateY(-20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        .animate-fade-in { animation: fadeIn 0.2s ease-out; }
        .animate-scale-in { animation: scaleIn 0.3s ease-out; }
        .animate-page-in { animation: pageIn 1s ease-out; }
        .animate-slide-down { animation: slideDown 0.8s ease-out; }
      `}</style>
    </div>
  );
}

export default App;