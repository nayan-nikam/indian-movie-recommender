# Mood Based AI Movie Recommender

An AI-powered web application that recommends Indian and global cinema based on your current mood and available OTT subscriptions. 

Instead of infinitely scrolling through platforms, users simply type how they are feeling. The app uses an LLM-driven workflow to analyze the emotion, map it to specific cinematic genres, and concurrently fetch top-rated movies available on selected Indian streaming services.

## ✨ Features

* **🧠 AI Mood Analysis:** Uses Google's Gemini (via LangGraph) to interpret complex human emotions and map them to strict TMDB genre IDs.
* **⚡ Concurrent Fetching:** FastAPI backend leverages asynchronous parallel requests (`asyncio.gather`) to pull balanced recommendations across multiple OTT platforms simultaneously without bottlenecks.
* **🇮🇳 Indian OTT Focus:** Tailored for the Indian streaming landscape, filtering specifically for platforms like Netflix, Prime Video, Disney+ Hotstar, JioCinema, SonyLIV, and Zee5.
* **💅 Modern UI:** Built with React and Tailwind CSS for a responsive, cinematic, and dark-themed user experience.

## 🛠️ Tech Stack

**Frontend:**
* React (Vite)
* Tailwind CSS

**Backend & AI:**
* FastAPI & Uvicorn (Python)
* LangGraph & LangChain 
* Google Gemini (gemini-3.5-flash)
* The Movie Database (TMDB) API

## 🚀 Getting Started

Follow these steps to run the project locally on your machine.

### Prerequisites
* Node.js (v18+)
* Python (3.9+)
* A free [TMDB API Read Access Token](https://developer.themoviedb.org/docs/getting-started)
* A free [Google Gemini API Key](https://aistudio.google.com/)

### 1. Backend Setup
Navigate to the backend directory, set up your virtual environment, and run the server:

-> ```bash
cd backend
python -m venv venv

# Activate the virtual environment
# Windows CMD: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create a .env file in the backend folder and add your API keys:
TMDB_API_KEY=your_tmdb_read_access_token_here
GEMINI_API_KEY=your_gemini_api_key_here

#Start the FastAPI server:
uvicorn main:app --reload

### 2. Frontend Setup
Open a new terminal window, navigate to the frontend directory, and run the React app:
cd frontend
npm install
npm run dev

# PROJECT STRUCTURE

indian-movie-recommender/
│
├── backend/                  # FastAPI & AI Logic
│   ├── agent.py              # LangGraph workflow and Gemini LLM configuration
│   ├── main.py               # FastAPI server, endpoints, and parallel fetching logic
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # Secret API keys (ignored by git)
│
└── frontend/                 # React UI
    ├── src/
    │   ├── App.jsx           # Main UI component and state management
    │   ├── index.css         # Tailwind CSS imports and global styles
    │   └── main.jsx          # React DOM rendering
    ├── tailwind.config.js    # Tailwind theme configuration
    └── package.json          # Node dependencies
