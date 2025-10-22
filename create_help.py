# Create comprehensive help.html file
with open('templates/help.html', 'w', encoding='utf-8') as f:
    f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BeeSmart Help Guide</title>
    <link rel="icon" type="image/png" href="/static/BeeSmartLogoTransparent.png">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/BeeSmart.css') }}">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 1200px; margin: 0 auto; background: linear-gradient(135deg, #FFF8DC 0%, #FFE5B4 100%); }
        h1 { color: #FFA500; text-align: center; font-size: 2.5em; margin-bottom: 10px; }
        h2 { color: #FF8C00; border-bottom: 2px solid #FFD700; padding-bottom: 10px; margin-top: 40px; }
        h3 { color: #FF8C00; margin-top: 25px; }
        .back-btn { display: inline-block; background: #FFD700; color: #333; padding: 12px 30px; border-radius: 25px; text-decoration: none; font-weight: bold; margin: 20px 0; box-shadow: 0 4px 8px rgba(0,0,0,0.2); transition: all 0.2s; }
        .back-btn:hover { background: #FFA500; transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.3); }
        .tip { background: #FFF8DC; border-left: 4px solid #FFD700; padding: 15px; margin: 20px 0; border-radius: 5px; }
        pre { background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; color: #d63384; }
        kbd { background: #333; color: white; padding: 3px 8px; border-radius: 4px; font-family: monospace; font-size: 0.9em; box-shadow: 0 2px 4px rgba(0,0,0,0.3); }
        .toc { background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 30px 0; }
        .toc ul { column-count: 2; column-gap: 30px; list-style: none; }
        .toc li { margin: 10px 0; }
        .toc a { color: #FF8C00; text-decoration: none; }
        .toc a:hover { text-decoration: underline; color: #FFD700; }
        .section { background: white; padding: 30px; border-radius: 15px; margin: 20px 0; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        @media(max-width: 768px) { .toc ul { column-count: 1; } body { padding: 10px; } .section { padding: 20px; } }
    </style>
</head>
<body>
    <h1>🐝 BeeSmart Spelling Bee - Complete Guide</h1>
    <p style="text-align: center; font-size: 1.2em; color: #666;">Everything you need to know about BeeSmart!</p>
    <div style="text-align: center;"><a href="/" class="back-btn">← Back to BeeSmart</a></div>

    <div class="toc">
        <h2>📋 Quick Jump</h2>
        <ul>
            <li><a href="#getting-started">🚀 Getting Started</a></li>
            <li><a href="#uploading">📝 Uploading Words</a></li>
            <li><a href="#quiz">🎯 Quiz Features</a></li>
            <li><a href="#timer">⏱️ Countdown Timer</a></li>
            <li><a href="#battle">⚔️ Battle Mode</a></li>
            <li><a href="#points">🏆 Points System</a></li>
            <li><a href="#profiles">👨‍👩‍👧 Profiles (Coming)</a></li>
            <li><a href="#shortcuts">⌨️ Shortcuts</a></li>
            <li><a href="#troubleshooting">🔧 Troubleshooting</a></li>
        </ul>
    </div>

    <div class="section" id="getting-started">
        <h2>🚀 Getting Started</h2>
        <h3>What is BeeSmart?</h3>
        <p>BeeSmart is an interactive spelling practice app designed for kids. It features voice announcements, visual feedback, and fun bee-themed elements to make learning spelling engaging!</p>
        
        <h3>Quick Start (3 Steps)</h3>
        <ol>
            <li><strong>Upload Words:</strong> CSV, TXT, DOCX, PDF, or take a photo (OCR)</li>
            <li><strong>Start Quiz:</strong> Click "Start Quiz" button</li>
            <li><strong>Practice:</strong> Listen, type your answer, and submit!</li>
        </ol>
        <div class="tip"><strong>💡 Tip:</strong> Click "Start Quiz" without uploading to use the default 50 words!</div>
    </div>

    <div class="section" id="uploading">
        <h2>📝 Uploading Word Lists</h2>
        <h3>Supported Formats</h3>
        <ul>
            <li><strong>CSV Files:</strong> word,definition,sentence</li>
            <li><strong>TXT Files:</strong> One word per line or pipe-delimited (word|sentence|hint)</li>
            <li><strong>Word Documents (.docx):</strong> Word documents with word lists</li>
            <li><strong>PDF Files:</strong> Extract text from PDFs</li>
            <li><strong>Images (OCR):</strong> Photos of printed words (JPG, PNG)</li>
        </ul>
        
        <h3>Format Examples</h3>
        <h4>CSV Format:</h4>
        <pre>word,sentence,hint
elephant,The elephant has a long trunk,Large animal
beautiful,She wore a beautiful dress,Pretty</pre>
        
        <h4>TXT Format (Pipe-delimited):</h4>
        <pre>elephant|The elephant has a long trunk|Large animal
beautiful|She wore a beautiful dress|Pretty</pre>
        
        <div class="tip"><strong>📸 OCR Tip:</strong> Use clear, well-lit photos with printed text (not handwritten) for best results!</div>
    </div>

    <div class="section" id="quiz">
        <h2>🎯 Quiz Features</h2>
        <h3>Voice Announcements</h3>
        <p><strong>Buzzy</strong>, your announcer bee, will:</p>
        <ul>
            <li>🎤 Announce each word clearly</li>
            <li>📖 Read the definition/sentence</li>
            <li>✅ Celebrate correct answers</li>
            <li>💪 Encourage you on mistakes</li>
            <li>⏱️ Announce when timer starts</li>
        </ul>
        
        <h3>Available Buttons</h3>
        <ul>
            <li><strong>🔊 Pronounce Word:</strong> Hear the word again</li>
            <li><strong>🔁 Repeat:</strong> Replay the announcement</li>
            <li><strong>🍯 Honey Hint:</strong> Get a helpful clue (-10 points)</li>
            <li><strong>⏭️ Skip Word:</strong> Move to next word (no penalty)</li>
            <li><strong>📤 Submit:</strong> Submit your answer (or press Enter)</li>
            <li><strong>🚪 Exit Quiz:</strong> Leave and see progress summary</li>
        </ul>
        
        <h3>Visual Feedback</h3>
        <ul>
            <li><strong>✅ Correct:</strong> Green message, points animation, honey fills up!</li>
            <li><strong>❌ Incorrect:</strong> Orange message (encouraging), shows correct spelling</li>
        </ul>
    </div>

    <div class="section" id="timer">
        <h2>⏱️ Countdown Timer</h2>
        <h3>How It Works</h3>
        <ol>
            <li>📢 Word and definition announced</li>
            <li>🎯 Timer announcement: "Your 15 seconds begins now!" (randomized)</li>
            <li>🍯 Honey jar appears and starts draining</li>
            <li>⏰ You have 15 seconds to spell the word</li>
            <li>✅ Timer stops when you submit</li>
        </ol>
        
        <h3>Timer States</h3>
        <ul>
            <li><strong>🟢 Normal (15-6s):</strong> Golden honey, calm animation, bubbles rising</li>
            <li><strong>🟠 Warning (5s):</strong> Orange honey, pulse effect, orange glow</li>
            <li><strong>🔴 Critical (3s):</strong> Red honey, faster pulse, buzz sound, shake</li>
            <li><strong>⏰ Expired:</strong> Empty gray jar - can still answer (soft mode!)</li>
        </ul>
        
        <h3>Timer Bonus Points</h3>
        <p>Each remaining second = 5 bonus points!</p>
        <pre>Example: 8 seconds left = 40 bonus points
Maximum bonus: 75 points (15 × 5)</pre>
        
        <div class="tip"><strong>💡 Soft Mode:</strong> Timer won't auto-submit when time runs out. Accuracy matters more than speed!</div>
    </div>

    <div class="section" id="battle">
        <h2>⚔️ Battle of the Bees</h2>
        <p>Competitive multiplayer mode where students compete on the same word list in real-time!</p>
        
        <h3>How to Start a Battle</h3>
        <ol>
            <li>Click "⚔️ Battle of the Bees" from main menu</li>
            <li>Choose:
                <ul>
                    <li><strong>Create Battle:</strong> Upload words, get 6-digit code</li>
                    <li><strong>Join Battle:</strong> Enter battle code</li>
                </ul>
            </li>
            <li>Enter your name (required for leaderboard)</li>
            <li>Start spelling and compete!</li>
        </ol>
        
        <h3>Live Leaderboard</h3>
        <pre>🏆 Battle Leaderboard - ABC123
━━━━━━━━━━━━━━━━━━━━━━━━
1. 🥇 Sarah  95% (19/20)
2. 🥈 Mike   90% (18/20)
3. 🥉 Emma   85% (17/20)</pre>
        
        <div class="tip"><strong>🎓 Teacher Tip:</strong> Export results as CSV for grading!</div>
    </div>

    <div class="section" id="points">
        <h2>🏆 Points System (Coming Soon)</h2>
        <h3>Point Calculation</h3>
        <pre>Base Score:         100 points
Time Bonus:         5 × seconds remaining
Streak Bonus:       10 × current streak
First Attempt:      +50 points
No Hints:           +25 points

Example: "elephant"
- Time left: 8s
- Streak: 3
- First try, no hints
= 100 + 40 + 30 + 50 + 25 = 245 points!</pre>
        
        <h3>Achievements</h3>
        <ul>
            <li><strong>🌟 Perfect Game (+500):</strong> 100% accuracy, no hints</li>
            <li><strong>⚡ Speed Demon (+200):</strong> Average under 5s per word</li>
            <li><strong>🔥 Hot Streak (+100):</strong> 10+ words correct in a row</li>
            <li><strong>🎯 Comeback Kid (+100):</strong> Correct after 3 wrong</li>
        </ul>
        
        <h3>Levels</h3>
        <pre>Level 1:  0-500      🐝 Busy Bee
Level 5:  5K-8K      🏆 Word Wizard
Level 10: 35K+       🏅 Queen/King Bee</pre>
    </div>

    <div class="section" id="profiles">
        <h2>👨‍👩‍👧 Family Profiles (Coming Soon)</h2>
        <p>Track progress for multiple children with individual profiles!</p>
        <ul>
            <li>📊 Individual progress tracking</li>
            <li>🏆 Personal achievements</li>
            <li>🍯 Honey collection (points)</li>
            <li>📈 Performance history</li>
            <li>👨‍👩‍👧 Family leaderboard</li>
            <li>🔒 PIN-protected parent mode</li>
        </ul>
    </div>

    <div class="section" id="shortcuts">
        <h2>⌨️ Keyboard Shortcuts</h2>
        <table style="width: 100%; border-collapse: collapse;">
            <thead style="background: #FFD700;">
                <tr>
                    <th style="padding: 12px; text-align: left;">Shortcut</th>
                    <th style="padding: 12px; text-align: left;">Action</th>
                </tr>
            </thead>
            <tbody>
                <tr><td style="padding: 10px;"><kbd>Enter</kbd></td><td style="padding: 10px;">Submit answer</td></tr>
                <tr><td style="padding: 10px;"><kbd>Ctrl</kbd>+<kbd>R</kbd></td><td style="padding: 10px;">Repeat word</td></tr>
                <tr><td style="padding: 10px;"><kbd>Ctrl</kbd>+<kbd>H</kbd></td><td style="padding: 10px;">Get hint</td></tr>
                <tr><td style="padding: 10px;"><kbd>Ctrl</kbd>+<kbd>P</kbd></td><td style="padding: 10px;">Pronounce</td></tr>
                <tr><td style="padding: 10px;"><kbd>Ctrl</kbd>+<kbd>S</kbd></td><td style="padding: 10px;">Skip word</td></tr>
                <tr><td style="padding: 10px;"><kbd>Esc</kbd></td><td style="padding: 10px;">Exit quiz</td></tr>
            </tbody>
        </table>
        <div class="tip"><strong>💡 Mac Users:</strong> Use <kbd>Cmd</kbd> instead of <kbd>Ctrl</kbd></div>
    </div>

    <div class="section" id="troubleshooting">
        <h2>🔧 Troubleshooting</h2>
        
        <h3>Voice Not Working</h3>
        <h4>On iOS (iPhone/iPad):</h4>
        <ol>
            <li>Unmute device (check side switch!)</li>
            <li>Tap anywhere on screen to unlock audio</li>
            <li>Go to Settings → Safari → Allow Audio</li>
            <li>Reload page AFTER unmuting</li>
        </ol>
        
        <h4>On Desktop:</h4>
        <ol>
            <li>Check speaker volume</li>
            <li>Allow browser audio permissions</li>
            <li>Try different browser (Chrome recommended)</li>
            <li>Reload page (F5)</li>
        </ol>
        
        <h3>Timer Not Appearing</h3>
        <ul>
            <li>Refresh page (F5 or Cmd+R)</li>
            <li>Start new quiz</li>
            <li>Clear browser cache</li>
            <li>Try different browser</li>
        </ul>
        
        <h3>File Upload Issues</h3>
        <ul>
            <li>Check file size is under 10MB</li>
            <li>Verify format: CSV, TXT, DOCX, PDF, JPG, PNG</li>
            <li>For OCR: Use clear, well-lit photos with printed text</li>
            <li>Try renaming file to remove special characters</li>
        </ul>
        
        <h3>Battle Mode Issues</h3>
        <ul>
            <li>Verify battle code is correct (case-sensitive)</li>
            <li>Check internet connection</li>
            <li>Wait 5-10 seconds for leaderboard updates</li>
            <li>Complete at least one word to appear on leaderboard</li>
        </ul>
    </div>

    <div style="text-align: center; margin: 40px 0; padding: 30px; background: white; border-radius: 15px;">
        <h2>🐝 Happy Spelling!</h2>
        <p style="font-size: 1.1em;">Practice makes perfect! Keep collecting honey and leveling up!</p>
        <a href="/" class="back-btn">← Back to BeeSmart Home</a>
        <p style="font-size: 0.9em; color: #888; margin-top: 30px;">BeeSmart v1.8.0 | Last Updated: October 17, 2025<br>Made with 💛 for young learners everywhere</p>
    </div>
</body>
</html>''')

print("✅ Comprehensive help.html created successfully!")
print("📄 File: templates/help.html")
print("📏 Includes all features: Timer, Battle Mode, Points System, and more!")
