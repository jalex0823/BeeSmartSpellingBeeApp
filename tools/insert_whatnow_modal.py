# One-off: insert What Now? modal and script into unified_menu.html
path = "templates/unified_menu.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Find the exact spot: after "    </div>\n\n" and before "    <script>"
anchor = "    </div>\n\n    <script>"
pos = content.find(anchor)
if pos < 0:
    print("Anchor not found")
    exit(1)

modal_html = '''
    <!-- What Now? modal: no scroll, trap focus, close on backdrop/ESC -->
    <div id="whatNowModalOverlay" role="dialog" aria-modal="true" aria-labelledby="whatNowModalTitle" aria-hidden="true" style="
        display: none; position: fixed; inset: 0; z-index: 99999; background: rgba(0,0,0,0.45); align-items: center; justify-content: center; padding: 16px; box-sizing: border-box;
    ">
        <div id="whatNowModal" style="
            background: linear-gradient(135deg, #FFFBF0 0%, #FFF9E6 100%); border-radius: 20px; padding: 1.5rem; max-width: min(92vw, 380px); width: 100%;
            box-shadow: 0 12px 40px rgba(0,0,0,0.2); border: 2px solid rgba(255, 215, 0, 0.4);
            max-height: 90vh; overflow: hidden; display: flex; flex-direction: column;
        ">
            <h2 id="whatNowModalTitle" style="margin: 0 0 1rem; font-size: 1.4rem; color: #5A2C15;">What Now?</h2>
            <ul style="margin: 0 0 1.25rem; padding-left: 1.25rem; font-size: 0.95rem; color: #5A2C15; line-height: 1.6;">
                <li><strong>Play as Guest</strong> — start now (progress won't be saved).</li>
                <li><strong>Register / Sign In</strong> — track your progress or a family member's progress across devices.</li>
            </ul>
            <div style="display: flex; gap: 12px; flex-shrink: 0;">
                <button type="button" id="whatNowContinueBtn" style="
                    flex: 1; height: 48px; border-radius: 12px; font-weight: 700; background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); color: #5A2C15; border: 2px solid rgba(255, 215, 0, 0.6); cursor: pointer;
                ">Continue</button>
                <button type="button" id="whatNowCloseBtn" style="
                    flex: 1; height: 48px; border-radius: 12px; font-weight: 700; background: rgba(255,255,255,0.9); color: #5A2C15; border: 2px solid rgba(139, 69, 19, 0.25); cursor: pointer;
                ">Close</button>
            </div>
        </div>
    </div>

'''

iife = """        // What Now? modal: open/close, trap focus, ESC, backdrop; restore body scroll on close
        (function(){
            var overlay = document.getElementById('whatNowModalOverlay');
            var openBtn = document.getElementById('whatNowBtn');
            var continueBtn = document.getElementById('whatNowContinueBtn');
            var closeBtn = document.getElementById('whatNowCloseBtn');
            function openWhatNow(){ if(overlay){ overlay.style.display='flex'; overlay.setAttribute('aria-hidden','false'); document.body.style.overflow='hidden'; document.documentElement.style.overflow='hidden'; if(closeBtn) closeBtn.focus(); } }
            function closeWhatNow(){ if(overlay){ overlay.style.display='none'; overlay.setAttribute('aria-hidden','true'); document.body.style.overflow=''; document.documentElement.style.overflow=''; if(openBtn) openBtn.focus(); } }
            if(openBtn) openBtn.addEventListener('click', openWhatNow);
            if(continueBtn) continueBtn.addEventListener('click', closeWhatNow);
            if(closeBtn) closeBtn.addEventListener('click', closeWhatNow);
            if(overlay) overlay.addEventListener('click', function(e){ if(e.target===overlay) closeWhatNow(); });
            document.addEventListener('keydown', function(e){ if(e.key==='Escape'&& overlay && overlay.style.display==='flex'){ closeWhatNow(); e.preventDefault(); } });
        })();
"""

# Insert modal HTML before <script> (keep "    <script>" from original)
content = content[:pos + len("    </div>\n\n")] + modal_html + content[pos + len("    </div>\n\n"):]

# Insert IIFE right after "<script>\n"
pos2 = content.find("    <script>")
if pos2 < 0:
    print("script tag not found")
    exit(1)
pos2 += len("    <script>\n")
content = content[:pos2] + iife + content[pos2:]

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Inserted What Now? modal and script.")
