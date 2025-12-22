import React, { useState, useEffect } from 'react';
import { Calendar, X, Filter, ChevronDown } from 'lucide-react';
/* */

function App() {
  const [summaries, setSummaries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showHero, setShowHero] = useState(true);
  const [selectedSummary, setSelectedSummary] = useState(null);
  const [filterDays, setFilterDays] = useState('all');
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    // Hero animation - hide after 2.5 seconds
    const timer = setTimeout(() => {
      setShowHero(false);
    }, 2500);

    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    fetchSummaries();
  }, [filterDays]);

  const fetchSummaries = async () => {
    setLoading(true);
    try {
      let url = 'http://127.0.0.1:5000/summaries';
      
      if (filterDays !== 'all') {
        url = `http://127.0.0.1:5000/summaries/recent?days=${filterDays}`;
      }
      
      const response = await fetch(url);
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

  const formatSummary = (text) => {
    if (!text) return [];
    return text
      .split(/\n|•/)
      .map(point => point.trim())
      .filter(point => point.length > 0);
  };

  if (showHero) {
    return (
      <div className="fixed inset-0 bg-gradient-to-br from-blue-900 via-indigo-900 to-purple-900 flex items-center justify-center overflow-hidden">
        <div className="text-center">
          <h1 className="text-8xl font-bold text-white animate-fade-in-up tracking-tight">
            CityScope
          </h1>
          <p className="text-2xl text-blue-200 mt-4 animate-fade-in-up-delay">
            London Council Meetings Simplified
          </p>
        </div>
        <style>{`
          @keyframes fadeInUp {
            from {
              opacity: 0;
              transform: translateY(30px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }
          
          .animate-fade-in-up {
            animation: fadeInUp 1s ease-out forwards;
          }
          
          .animate-fade-in-up-delay {
            opacity: 0;
            animation: fadeInUp 1s ease-out 0.5s forwards;
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Fixed Header */}
      <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              CityScope
            </h1>
            <p className="text-sm text-gray-600">London Council Meetings</p>
          </div>
          
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Filter size={18} />
            Filter
          </button>
        </div>

        {/* Filter Dropdown */}
        {showFilters && (
          <div className="border-t border-gray-200 bg-white">
            <div className="max-w-7xl mx-auto px-6 py-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Time Period
              </label>
              <select
                value={filterDays}
                onChange={(e) => setFilterDays(e.target.value)}
                className="w-full md:w-64 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
              >
                <option value="all">All Time</option>
                <option value="7">Last 7 Days</option>
                <option value="30">Last 30 Days</option>
                <option value="90">Last 90 Days</option>
                <option value="180">Last 6 Months</option>
                <option value="365">Last Year</option>
              </select>
            </div>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats Bar */}
        <div className="mb-8 text-center">
          <p className="text-gray-600">
            <span className="text-2xl font-bold text-gray-900">{summaries.length}</span>
            {' '}meeting summaries available
          </p>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600"></div>
            <p className="text-gray-600 mt-4">Loading meetings...</p>
          </div>
        )}

        {/* Cards Grid */}
        {!loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {summaries.map((summary) => (
              <button
                key={summary.id || summary.document_id}
                onClick={() => setSelectedSummary(summary)}
                className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 p-6 text-left border-2 border-transparent hover:border-blue-400 transform hover:-translate-y-1"
              >
                <h3 className="font-bold text-lg text-gray-900 mb-2 line-clamp-2">
                  {summary.meeting_title || summary.filename || 'Council Meeting'}
                </h3>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Calendar size={16} />
                  <span>{formatDate(summary.meeting_date || summary.created_at)}</span>
                </div>
              </button>
            ))}
          </div>
        )}

        {/* Empty State */}
        {!loading && summaries.length === 0 && (
          <div className="text-center py-20">
            <ChevronDown className="mx-auto text-gray-400 mb-4" size={48} />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Meetings Found</h3>
            <p className="text-gray-600">Try adjusting your filter settings</p>
          </div>
        )}
      </main>

      {/* Modal for Full Summary */}
      {selectedSummary && (
        <div 
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedSummary(null)}
        >
          <div 
            className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden animate-modal-in"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-8 py-6 relative">
              <button
                onClick={() => setSelectedSummary(null)}
                className="absolute top-4 right-4 text-white/80 hover:text-white bg-white/10 hover:bg-white/20 rounded-full p-2 transition-colors"
              >
                <X size={24} />
              </button>
              
              <h2 className="text-2xl font-bold text-white pr-12 mb-2">
                {selectedSummary.meeting_title || selectedSummary.filename || 'Council Meeting'}
              </h2>
              <div className="flex items-center gap-2 text-blue-100">
                <Calendar size={18} />
                <span>{formatDate(selectedSummary.meeting_date || selectedSummary.created_at)}</span>
              </div>
            </div>

            {/* Modal Body */}
            <div className="p-8 overflow-y-auto max-h-[calc(90vh-200px)]">
              <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wide mb-4">
                Meeting Summary
              </h3>
              
              <div className="space-y-3">
                {formatSummary(selectedSummary.summary).map((point, idx) => (
                  <div key={idx} className="flex items-start gap-3">
                    <div className="flex-shrink-0 w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center mt-0.5">
                      <span className="text-blue-600 font-bold text-sm">{idx + 1}</span>
                    </div>
                    <p className="text-gray-700 leading-relaxed flex-1">{point}</p>
                  </div>
                ))}
              </div>

              {/* View Original Button */}
              <div className="mt-8 pt-6 border-t border-gray-200">
                <a
                  href={selectedSummary.original_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                  View Original PDF Document
                </a>
              </div>
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes modalIn {
          from {
            opacity: 0;
            transform: scale(0.95);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }
        
        .animate-modal-in {
          animation: modalIn 0.2s ease-out;
        }

        .line-clamp-2 {
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
      `}</style>
    </div>
  );
}

export default App;