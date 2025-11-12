#!/bin/bash

# BeeSmart Spelling Bee App - Persistent Server Starter
# This script keeps the Flask server running and restarts it if it crashes

cd "$(dirname "$0")"

echo "🐝 Starting BeeSmart Spelling Bee App Server..."
echo "📍 Working Directory: $(pwd)"
echo "🔧 Press Ctrl+C twice quickly to stop the server completely"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Trap to handle cleanup
cleanup() {
    echo ""
    echo "🛑 Stopping server..."
    kill $SERVER_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Keep the server running
while true; do
    echo "🚀 Starting Flask server ($(date '+%Y-%m-%d %H:%M:%S'))..."
    python3 AjaSpellBApp.py &
    SERVER_PID=$!
    
    # Wait for the server process
    wait $SERVER_PID
    EXIT_CODE=$?
    
    # If exit code is 0 or 130 (Ctrl+C), don't restart
    if [ $EXIT_CODE -eq 0 ] || [ $EXIT_CODE -eq 130 ]; then
        echo "✅ Server stopped gracefully"
        break
    fi
    
    echo "⚠️  Server crashed with exit code $EXIT_CODE"
    echo "🔄 Restarting in 3 seconds..."
    sleep 3
done

echo "👋 Server shutdown complete"
