@echo off
echo [1/5] Building Frontend...
cd frontend
call npm run build
cd ..

echo [2/5] Preparing Deploy Directory...
if exist addoc_deploy rmdir /s /q addoc_deploy
mkdir addoc_deploy
mkdir addoc_deploy\backend

echo [3/5] Copying Backend Files...
xcopy /E /I /Y backend\* addoc_deploy\backend\
copy backend\Dockerfile addoc_deploy\backend\Dockerfile
copy backend\requirements.txt addoc_deploy\backend\requirements.txt

echo [4/5] Copying Frontend Build to Backend...
xcopy /E /I /Y frontend\dist\* addoc_deploy\backend\dist\

echo [5/5] Copying Docker Config...
copy docker-compose.yml addoc_deploy\docker-compose.yml

echo.
echo ==========================================
echo  Deploy Package Created: ./addoc_deploy
echo ==========================================
echo  1. Upload 'addoc_deploy' folder to NAS
echo  2. Run: cd addoc_deploy && docker-compose up -d --build
echo ==========================================
pause
