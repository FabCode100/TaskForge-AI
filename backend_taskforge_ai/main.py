"""Entry point to run the FastAPI app in `app.main`.

Run: `python backend_taskforge_ai/main.py` for dev.
"""

import uvicorn


if __name__ == "__main__":
	uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
