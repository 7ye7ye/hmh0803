from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from facial_recognition import facial

app = FastAPI(
    title="ICMS - Intelligent Camera Management System",
    description="API for managing video streams and AI-based analysis tasks",
    version="1.0.0"
)

# CORS 配置

# 1. 定义允许访问的源列表 (origins)
#    这里应该包含你前端应用的地址。
origins = [
    "http://localhost",
    "http://localhost:8085",

]

# 2. 将 CORS 中间件添加到你的 FastAPI 应用中
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # 允许访问的源
    allow_credentials=True,      # 允许携带 cookies
    allow_methods=["*"],         # 允许所有 HTTP 方法 (GET, POST, PUT, etc.)
    allow_headers=["*"],         # 允许所有 HTTP 请求头
)

# --- CORS 配置结束 ---
# Include routers
app.include_router(facial.router, tags=["facial"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)