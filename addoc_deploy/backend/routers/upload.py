from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
import uuid
from datetime import datetime

router = APIRouter()

UPLOAD_DIR = "uploads"

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Generate path: uploads/{YYYY}/{MM}/{uuid}.ext
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        file_ext = os.path.splitext(file.filename)[1]
        new_filename = f"{uuid.uuid4()}{file_ext}"
        
        directory = os.path.join(UPLOAD_DIR, year, month)
        os.makedirs(directory, exist_ok=True)
        
        file_path = os.path.join(directory, new_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Return relative URL
        url_path = f"/uploads/{year}/{month}/{new_filename}"
        return {"url": url_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
