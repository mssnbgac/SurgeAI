@echo off
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║   Push SurgeAI to GitHub                                      ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

echo This script will push your code to GitHub.
echo Repository: https://github.com/mssnbgac/surge.git
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

echo.
echo [1/6] Checking git status...
git status
echo.

echo [2/6] Adding all files...
git add .
echo ✅ Files added
echo.

echo [3/6] Committing changes...
git commit -m "feat: Complete SurgeAI implementation - ERC-8004 Trading Agent"
if %ERRORLEVEL% EQU 0 (
    echo ✅ Changes committed
) else (
    echo ⚠️  No changes to commit or already committed
)
echo.

echo [4/6] Checking remote...
git remote -v
echo.

echo [5/6] Setting branch to main...
git branch -M main
echo ✅ Branch set to main
echo.

echo [6/6] Pushing to GitHub...
echo.
echo ⚠️  You may be prompted for GitHub credentials:
echo    - Username: your GitHub username
echo    - Password: use Personal Access Token (not your password!)
echo.
echo    Get token at: https://github.com/settings/tokens
echo.

git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ╔════════════════════════════════════════════════════════════════╗
    echo ║                                                                ║
    echo ║   ✅ SUCCESS! Code pushed to GitHub                           ║
    echo ║                                                                ║
    echo ║   Repository: https://github.com/mssnbgac/surge                ║
    echo ║                                                                ║
    echo ║   Next steps:                                                  ║
    echo ║   1. Visit the repository to verify                            ║
    echo ║   2. Add topics: ethereum, defi, trading-bot, erc-8004        ║
    echo ║   3. Create release: v1.0.0                                    ║
    echo ║   4. Update repository description                             ║
    echo ║                                                                ║
    echo ╚════════════════════════════════════════════════════════════════╝
) else (
    echo.
    echo ╔════════════════════════════════════════════════════════════════╗
    echo ║                                                                ║
    echo ║   ❌ PUSH FAILED                                               ║
    echo ║                                                                ║
    echo ║   Common solutions:                                            ║
    echo ║   1. Use Personal Access Token instead of password             ║
    echo ║   2. Check if remote is correct: git remote -v                 ║
    echo ║   3. Try: git pull origin main --rebase                        ║
    echo ║   4. See PUSH_TO_GITHUB.md for detailed help                   ║
    echo ║                                                                ║
    echo ╚════════════════════════════════════════════════════════════════╝
)

echo.
echo Press any key to close...
pause >nul
