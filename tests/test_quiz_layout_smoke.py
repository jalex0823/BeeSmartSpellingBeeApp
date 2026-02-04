"""
Smoke tests for quiz page: functionality, syntax, and layout.

- Ensures quiz template renders and all required elements are present.
- Ensures no duplicate IDs (would break JS and a11y).
- Ensures layout structure order (header, crest/avatar, card, actions).
- Ensures full-page scroll (no trapped scroll); no overlapping fixed elements over main content.

Run: pytest tests/test_quiz_layout_smoke.py -v
"""

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def app():
    import AjaSpellBApp
    AjaSpellBApp.app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        PROPAGATE_EXCEPTIONS=True,
    )
    return AjaSpellBApp.app


@pytest.fixture(scope="module")
def client(app):
    with app.test_client() as c:
        with app.app_context():
            yield c


def _render_quiz_html(app, user_name=None):
    with app.test_request_context("/"):
        from flask import render_template
        return render_template("quiz.html", user_name=user_name, timestamp=12345)


# ─── Required elements (IDs and classes) ─────────────────────────────────────

QUIZ_REQUIRED_IDS = [
    "quizContainer",
    "quizCard",
    "mascotBee3D",
    "progressText",
    "correctCount",
    "incorrectCount",
    "streakCount",
    "sessionPoints",
    "quizHeaderBadge",
    "morphContainer",
    "countdownContainer",
    "voiceVisualizer",
    "spellingInput",
    "answerAreaContainer",
    "keyboardHost",
    "quizKeyboardContainer",
    "quizActionButtons",
    "submitButton",
    "speakButton",
    "showDefinitionButton",
    "showSentenceButton",
    "skipButton",
    "getHintButton",
    "exitQuizButton",
    "feedbackArea",
    "definitionDisplay",
]

QUIZ_REQUIRED_CLASSES_OR_MARKERS = [
    "quiz-header",
    "quiz-card",
    "quiz-card-crest-avatar",
    "quiz-card-crest",
    "card-scroll",
    "quiz-card-top",
    "question-area",
    "answer-and-keyboard",
    "quiz-answer-area",
    "actions-area",
    "quiz-buttons",
]


def test_quiz_template_renders(app):
    """Quiz template renders without Jinja/syntax errors."""
    html = _render_quiz_html(app)
    assert "route-quiz" in html or "quiz" in html.lower()
    assert "QuizKeyboard" in html or "quiz_keyboard" in html.lower()


def test_quiz_all_required_elements_present(app):
    """All required quiz elements (IDs and key classes) are present in rendered HTML."""
    html = _render_quiz_html(app)
    for eid in QUIZ_REQUIRED_IDS:
        assert f'id="{eid}"' in html or f"id='{eid}'" in html, f"Missing required id: {eid}"
    for cls in QUIZ_REQUIRED_CLASSES_OR_MARKERS:
        assert cls in html, f"Missing required class/marker: {cls}"


def test_quiz_crest_and_avatar_section_present(app):
    """Crest logo and avatar container are present."""
    html = _render_quiz_html(app)
    assert "quiz-card-crest" in html or "BeeSmartCrestLogo1" in html
    assert "mascot-3d-container" in html
    assert "mascotBee3D" in html
    assert "quiz-card-crest-avatar" in html


def test_quiz_no_duplicate_ids_in_quiz_markup(app):
    """No duplicate id attributes in the quiz container (avoids JS and a11y bugs)."""
    html = _render_quiz_html(app)
    # Extract all id="..." values (simple regex; SVG gradient ids can repeat in defs)
    ids = re.findall(r'\bid=["\']([^"\']+)["\']', html)
    # SVG internal refs (e.g. jarClip, glassGradient) may be unique per SVG; focus on main DOM
    # Remove known SVG/defs ids that are not in the main quiz DOM
    svg_internal = {"glassGradient", "honeyGradient", "shineGradient", "jarClip"}
    main_ids = [i for i in ids if i not in svg_internal]
    seen = set()
    duplicates = []
    for i in main_ids:
        if i in seen:
            duplicates.append(i)
        seen.add(i)
    assert not duplicates, f"Duplicate ids found: {duplicates}"


def test_quiz_structure_order(app):
    """Key sections appear in document order: header -> crest/avatar -> question -> answer -> actions -> exit."""
    html = _render_quiz_html(app)
    idx_container = html.find('id="quizContainer"')
    assert idx_container >= 0, "quizContainer not found"
    # Search only inside the quiz container so we don't match strings inside <script> or <style>
    fragment = html[idx_container:]
    idx_header = fragment.find('<div class="quiz-header">')
    idx_crest = fragment.find('<div class="quiz-card-crest-avatar">')
    idx_card = fragment.find('id="quizCard"')
    idx_question = fragment.find("question-area")
    idx_answer = fragment.find("answerAreaContainer")
    idx_actions = fragment.find("quizActionButtons")
    idx_exit = fragment.find("exitQuizButton")
    assert idx_header >= 0 and idx_crest >= 0 and idx_card >= 0
    assert idx_question >= 0 and idx_answer >= 0 and idx_actions >= 0 and idx_exit >= 0
    assert idx_header < idx_crest < idx_question < idx_answer < idx_actions < idx_exit


def test_quiz_full_page_scroll_css(app):
    """Layout uses full-page scroll (body or quiz-page scrolls), not trapped card-scroll."""
    quiz_path = REPO_ROOT / "templates" / "quiz.html"
    txt = quiz_path.read_text(encoding="utf-8")
    # card-scroll should be overflow visible (so content flows in page scroll)
    assert "overflow: visible" in txt or "overflow:visible" in txt.replace(" ", "")
    # body.route-quiz should be allowed to scroll (overflow-y: auto or overflow visible)
    assert "body.route-quiz" in txt
    assert "overflow-y: auto" in txt or "overflow: visible" in txt


def test_quiz_no_main_card_fixed_overlay(app):
    """Main quiz card and card-scroll are not position:fixed (would overlay and trap content)."""
    quiz_path = REPO_ROOT / "templates" / "quiz.html"
    txt = quiz_path.read_text(encoding="utf-8")
    # .quiz-card and .card-scroll should not be position: fixed
    card_scroll_block = re.search(r"\.card-scroll\s*\{[^}]*\}", txt, re.DOTALL)
    if card_scroll_block:
        block = re.sub(r"\s+", " ", card_scroll_block.group(0))
        assert "position: fixed" not in block and "position:fixed" not in block, \
            ".card-scroll must not be position:fixed"
    quiz_card_block = re.search(r"\.quiz-card\s*\{[^}]*\}", txt, re.DOTALL)
    if quiz_card_block:
        block = re.sub(r"\s+", " ", quiz_card_block.group(0))
        assert "position: fixed" not in block and "position:fixed" not in block, \
            ".quiz-card must not be position:fixed"


def test_quiz_script_tags_balanced(app):
    """Script tags in quiz template are balanced (no unclosed or stray tags)."""
    html = _render_quiz_html(app)
    open_script = html.count("<script")
    close_script = html.count("</script>")
    assert open_script == close_script, f"Script tags unbalanced: {open_script} open, {close_script} close"


def test_quiz_route_returns_200_or_redirect(client):
    """GET /quiz returns 200 or 302."""
    r = client.get("/quiz")
    assert r.status_code in (200, 302), f"Expected 200 or 302, got {r.status_code}"


def test_quiz_response_contains_key_elements_when_200(client):
    """When /quiz returns 200, response body contains quiz container and crest/avatar."""
    r = client.get("/quiz")
    if r.status_code != 200:
        pytest.skip("quiz route redirected (e.g. no wordbank)")
    body = r.get_data(as_text=True)
    assert "quizContainer" in body
    assert "quiz-crest-logo" in body or "quiz-logo" in body
    assert "quizCard" in body
