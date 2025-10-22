@echo off
echo === Quick Git Push - ALL CHANGES ===
echo.
echo Checking status...
git status
echo.
echo Adding ALL files...
git add .
echo.
echo Committing changes...
git commit -m "CRITICAL FIX: Default wordbank parser and production stability - FIXED: load_default_wordbank parser for current file format (word|definition. Example: sentence|) - Added proper splitting of definition and example sentences with blank insertion - Enhanced error handling and logging in default word loading - Fixed Procfile to use single worker (--workers 1) to prevent WORD_STORAGE desync - Simplified startQuiz navigation to avoid fetch/redirect races - Added cache-busting to initial wordbank check to prevent stale 0-word responses - Enhanced logging in get_wordbank for debugging default fallback - All session flags properly managed for clear/upload workflow"
echo.
echo Pushing to GitHub...
git push origin main
echo.
echo Done!
pause
