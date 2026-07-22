import { useState } from 'react';

// TMDB IDs for popular platforms in India
const OTT_PLATFORMS = [
  { id: 8, name: "Netflix" },
  { id: 119, name: "Prime Video" },
  { id: 2336, name: "Jio Hotstar" },
  { id: 11, name: "MUBI" },
  { id: 237, name: "SonyLIV" },
  { id: 232, name: "Zee5" }
];

function App() {
  // 1. Form State
  const [mood, setMood] = useState("");
  const [selectedProviders, setSelectedProviders] = useState([]);
  
  // 2. Results State
  const [loading, setLoading] = useState(false);
  const [aiReasoning, setAiReasoning] = useState("");
  const [movies, setMovies] = useState([]);

  // 3. Handle Checkbox Clicks
  const handleCheckboxChange = (id) => {
    if (selectedProviders.includes(id)) {
      setSelectedProviders(selectedProviders.filter(providerId => providerId !== id));
    } else {
      setSelectedProviders([...selectedProviders, id]);
    }
  };

  // 4. Fetch Movies from Backend
  const fetchMovies = async (e) => {
    e.preventDefault(); 
    
    if (!mood || selectedProviders.length === 0) {
      alert("Please enter your mood and select at least one OTT platform!");
      return;
    }

    setLoading(true);
    setAiReasoning("");
    setMovies([]);

    try {
      const baseUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
      const providersString = selectedProviders.join(",");
      const response = await fetch(`${baseUrl}/recommend?mood=${encodeURIComponent(mood)}&providers=${providersString}`);
      const data = await response.json();
      
      if (data.error) {
        console.error("Backend error:", data.error);
      } else {
        setAiReasoning(data.ai_reasoning);
        setMovies(data.movies_found);
      }
    } catch (error) {
      console.error("Failed to fetch:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-4 md:p-8 font-sans">
      <div className="max-w-4xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">
            Mood Based AI Movie Recommender
          </h1>
          
        </div>

        {/* THE FORM */}
        <form onSubmit={fetchMovies} className="bg-slate-800 p-6 rounded-2xl shadow-xl border border-slate-700 space-y-6">
          
          <div className="space-y-3">
            <label className="block text-sm font-medium text-slate-300">
              How are you feeling right now?
            </label>
            <textarea 
              value={mood} 
              onChange={(e) => setMood(e.target.value)} 
              placeholder="e.g., Had a tiring day, need something light and comforting..."
              rows="3"
              className="w-full bg-slate-900 border border-slate-600 rounded-lg p-3 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
          </div>

          <div className="space-y-3">
            <label className="block text-sm font-medium text-slate-300">
              What platforms do you have?
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {OTT_PLATFORMS.map((platform) => (
                <label 
                  key={platform.id} 
                  className={`flex items-center p-3 rounded-lg border cursor-pointer transition-colors duration-200 ${
                    selectedProviders.includes(platform.id) 
                      ? 'bg-blue-900/50 border-blue-500' 
                      : 'bg-slate-900 border-slate-600 hover:border-slate-400'
                  }`}
                >
                  <input 
                    type="checkbox" 
                    value={platform.id} 
                    onChange={() => handleCheckboxChange(platform.id)}
                    className="w-4 h-4 text-blue-600 bg-slate-800 border-slate-500 rounded focus:ring-blue-500 focus:ring-2"
                  />
                  <span className="ml-3 text-sm text-white font-medium">{platform.name}</span>
                </label>
              ))}
            </div>
          </div>

          <button 
            type="submit" 
            disabled={loading}
            className="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white font-bold rounded-lg shadow-md transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Curating Films..." : "Find Movies"}
          </button>
        </form>

        {/* AI REASONING */}
        {aiReasoning && (
          <div className="bg-slate-800/50 p-5 rounded-xl border border-emerald-500/30">
            <h3 className="text-emerald-400 font-semibold mb-2 flex items-center">
              <span className="mr-2">✨</span> Why these films?
            </h3>
            <p className="text-slate-300 italic leading-relaxed">{aiReasoning}</p>
          </div>
        )}

        {/* THE RESULTS GRID */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {movies.map((movie) => (
            <div key={movie.id} className="bg-slate-800 rounded-xl overflow-hidden flex shadow-lg hover:shadow-2xl transition-shadow border border-slate-700 hover:border-slate-500">
              {movie.poster_path ? (
                <img 
                  src={`https://image.tmdb.org/t/p/w200${movie.poster_path}`} 
                  alt={movie.title} 
                  className="w-1/3 object-cover"
                />
              ) : (
                <div className="w-1/3 bg-slate-700 flex items-center justify-center text-slate-500 text-xs text-center p-2">
                  No Poster
                </div>
              )}
              
              <div className="w-2/3 p-4 flex flex-col justify-between">
                <div>
                  <h3 className="text-lg font-bold text-white line-clamp-1" title={movie.title}>
                    {movie.title}
                  </h3>
                  <p className="text-yellow-400 text-sm font-medium mt-1 mb-2">
                    ⭐ {movie.vote_average.toFixed(1)} <span className="text-slate-500 text-xs">({movie.release_date?.split('-')[0]})</span>
                  </p>
                  <p className="text-slate-400 text-sm line-clamp-4 leading-snug">
                    {movie.overview || "No overview available."}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

      </div>
    </div>
  );
}

export default App;