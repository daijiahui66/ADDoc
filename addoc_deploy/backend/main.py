from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import uvicorn
from database import engine, Base, SessionLocal
from routers import auth, upload, structure, docs, search, stats, users, backup, activity
from init_db import init_db
import os

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5175",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure uploads directory exists
os.makedirs("uploads", exist_ok=True)
# Ensure data directory exists for SQLite
os.makedirs("data", exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(structure.router, prefix="/api")
app.include_router(docs.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(backup.router, prefix="/api")
app.include_router(activity.router, prefix="/api/activity", tags=["Activity"])

# Check if dist directory exists for static files (Production/Docker)
dist_path = os.path.join(os.path.dirname(__file__), "dist")
if os.path.exists(dist_path):
    print("Mounting static files from dist directory...")
    # 1. Mount assets
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="assets")
    
    # 2. SPA Catch-all route
    # Must be defined AFTER all API routes
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # If API request not matched (404), raise exception to let FastAPI handle it
        if full_path.startswith("api/") or full_path.startswith("uploads/"):
             raise HTTPException(status_code=404, detail="Not Found")
        
        # Check if specific file exists (e.g. favicon.ico, robots.txt)
        file_path = os.path.join(dist_path, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # Default: Serve index.html for SPA routing
        return FileResponse(os.path.join(dist_path, "index.html"))

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    init_db(db)
    db.close()

@app.get("/api/health")
def read_health():
    return {"status": "ok", "backend": "FastAPI running with uv"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
