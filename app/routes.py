import os
from typing import Optional
from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
from .security import rate_limit, path_guard, record_404

router = APIRouter(tags=["Files"]) 

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage"))
RESOURCE_ROOT = os.path.join(BASE_DIR, "resource")
MAP_ROOT = os.path.join(BASE_DIR, "map")

def _safe_join(root: str, path: str) -> Optional[str]:
    abs_path = os.path.abspath(os.path.join(root, path))
    if abs_path.startswith(root) and os.path.exists(abs_path):
        return abs_path
    return None

@router.get("/resource/{category}/{path:path}", summary="下载资源文件")
def download_resource(category: str, path: str, request: Request):
    rate_limit(request)
    path_guard(path)
    # category 子目录保护
    safe_root = os.path.join(RESOURCE_ROOT, category)
    if not os.path.isdir(safe_root):
        record_404(request)
        return {"success": False, "error": "category not found"}
    abs_path = _safe_join(safe_root, path)
    if not abs_path:
        record_404(request)
        return {"success": False, "error": "file not found"}
    return FileResponse(abs_path, filename=os.path.basename(abs_path), headers={"Content-Disposition": f"attachment; filename={os.path.basename(abs_path)}"})

@router.get("/map/{path:path}", summary="下载map配置文件")
def download_map(path: str, request: Request):
    rate_limit(request)
    path_guard(path)
    abs_path = _safe_join(MAP_ROOT, path)
    if not abs_path:
        record_404(request)
        return {"success": False, "error": "file not found"}
    return FileResponse(abs_path, filename=os.path.basename(abs_path), headers={"Content-Disposition": f"attachment; filename={os.path.basename(abs_path)}"})
