# Manual Personalization Check

Quick manual steps to verify the report card header shows the player's name with correct possessive formatting.

1) Start the server locally.
   - Ensure your virtual environment is active.
   - Run the Flask app and open http://127.0.0.1:5000

2) Set a student name.
   - On the main menu, enter a name in the Student Name field (e.g., `Alex`, `James`).
   - This saves to localStorage automatically.

3) Load or upload a word list, then start the quiz.
   - Use one of the sample word lists in the repo if needed.
   - Proceed through the quiz until the report card appears.

4) Verify the header text.
   - For `Alex`, it should read: `Alex's Report Card!`
   - For `James`, it should read: `James' Report Card!`

Troubleshooting:
- If redirected back to the menu from /quiz, ensure a wordbank is loaded first.
- Clear localStorage key `studentName` from DevTools > Application if needed and retry.
