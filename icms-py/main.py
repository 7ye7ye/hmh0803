from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from facial_recognition import facial

app = FastAPI(
    title="ICMS - Intelligent Camera Management System",
    description="API for managing video streams and AI-based analysis tasks",
    version="1.0.0"
)

# Include routers
app.include_router(facial.router, tags=["facial"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 