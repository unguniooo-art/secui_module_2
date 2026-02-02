@echo off
echo ================================
echo Running Tests
echo ================================
echo.

echo Installing test dependencies...
python -m pip install pytest pytest-cov

echo.
echo Running tests...
python -m pytest tests/ -v

pause
