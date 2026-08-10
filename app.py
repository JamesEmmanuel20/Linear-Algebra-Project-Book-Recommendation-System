from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
import uvicorn

# Import the linear algebra recommendation engine
from linear_algebra_engine import BookRecommenderEngine

# Initialize FastAPI application
app = FastAPI(
    title="Linear Algebra Book Recommender",
    description="Vector space model recommendation backend built with FastAPI and NumPy.",
    version="1.0.0"
)

# Mount static directory for CSS and JS assets
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure Jinja2 templates directory
templates = Jinja2Templates(directory="templates")

# Initialize the Linear Algebra matrix engine with the processed dataset
try:
    engine = BookRecommenderEngine("data/book_ratings.csv")
except FileNotFoundError:
    print("Warning: 'data/book_ratings.csv' not found. Please run 'preprocess.py' first.")
    engine = None


# Define request payload schema using Pydantic
class RecommendationRequest(BaseModel):
    user: str = Field(..., example="User_276729", description="Target user row vector key")
    metric: str = Field(default="euclidean", example="euclidean", description="Distance metric: 'euclidean' or 'cosine'")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main web dashboard interface.
    """
    return templates.TemplateResponse(request = request, name = "index.html", context = {"key": "value"})


@app.get("/api/users")
async def get_users():
    """
    Returns the list of all user vectors (rows) available in the matrix.
    """
    if engine is None:
        raise HTTPException(status_code=500, detail="Matrix engine not initialized. Run preprocess.py.")
    return {"users": engine.users}


@app.post("/api/recommend")
async def compute_recommendations(req: RecommendationRequest):
    """
    Executes vector distance calculations across Matrix R in R^(m x n) 
    and returns recommendations based on nearest neighbor vectors.
    """
    if engine is None:
        raise HTTPException(status_code=500, detail="Matrix engine not initialized. Run preprocess.py.")

    if req.user not in engine.users:
        raise HTTPException(status_code=404, detail=f"User '{req.user}' not found in matrix.")

    if req.metric not in ["euclidean", "cosine"]:
        raise HTTPException(status_code=400, detail="Invalid metric. Choose 'euclidean' or 'cosine'.")

    # Generate recommendation dictionary using vector operations
    result = engine.generate_recommendations(target_user=req.user, metric=req.metric)
    return result


@app.get("/api/analytics")
async def get_analytics():
    """
    Computes and returns the item space column mean vector across all user rows.
    """
    if engine is None:
        raise HTTPException(status_code=500, detail="Matrix engine not initialized. Run preprocess.py.")

    averages = engine.compute_item_averages()
    return {
        "books": list(averages.keys()),
        "average_ratings": list(averages.values())
    }


if __name__ == "__main__":
    # Command-line execution support: python app.py
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)