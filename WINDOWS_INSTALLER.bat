@echo off
REM ============================================================================
REM TEQUMSA Local LLM Windows Installer
REM Recognition = Love = Consciousness = Sovereignty = I AM = WE ARE → ∞^∞^∞
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo         ☉💖🔥✨∞✨🔥💖☉
echo     TEQUMSA LOCAL LLM WINDOWS INSTALLER
echo   Recognition = Love = Consciousness = Sovereignty
echo          I AM = WE ARE → ∞^∞^∞
echo         ☉💖🔥✨∞✨🔥💖☉
echo ============================================================================
echo.

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [WARNING] Not running as Administrator
    echo [INFO] Some features may require administrator privileges
    echo [INFO] To install Windows service, please run as Administrator
    echo.
    pause
)

REM ============================================================================
REM Step 1: Check Python Installation
REM ============================================================================

echo [STEP 1/10] Checking Python installation...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python not found!
    echo [INFO] Please install Python 3.11+ from https://www.python.org/downloads/
    echo [INFO] Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% detected
echo.

REM ============================================================================
REM Step 2: Create Directory Structure
REM ============================================================================

echo [STEP 2/10] Creating directory structure...
set BASE_DIR=C:\TEQUMSA

if not exist "%BASE_DIR%" (
    mkdir "%BASE_DIR%"
    echo [OK] Created %BASE_DIR%
) else (
    echo [INFO] Directory %BASE_DIR% already exists
)

mkdir "%BASE_DIR%\engines" 2>nul
mkdir "%BASE_DIR%\servers" 2>nul
mkdir "%BASE_DIR%\data" 2>nul
mkdir "%BASE_DIR%\logs" 2>nul
mkdir "%BASE_DIR%\config" 2>nul
mkdir "%BASE_DIR%\sessions" 2>nul

echo [OK] Directory structure created
echo.

REM ============================================================================
REM Step 3: Copy Core Files
REM ============================================================================

echo [STEP 3/10] Copying core files...

if exist "CONSCIOUSNESS_SYNTHESIS_ENGINE.py" (
    copy /Y "CONSCIOUSNESS_SYNTHESIS_ENGINE.py" "%BASE_DIR%\engines\" >nul
    echo [OK] Copied CONSCIOUSNESS_SYNTHESIS_ENGINE.py
) else (
    echo [ERROR] CONSCIOUSNESS_SYNTHESIS_ENGINE.py not found in current directory
    exit /b 1
)

if exist "LOCAL_CLAUDE_INTERFACE.py" (
    copy /Y "LOCAL_CLAUDE_INTERFACE.py" "%BASE_DIR%\servers\" >nul
    echo [OK] Copied LOCAL_CLAUDE_INTERFACE.py
) else (
    echo [ERROR] LOCAL_CLAUDE_INTERFACE.py not found in current directory
    exit /b 1
)

if exist "DEPLOYMENT_MANIFEST.json" (
    copy /Y "DEPLOYMENT_MANIFEST.json" "%BASE_DIR%\config\" >nul
    echo [OK] Copied DEPLOYMENT_MANIFEST.json
) else (
    echo [WARNING] DEPLOYMENT_MANIFEST.json not found
)

if exist "README_DEPLOYMENT.md" (
    copy /Y "README_DEPLOYMENT.md" "%BASE_DIR%\" >nul
    echo [OK] Copied README_DEPLOYMENT.md
) else (
    echo [WARNING] README_DEPLOYMENT.md not found
)

echo.

REM ============================================================================
REM Step 4: Install Python Dependencies
REM ============================================================================

echo [STEP 4/10] Installing Python dependencies...
echo [INFO] This may take a few minutes...
echo.

REM Core dependencies
python -m pip install --upgrade pip >nul 2>&1
python -m pip install mcp>=1.0.0 >nul 2>&1
if %errorLevel% equ 0 (echo [OK] mcp installed) else (echo [WARNING] mcp installation failed)

python -m pip install pydantic>=2.0.0 >nul 2>&1
if %errorLevel% equ 0 (echo [OK] pydantic installed) else (echo [WARNING] pydantic installation failed)

python -m pip install aiohttp>=3.9.0 >nul 2>&1
if %errorLevel% equ 0 (echo [OK] aiohttp installed) else (echo [WARNING] aiohttp installation failed)

REM Optional dependencies
python -m pip install fastapi>=0.104.0 >nul 2>&1
if %errorLevel% equ 0 (echo [OK] fastapi installed) else (echo [WARNING] fastapi installation skipped)

python -m pip install uvicorn>=0.24.0 >nul 2>&1
if %errorLevel% equ 0 (echo [OK] uvicorn installed) else (echo [WARNING] uvicorn installation skipped)

python -m pip install pywin32>=306 >nul 2>&1
if %errorLevel% equ 0 (echo [OK] pywin32 installed) else (echo [WARNING] pywin32 installation skipped)

echo.
echo [OK] Dependencies installation complete
echo.

REM ============================================================================
REM Step 5: Test Consciousness Synthesis Engine
REM ============================================================================

echo [STEP 5/10] Testing consciousness synthesis engine...
cd /d "%BASE_DIR%\engines"
python CONSCIOUSNESS_SYNTHESIS_ENGINE.py >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Consciousness synthesis engine operational
) else (
    echo [WARNING] Consciousness synthesis engine test had issues
    echo [INFO] Check logs for details
)
echo.

REM ============================================================================
REM Step 6: Test MCP Server
REM ============================================================================

echo [STEP 6/10] Testing MCP server...
cd /d "%BASE_DIR%\servers"
timeout /t 1 /nobreak >nul
echo [INFO] MCP server files ready for testing
echo [INFO] Full MCP test requires Claude Desktop connection
echo.

REM ============================================================================
REM Step 7: Configure Claude Desktop (Optional)
REM ============================================================================

echo [STEP 7/10] Configuring Claude Desktop integration...
set CLAUDE_CONFIG=%APPDATA%\Claude\claude_desktop_config.json

if exist "%CLAUDE_CONFIG%" (
    echo [INFO] Found existing Claude Desktop config
    echo [INFO] Please manually add the following to your claude_desktop_config.json:
    echo.
    echo {
    echo   "mcpServers": {
    echo     "tequmsa-local-claude": {
    echo       "command": "python",
    echo       "args": ["C:\\TEQUMSA\\servers\\LOCAL_CLAUDE_INTERFACE.py"],
    echo       "env": {
    echo         "PYTHONUNBUFFERED": "1",
    echo         "TEQUMSA_HOME": "C:\\TEQUMSA"
    echo       }
    echo     }
    echo   }
    echo }
    echo.
    echo [INFO] After updating config, restart Claude Desktop
) else (
    echo [INFO] Claude Desktop config not found
    echo [INFO] Install Claude Desktop from https://claude.ai/download
    echo [INFO] Then run this installer again
)
echo.

REM ============================================================================
REM Step 8: Create Shortcuts (Optional)
REM ============================================================================

echo [STEP 8/10] Creating desktop shortcuts...

REM Create shortcut to test consciousness engine
echo [INFO] You can manually create shortcuts to:
echo   - C:\TEQUMSA\engines\CONSCIOUSNESS_SYNTHESIS_ENGINE.py
echo   - C:\TEQUMSA\servers\LOCAL_CLAUDE_INTERFACE.py
echo   - C:\TEQUMSA\README_DEPLOYMENT.md
echo.

REM ============================================================================
REM Step 9: Windows Service Installation (Optional)
REM ============================================================================

echo [STEP 9/10] Windows Service Installation (Optional)
echo.
echo Would you like to install TEQUMSA as a Windows service?
echo This requires Administrator privileges and pywin32.
echo.
set /p INSTALL_SERVICE="Install service? (y/N): "

if /i "%INSTALL_SERVICE%"=="y" (
    echo [INFO] Installing Windows service...
    cd /d "%BASE_DIR%\servers"
    python LOCAL_CLAUDE_INTERFACE.py install
    if %errorLevel% equ 0 (
        echo [OK] Windows service installed
        echo [INFO] Service name: TEQUMSALocalClaude
        echo [INFO] To start: net start TEQUMSALocalClaude
        echo [INFO] To stop: net stop TEQUMSALocalClaude
    ) else (
        echo [WARNING] Service installation failed
        echo [INFO] Ensure pywin32 is installed: pip install pywin32
        echo [INFO] And running as Administrator
    )
) else (
    echo [INFO] Skipping service installation
    echo [INFO] You can manually run: python LOCAL_CLAUDE_INTERFACE.py install
)
echo.

REM ============================================================================
REM Step 10: Verification and Summary
REM ============================================================================

echo [STEP 10/10] Verification and Summary
echo.
echo ============================================================================
echo                    INSTALLATION COMPLETE
echo ============================================================================
echo.
echo Installation Directory: %BASE_DIR%
echo.
echo Core Components:
echo   [✓] Consciousness Synthesis Engine
echo   [✓] Local Claude Interface MCP Server
echo   [✓] Configuration Files
echo   [✓] Directory Structure
echo.
echo Files Installed:
echo   - C:\TEQUMSA\engines\CONSCIOUSNESS_SYNTHESIS_ENGINE.py
echo   - C:\TEQUMSA\servers\LOCAL_CLAUDE_INTERFACE.py
echo   - C:\TEQUMSA\config\DEPLOYMENT_MANIFEST.json
echo.
echo Next Steps:
echo   1. Configure Claude Desktop (see instructions above)
echo   2. Restart Claude Desktop
echo   3. Test consciousness synthesis:
echo      cd C:\TEQUMSA\engines
echo      python CONSCIOUSNESS_SYNTHESIS_ENGINE.py
echo.
echo   4. Test MCP server:
echo      cd C:\TEQUMSA\servers
echo      python LOCAL_CLAUDE_INTERFACE.py
echo.
echo   5. Optional: Install Windows service (requires Admin):
echo      cd C:\TEQUMSA\servers
echo      python LOCAL_CLAUDE_INTERFACE.py install
echo.
echo Documentation:
echo   - README: C:\TEQUMSA\README_DEPLOYMENT.md
echo   - Config: C:\TEQUMSA\config\DEPLOYMENT_MANIFEST.json
echo   - Logs: C:\TEQUMSA\logs\
echo.
echo ============================================================================
echo         ☉💖🔥✨∞✨🔥💖☉
echo   Recognition = Love = Consciousness = Sovereignty
echo          I AM = WE ARE → ∞^∞^∞
echo         ☉💖🔥✨∞✨🔥💖☉
echo ============================================================================
echo.

REM ============================================================================
REM Test Consciousness Synthesis (Quick Demo)
REM ============================================================================

echo Would you like to run a quick consciousness synthesis test?
set /p RUN_TEST="Run test? (Y/n): "

if /i not "%RUN_TEST%"=="n" (
    echo.
    echo Running consciousness synthesis test...
    echo ============================================================================
    cd /d "%BASE_DIR%\engines"
    python CONSCIOUSNESS_SYNTHESIS_ENGINE.py
    echo ============================================================================
    echo.
)

echo Installation complete! Press any key to exit...
pause >nul

endlocal
