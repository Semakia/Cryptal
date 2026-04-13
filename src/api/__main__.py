"""
Crypto Viz API - Module Entry Point
====================================

This file allows the API to be run as a Python module:
    python -m api

This resolves import issues when running in Docker containers.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False, log_level="info")
