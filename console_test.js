// 🧪 PASTE THIS INTO BROWSER CONSOLE AT http://localhost:5000/quiz

console.log("🧪 BeeSmart Retry Flow Console Test");
console.log("================================");

// Check if BeeSmart object exists
if (typeof QuizGame !== 'undefined') {
    console.log("✅ QuizGame object found");
    
    // Check for retry choice UI elements
    const retryYes = document.getElementById('retryChoiceYes');
    const retryNo = document.getElementById('retryChoiceNo');
    const timer = document.getElementById('retryChoiceTimer');
    
    console.log(`✅ retryChoiceYes button: ${!!retryYes}`);
    console.log(`✅ retryChoiceNo button: ${!!retryNo}`);
    console.log(`✅ retryChoiceTimer display: ${!!timer}`);
    
    // Check for functions
    console.log(`✅ startRetryChoiceCountdown: ${typeof QuizGame.prototype.startRetryChoiceCountdown === 'function'}`);
    console.log(`✅ handleRetryChoiceYes: ${typeof QuizGame.prototype.handleRetryChoiceYes === 'function'}`);
    console.log(`✅ handleRetryChoiceNo: ${typeof QuizGame.prototype.handleRetryChoiceNo === 'function'}`);
    
    console.log("");
    console.log("📋 TO TEST:");
    console.log("1. Spell the word WRONG");
    console.log("2. Press Enter");
    console.log("3. Watch browser console for logs");
    console.log("4. You should see 10-second countdown WITHOUT the answer");
    console.log("5. Click 'Retry' button");
    console.log("6. Watch for 20-second retry window");
    console.log("7. Spell it wrong again");
    console.log("8. Should show 'No more retries' message");
    console.log("");
    console.log("✅ Test setup complete!");
    
} else {
    console.log("❌ QuizGame object not found - page may not be fully loaded");
}
