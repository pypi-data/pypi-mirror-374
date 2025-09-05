from fastapi import APIRouter
from fastapi.responses import JSONResponse


import os
import psutil
from typing import Tuple
uvicorn_router = APIRouter()


def get_uvicorn_worker_count() -> Tuple[int, str]:
    """
    Detect the number of running Uvicorn workers and return both
    the count and the source of information ("env" or "psutil").

    Returns:
        Tuple[int, str]: (worker_count, source)
    """
    # 1. Check environment variable
    if "UVICORN_WORKERS" in os.environ:
        return int(os.environ["UVICORN_WORKERS"]), "env"

    # 2. Auto-detect via psutil
    try:
        current_pid = os.getpid()
        parent = psutil.Process(current_pid).parent()

        siblings = [
            p for p in parent.children(recursive=False)
            if "uvicorn" in " ".join(p.cmdline())
        ]
        return max(1, len(siblings)), "psutil"
    except Exception:
        # 3. Fallback to 1 if detection fails
        return 1, "fallback"


@uvicorn_router.get("/uvicorn/workers", name="get_uvicorn_worker_count")
async def get_workers():
    """
    Return the current number of active Uvicorn workers
    along with the detection method used.
    """
    count, source = get_uvicorn_worker_count()
    return JSONResponse(content={
        "uvicorn_worker_count": count,
        "source": source
    })