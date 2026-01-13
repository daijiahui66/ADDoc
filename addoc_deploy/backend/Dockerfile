# Base Image
FROM python:3.11-slim

# Workdir
WORKDIR /app

# 1. Install Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 2. Copy Code (Backend + Frontend dist)
# We assume the build context contains the prepared 'dist' folder inside
COPY . .

# 3. Create Directories
RUN mkdir -p uploads data

# Expose Port
EXPOSE 8000

# CMD
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
