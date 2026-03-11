@echo off
echo ========================================
echo   AI Trading Agent - Local Setup
echo ========================================
echo.

echo Step 1: Checking if Hardhat node is running...
curl -s http://localhost:8545 >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Hardhat node is NOT running
    echo.
    echo Please open a NEW terminal and run:
    echo   npm run node
    echo.
    echo Then press any key to continue...
    pause >nul
) else (
    echo [OK] Hardhat node is running!
)

echo.
echo Step 2: Running the AI Agent...
echo.
cd agent
python main_production.py

pause
