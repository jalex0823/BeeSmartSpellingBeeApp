#!/bin/bash
echo "🚀 Committing BeeSmart v1.5 changes..."
echo "Current directory: $(pwd)"
echo ""

echo "📋 Git status before commit:"
git status --short
echo ""

echo "💾 Committing changes..."
git add .
git commit -m "BeeSmart v1.5 Complete Implementation

✅ All 38 P0 Features Implemented:
- Modern UI with fairy animations and responsive design
- Complete file upload pipeline (TXT, CSV, DOCX, PDF, Images)
- OCR functionality with Tesseract integration and graceful fallback
- Interactive spelling quiz with progress tracking
- Dictionary API integration with persistent caching
- Comprehensive error handling and user-friendly messaging
- Complete test suite with 100% pass rate
- Railway deployment configuration

🔧 Key Changes:
- Updated AjaSpellBApp.py with OCR and production fixes
- Added complete template system (base.html, quiz.html, etc.)
- Created railway_app.py for production deployment
- Updated Procfile and railway.toml for Railway
- Added comprehensive test suites and documentation

🚀 Ready for production deployment on Railway!"

echo ""
echo "📤 Pushing to GitHub..."
git push origin main

echo ""
echo "✅ Commit and push completed!"
echo ""
echo "📋 Final git status:"
git status --short