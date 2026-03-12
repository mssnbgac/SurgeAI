@echo off
echo ========================================
echo   PUSHING TO GITHUB
echo ========================================
echo.

echo Step 1: Adding all files...
git add .
if %errorlevel% neq 0 (
    echo ERROR: Failed to add files
    pause
    exit /b 1
)
echo ✓ Files added
echo.

echo Step 2: Creating commit...
git commit -m "Complete AI Trading Agent with all hackathon features"
if %errorlevel% neq 0 (
    echo ERROR: Failed to commit
    echo Note: If nothing to commit, this is normal
    pause
    exit /b 1
)
echo ✓ Commit created
echo.

echo Step 3: Pushing to GitHub...
git push origin main
if %errorlevel% neq 0 (
    echo ERROR: Failed to push
    echo.
    echo Possible solutions:
    echo 1. Check your internet connection
    echo 2. Verify GitHub credentials
    echo 3. Try: git push -u origin main
    pause
    exit /b 1
)
echo ✓ Pushed successfully!
echo.

echo ========================================
echo   SUCCESS!
echo ========================================
echo.
echo Your code is now on GitHub:
echo https://github.com/mssnbgac/SurgeAI
echo.
pause
