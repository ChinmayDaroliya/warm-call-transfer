from fastapi import FastAPI
import logging
from contextlib import asynccontextmanager
import uvicorn
from app.config import Settings


#configure logging
#its just like console.log in js
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#its like special decorator in python and it turns async function into a context manager
#@ are like annotations in spring boot but here they are decorators
@asynccontextmanager
async def lifespan(app:FastAPI):
    #startup
    logger.info("Starting up...")
    yield
    #shutdown
    logger.info("Shutting down...") 


# Initialize FastAPI app (like Express in Node.js)
app = FastAPI(
    title="Warm Transfer System",
    description="LiveKit based warm transfer system with LLM integration",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {"message" : "Backend is working from app/main.py"}

@app.get("/health")
async def health_check():
    return {"status":"healthy" , "message":"service is running"}



# Start FastAPI server with Uvicorn; auto-reloads on code changes
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host = Settings.HOST,
        port = Settings.PORT,
        reload = Settings.DEBUG 
    )