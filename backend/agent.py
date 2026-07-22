from typing import List
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END

# 1. Define the exact structure we want the AI to return
class MoodAnalysis(BaseModel):
    genres: List[str] = Field(description="List of matching TMDB Genre IDs. Options: 28 (Action), 35 (Comedy), 18 (Drama), 10749 (Romance), 27 (Horror), 53 (Thriller), 9648 (Mystery)")
    search_keywords: List[str] = Field(description="2-3 contextual keywords tailored for cinema (e.g., 'heartbreak', 'wholesome', 'mass', 'feel good')")
    explanation: str = Field(description="A short 1-sentence reason why these genres fit the user's vibe.")

# 2. Define the State (the data memory shared across the graph)
class GraphState(BaseModel):
    user_mood: str
    analysis: MoodAnalysis = None

# 3. Create the Node function that talks to the LLM
def analyze_mood_node(state: GraphState):
    # We are now using gemini-3.5-flash as it is the current active model
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.2)
    
    # Force the LLM to strictly output our Pydantic structure
    structured_llm = llm.with_structured_output(MoodAnalysis)
    
    system_prompt = (
        "You are an expert film curator specializing in world cinema (Bollywood, hollywood, Tollywood, Kollywood, etc.). "
        "Analyze the user's emotional state, vibe, or current mood. Map it to the most appropriate movie genres "
        "and if user asking for only one particular genre depending on mood so just suggest one genre otherwise you can suggest multiples genres."
    )
    
    # Ask the structured LLM
    result = structured_llm.invoke([
        ("system", system_prompt),
        ("user", f"Analyze this mood: {state.user_mood}")
    ])
    
    # Return the updated state
    return {"analysis": result}

# 4. Assemble the LangGraph Workflow
workflow = StateGraph(GraphState)

# Add our node to the graph layout
workflow.add_node("analyze_mood", analyze_mood_node)

# Define the pathways (Edges)
workflow.add_edge(START, "analyze_mood")
workflow.add_edge("analyze_mood", END)

# Compile the graph into an executable application
mood_agent = workflow.compile()