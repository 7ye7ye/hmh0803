from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from facial_recognition.facial import router as facial_stream_router
from facial_recognition.facial_login import router as facial_login_router
import fastapi_cdn_host

# 配置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ICMS - Intelligent Camera Management System",
    description="API for managing video streams and AI-based analysis tasks",
    version="1.0.0"
)

# CORS 配置
origins = [
    "http://localhost",
    "http://localhost:8087",
    "http://localhost:8085",
    "*",  # 开发时可以允许所有源
    "http://121.36.44.77:8090 ",
    "http://121.36.44.77:8085"
]

# 将 CORS 中间件添加到你的 FastAPI 应用中
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """服务启动时的初始化工作"""
    logger.info("服务正在启动...")
    try:
        # Include routers
        app.include_router(facial_stream_router)
        app.include_router(facial_login_router)
        logger.info("所有路由注册成功")
    except Exception as e:
        logger.error(f"服务启动时发生错误: {e}")
        raise

@app.get("/")
async def root():
    """测试根路由是否正常工作"""
    return {"message": "ICMS API 服务正常运行中"}

if __name__ == "__main__":
    import uvicorn
    logger.info("正在启动服务器...")
    try:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        raise