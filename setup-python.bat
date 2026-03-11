@echo off
echo Installing Python dependencies...
echo.

cd agent
pip install web3 eth-account python-dotenv numpy requests aiohttp

echo.
echo ✅ Python dependencies installed!
echo.
echo You can now run the agent:
echo   cd agent
echo   python main_production.py
echo.
pause
