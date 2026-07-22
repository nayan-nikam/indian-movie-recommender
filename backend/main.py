from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import asyncio
from dotenv import load_dotenv
from agent import mood_agent

# 1. Load Environment Variables
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# 2. Initialize the App (This is the line that was missing!)
app = FastAPI(title="Indian Movie Recommender API")

# 3. Configure CORS for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# 4. Root Endpoint
@app.get("/")
def read_root():
    return {"message": "Namaste! The Movie Recommender Backend is running."}

# 5. Recommendation Endpoint with Parallel Fetching
@app.get("/recommend")
async def get_recommendations(
    mood: str = Query(..., description="How is the user feeling?"),
    providers: str = Query(..., description="Comma separated OTT provider IDs")
):
    # Run the AI Logic
    initial_state = {"user_mood": mood}
    graph_result = mood_agent.invoke(initial_state)
    ai_analysis = graph_result["analysis"]
    genre_ids_str = ",".join(ai_analysis.genres)
    
    url = "https://api.themoviedb.org/3/discover/movie"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_API_KEY}"
    }
    
    provider_list = providers.split(",")
    
    # Helper function to fetch movies for a SINGLE provider
    async def fetch_provider_movies(client, provider_id):
        params = {
            "watch_region": "IN",
            "with_watch_providers": provider_id, 
            "with_genres": genre_ids_str,
            "with_watch_monetization_types": "flatrate",
            "sort_by": "popularity.desc"
        }
        response = await client.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json().get("results", [])[:5]
        return []

    # Run all API calls concurrently
    async with httpx.AsyncClient() as client:
        tasks = [fetch_provider_movies(client, pid) for pid in provider_list]
        results = await asyncio.gather(*tasks)
        
    # Mix the results together and remove duplicates
    all_movies = []
    seen_movie_ids = set()
    
    for provider_movies in results:
        for movie in provider_movies:
            if movie["id"] not in seen_movie_ids:
                seen_movie_ids.add(movie["id"])
                all_movies.append(movie)
                    
    return {
        "user_mood_input": mood,
        "ai_reasoning": ai_analysis.explanation,
        "selected_genres": ai_analysis.genres,
        "movies_found": all_movies
    }