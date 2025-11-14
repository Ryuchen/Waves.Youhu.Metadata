import time
import os
from typing import Dict
from fastapi import Request, HTTPException

_rate: Dict[str, list] = {}
_ban: Dict[str, float] = {}
_fail404: Dict[str, int] = {}

RATE_PER_WINDOW = int(os.getenv("RATE_PER_WINDOW", "30"))
RATE_WINDOW_SEC = int(os.getenv("RATE_WINDOW_SEC", "10"))
MAX_PATH_LEN = int(os.getenv("MAX_PATH_LEN", "512"))
MAX_SEGMENTS = int(os.getenv("MAX_SEGMENTS", "20"))
FAIL_404_LIMIT = int(os.getenv("FAIL_404_LIMIT", "10"))
BAN_SECONDS = int(os.getenv("BAN_SECONDS", "300"))

def client_ip(req: Request) -> str:
    return req.client.host if req.client else "unknown"

def rate_limit(req: Request):
    ip = client_ip(req)
    now = time.time()
    # ban check
    until = _ban.get(ip, 0)
    if until and until > now:
        raise HTTPException(status_code=429, detail="BANNED")
    bucket = [t for t in _rate.get(ip, []) if now - t <= RATE_WINDOW_SEC]
    if len(bucket) >= RATE_PER_WINDOW:
        raise HTTPException(status_code=429, detail="Too many requests")
    bucket.append(now)
    _rate[ip] = bucket

def path_guard(path: str):
    if not path or len(path) > MAX_PATH_LEN:
        raise HTTPException(status_code=400, detail="Invalid path")
    # normalize and simple traversal check
    if ".." in path or path.startswith("/") or path.startswith("\\"):
        raise HTTPException(status_code=400, detail="Invalid path")
    if path.count("/") > MAX_SEGMENTS:
        raise HTTPException(status_code=400, detail="Too many segments")

def record_404(req: Request):
    ip = client_ip(req)
    cnt = _fail404.get(ip, 0) + 1
    _fail404[ip] = cnt
    if cnt >= FAIL_404_LIMIT:
        _ban[ip] = time.time() + BAN_SECONDS
        _fail404[ip] = 0
