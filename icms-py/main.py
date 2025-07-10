from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import video_streams, analysis_tasks

app = FastAPI(
    title="ICMS - Intelligent Camera Management System",
    description="API for managing video streams and AI-based analysis tasks",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(video_streams.router, tags=["Video Streams"])
app.include_router(analysis_tasks.router, tags=["Analysis Tasks"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 