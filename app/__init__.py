from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router as file_router

def create_app() -> FastAPI:
    app = FastAPI(title="Waves.Youhu.Metadata", version="1.0.0", description="简单的HTTP文件下载服务（含防爆破、防DOS）")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(file_router, prefix="/files")
    @app.get("/health")
    def health():
        return {"success": True, "message": "ok"}
    return app
