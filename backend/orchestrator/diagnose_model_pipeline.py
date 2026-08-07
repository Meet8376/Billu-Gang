"""Step-by-Step Diagnostic Tool for Gemini Model Request Pipeline.

Executes 4 sequential diagnostic checks to pinpoint the exact failure location:
- Step 1: Environment API Key Verification
- Step 2: Direct Gemini Model API Connection Test
- Step 3: FastAPI Backend Server Health Check (http://localhost:8000)
- Step 4: End-to-End HTTP /api/v1/run Endpoint Dispatch
"""

import os
import sys
import asyncio
import logging
import urllib.request
import json

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def check_step_1_env():
    logger.info("\n--- STEP 1: Checking Environment API Keys ---")
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    google_key = os.environ.get("GOOGLE_API_KEY", "")
    
    if gemini_key:
        logger.info(f"[PASS] GEMINI_API_KEY is set (length: {len(gemini_key)}, prefix: '{gemini_key[:6]}...')")
    elif google_key:
        logger.info(f"[PASS] GOOGLE_API_KEY is set (length: {len(google_key)}, prefix: '{google_key[:6]}...')")
    else:
        logger.warning("[WARN] Neither GEMINI_API_KEY nor GOOGLE_API_KEY is set in process environment.")
        logger.warning("       Pass your key via: $env:GEMINI_API_KEY='your_key' or entering it in CLI prompt.")


async def check_step_2_direct_model_adapter():
    logger.info("\n--- STEP 2: Testing Direct Gemini Model API Connection ---")
    from backend.core.adapters.gemini_adapter import GeminiAdapter

    adapter = GeminiAdapter(model_name="gemini-3.5-flash-lite")
    logger.info(f"Initialized GeminiAdapter (Target Model: '{adapter.model_name}')")

    try:
        res = await adapter.complete(
            messages=[{"role": "user", "content": "Respond with 'CONNECTED' if you receive this."}],
            system_prompt="Diagnostic test."
        )
        logger.info(f"[PASS] Model Response Received! Content: {res.content[:150]}")
    except Exception as err:
        logger.error(f"[FAIL] Direct Gemini Model request failed: {err}")


async def check_step_3_backend_server_health():
    logger.info("\n--- STEP 3: Checking FastAPI Backend Server (http://localhost:8000) ---")
    url = "http://localhost:8000/health"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            logger.info(f"[PASS] FastAPI Backend Server is UP and healthy! Response: {data}")
            return True
    except Exception as err:
        logger.error(f"[FAIL] Cannot connect to FastAPI Backend at http://localhost:8000: {err}")
        logger.error("       Reason: FastAPI server is not running in background.")
        logger.error("       Fix: Run 'python -m uvicorn backend.core.main:app --port 8000' in another terminal.")
        return False


async def check_step_4_http_run_endpoint():
    logger.info("\n--- STEP 4: Testing End-to-End HTTP /api/v1/run Endpoint Dispatch ---")
    url = "http://localhost:8000/api/v1/run"
    payload = {
        "session_id": "diag-sess-001",
        "prompt": "Test AI code review dispatch",
        "model_name": "gemini-3.5-flash-lite",
        "workspace_path": PROJECT_ROOT,
        "api_key": os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")
    }
    
    data_bytes = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data_bytes, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            logger.info(f"[PASS] HTTP /api/v1/run succeeded! Status: {data.get('status')}, Message: {data.get('message')}")
    except Exception as err:
        logger.error(f"[FAIL] HTTP /api/v1/run request failed: {err}")


async def main():
    logger.info("=============================================================")
    logger.info("      Gemini Model Pipeline Step-by-Step Diagnostic Tool     ")
    logger.info("=============================================================")
    await check_step_1_env()
    await check_step_2_direct_model_adapter()
    server_up = await check_step_3_backend_server_health()
    if server_up:
        await check_step_4_http_run_endpoint()
    logger.info("=============================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
