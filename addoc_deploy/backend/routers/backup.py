from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import shutil
import os
from datetime import datetime
import re
import models
from urllib.parse import unquote
from routers.auth import get_current_user
from database import SessionLocal

router = APIRouter(prefix="/backup", tags=["backup"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_admin(current_user: models.User):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

def cleanup_temp_files(path: str):
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

@router.get("")
def backup_system(background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    check_admin(current_user)
    
    # Setup paths
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir = f"temp_backup_{timestamp}"
    assets_dir = os.path.join(temp_dir, "assets")
    
    os.makedirs(assets_dir, exist_ok=True)
    
    # Query all data
    categories = db.query(models.Category).all()
    
    # Regex for finding image links: ![alt](/uploads/xxx.jpg)
    img_pattern = re.compile(r'!\[(.*?)\]\(/uploads/(.*?)\)')
    
    # Process structure
    for category in categories:
        cat_dir = os.path.join(temp_dir, sanitize_filename(category.name))
        os.makedirs(cat_dir, exist_ok=True)
        
        for sub in category.sub_categories:
            sub_dir = os.path.join(cat_dir, sanitize_filename(sub.name))
            os.makedirs(sub_dir, exist_ok=True)
            
            for doc in sub.documents:
                doc_filename = f"{sanitize_filename(doc.title)}.md"
                doc_path = os.path.join(sub_dir, doc_filename)
                
                content = doc.content or ""
                
                # Handle images
                def replace_image(match):
                    alt_text = match.group(1)
                    # 1. Decode URL to handle spaces/special chars 
                    raw_filename = match.group(2) # e.g. "2026/01/xxx.png" 
                    img_filename = unquote(raw_filename)
                    
                    # 2. Construct Source Path (Use normpath for Windows safety) 
                    source_path = os.path.normpath(os.path.join("uploads", img_filename))
                    
                    # Fix: Check if source exists before copying to avoid crash
                    if not os.path.exists(source_path):
                        print(f"Warning: Missing image source: {source_path}")
                        return match.group(0)

                    try:
                        # 3. Construct Dest Path 
                        dest_path = os.path.normpath(os.path.join(assets_dir, img_filename))
                        
                        # 4. CRITICAL FIX: Create subdirectories if they don't exist (e.g. assets/2026/01) 
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        
                        if not os.path.exists(dest_path):
                            shutil.copy2(source_path, dest_path)
                        
                        # 5. Return relative path (Convert back to forward slashes for Markdown) 
                        # Using explicit string replacement to ensure Markdown compatibility on Windows 
                        relative_path = f"../../assets/{img_filename}".replace("\\", "/") 
                        return f"![{alt_text}]({relative_path})"
                        
                    except Exception as e:
                        print(f"Error processing image {source_path}: {e}")
                        return match.group(0)
                
                new_content = img_pattern.sub(replace_image, content)
                
                # Write file
                with open(doc_path, "w", encoding="utf-8") as f:
                    f.write(f"# {doc.title}\n\n")
                    f.write(new_content)
    
    # Create ZIP
    zip_filename = f"backup_{timestamp}"
    shutil.make_archive(zip_filename, 'zip', temp_dir)
    zip_path = f"{zip_filename}.zip"
    
    # Cleanup temp dir immediately, zip file later
    shutil.rmtree(temp_dir)
    background_tasks.add_task(cleanup_temp_files, zip_path)
    
    return FileResponse(zip_path, filename=zip_path, media_type="application/zip")

def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name)
