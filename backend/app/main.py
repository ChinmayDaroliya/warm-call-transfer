from fastapi import FastAPI
import logging
from contextlib import asynccontextmanager
import uvicorn
from app.config import settings
from app.database import init_db
from fastapi.middleware.cors import CORSMiddleware
from routers import calls,agents,transfer,rooms
from fastapi.responses import JSONResponse


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
    await init_db()
    logger.info("Database initialized")
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

# Configure CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.ALLOWED_ORIGINS,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# CORS settings
origins = [
    "http://localhost:3000",  # your frontend origin
    "http://127.0.0.1:3000",  # optional
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # allow frontend to access backend
    allow_credentials=True,
    allow_methods=["*"],             # allow all HTTP methods
    allow_headers=["*"],             # allow all headers
)

# Include routers
app.include_router(calls.router, prefix="/routers/calls", tags=["calls"])
app.include_router(agents.router, prefix="/routers/agents", tags=["agents"])
app.include_router(transfer.router, prefix="/routers/transfer", tags=["transfer"])
app.include_router(rooms.router, prefix="/rooms", tags=["rooms"])

@app.get("/")
async def root():
    return {"message" : "Backend is working from app/main.py"}

@app.get("/health")
async def health_check():
    return {"status":"healthy" , "message":"service is running"}

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Start FastAPI server with Uvicorn; auto-reloads on code changes
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", 
        host = settings.HOST,
        port = settings.PORT,
        reload = settings.DEBUG,
        log_level="info"
    )