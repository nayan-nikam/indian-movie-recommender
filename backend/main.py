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

# 2. Initialize the App
app = FastAPI(title="Indian Movie Recommender API")

# 3. Configure CORS for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows your Vercel frontend to connect
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
    
    # NEW LOGIC: Dynamically set the movie limit
    # If the user only selected 1 provider, fetch 10 movies. Otherwise, fetch 5 per provider.
    movie_limit = 10 if len(provider_list) == 1 else 5
    
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
            # Apply the dynamic limit here instead of hardcoding [:5]
            return response.json().get("results", [])[:movie_limit]
        return []

    # Run all API calls concurrently
    async with httpx.AsyncClient() as client:
        tasks = [fetch_provider_movies(client, pid) for pid in provider_list]
        results = await asyncio.gather(*tasks)
        
    # Mix the results and track WHICH platforms have the movie
    all_movies_dict = {}
    
    for index, provider_movies in enumerate(results):
        current_provider_id = int(provider_list[index]) 
        
        for movie in provider_movies:
            movie_id = movie["id"]
            
            if movie_id not in all_movies_dict:
                # First time seeing this movie: inject our custom 'available_on' list
                movie["available_on"] = [current_provider_id]
                all_movies_dict[movie_id] = movie
            else:
                # We already have this movie from another platform! 
                # Just add this new provider ID to the existing list.
                all_movies_dict[movie_id]["available_on"].append(current_provider_id)
                    
    # Convert our dictionary back into a simple list to send to React
    all_movies = list(all_movies_dict.values())
                    
    return {
        "user_mood_input": mood,
        "ai_reasoning": ai_analysis.explanation,
        "selected_genres": ai_analysis.genres,
        "movies_found": all_movies
    }