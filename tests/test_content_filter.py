import json
import unittest

from AjaSpellBApp import app


class ContentFilterTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_upload_filters_profanity_in_definitions(self):
        payload = {
            "words": [
                {"word": "apple", "sentence": "Apples are tasty and healthy.", "hint": ""},
                {"word": "river", "sentence": "This river is full of shit.", "hint": ""},
                {"word": "chair", "sentence": "A chair is for sitting.", "hint": "Don't be a bitch."}
            ]
        }
        resp = self.app.post(
            "/api/upload",
            data=json.dumps(payload),
            content_type="application/json"
        )
        # Expect only the clean entries to be kept (apple and chair get filtered due to profanity in sentence/hint)
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
        data = json.loads(resp.data.decode("utf-8"))
        # Only 'apple' should remain
        self.assertTrue(data.get("ok"))
        self.assertEqual(data.get("count"), 1)

    def test_upload_rejects_profanity_words(self):
        payload = {
            "words": [
                {"word": "shit", "sentence": "", "hint": ""},
                {"word": "sun", "sentence": "The sun is bright.", "hint": ""}
            ]
        }
        resp = self.app.post(
            "/api/upload",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
        data = json.loads(resp.data.decode("utf-8"))
        # Only 'sun' should remain
        self.assertTrue(data.get("ok"))
        self.assertEqual(data.get("count"), 1)

    def test_upload_filters_violence_in_definitions(self):
        payload = {
            "words": [
                {"word": "hero", "sentence": "The hero will kill the dragon.", "hint": ""},
                {"word": "peace", "sentence": "Peace means no conflict.", "hint": ""}
            ]
        }
        resp = self.app.post(
            "/api/upload",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
        data = json.loads(resp.data.decode("utf-8"))
        # 'hero' should be filtered due to 'kill' in definition
        self.assertTrue(data.get("ok"))
        self.assertEqual(data.get("count"), 1)

    def test_upload_rejects_hate_speech_word(self):
        payload = {
            "words": [
                {"word": "racist", "sentence": "", "hint": ""},
                {"word": "flower", "sentence": "Flowers bloom in spring.", "hint": ""}
            ]
        }
        resp = self.app.post(
            "/api/upload",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
        data = json.loads(resp.data.decode("utf-8"))
        self.assertTrue(data.get("ok"))
        self.assertEqual(data.get("count"), 1)

    def test_upload_filters_hate_speech_in_hint(self):
        payload = {
            "words": [
                {"word": "chair", "sentence": "A chair is for sitting.", "hint": "Don't be racist."},
                {"word": "table", "sentence": "A table has four legs.", "hint": ""}
            ]
        }
        resp = self.app.post(
            "/api/upload",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
        data = json.loads(resp.data.decode("utf-8"))
        # 'chair' should be filtered due to hate speech in hint
        self.assertTrue(data.get("ok"))
        self.assertEqual(data.get("count"), 1)

    def test_upload_rejects_drug_word(self):
        payload = {
            "words": [
                {"word": "marijuana", "sentence": "", "hint": ""},
                {"word": "book", "sentence": "Books are for reading.", "hint": ""}
            ]
        }
        resp = self.app.post(
            "/api/upload",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
        data = json.loads(resp.data.decode("utf-8"))
        self.assertTrue(data.get("ok"))
        self.assertEqual(data.get("count"), 1)

    def test_upload_filters_disturbing_in_definition(self):
        payload = {
            "words": [
                {"word": "story", "sentence": "The story describes a lot of blood.", "hint": ""},
                {"word": "garden", "sentence": "A garden is full of flowers.", "hint": ""}
            ]
        }
        resp = self.app.post(
            "/api/upload",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
        data = json.loads(resp.data.decode("utf-8"))
        self.assertTrue(data.get("ok"))
        self.assertEqual(data.get("count"), 1)

    def test_manual_words_rejects_inappropriate_word(self):
        # Manual-words endpoint accepts an array of strings under 'words'
        payload = {
            "words": ["shit", "book"]
        }
        resp = self.app.post(
            "/api/upload-manual-words",
            data=json.dumps(payload),
            content_type="application/json"
        )
        # Expect only the clean word to remain
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
        data = json.loads(resp.data.decode("utf-8"))
        self.assertTrue(data.get("ok"))
        self.assertEqual(data.get("count"), 1)


class IsKidFriendlyDirectTests(unittest.TestCase):
    """Unit tests for is_kid_friendly() covering all expanded blocklist categories."""

    def setUp(self):
        from AjaSpellBApp import is_kid_friendly
        self.check = is_kid_friendly

    def _assert_blocked(self, word):
        safe, reason = self.check(word)
        self.assertFalse(safe, f"Expected '{word}' to be blocked but it passed. Reason given: {reason}")

    def _assert_allowed(self, word):
        safe, reason = self.check(word)
        self.assertTrue(safe, f"Expected '{word}' to be allowed but it was blocked. Reason: {reason}")

    # --- Profanity ---
    def test_blocks_fuck(self):
        self._assert_blocked("fuck")

    def test_blocks_shit(self):
        self._assert_blocked("shit")

    def test_blocks_bitch(self):
        self._assert_blocked("bitch")

    def test_blocks_ass(self):
        self._assert_blocked("ass")

    def test_blocks_dick(self):
        self._assert_blocked("dick")

    def test_blocks_cock(self):
        self._assert_blocked("cock")

    def test_blocks_cunt(self):
        self._assert_blocked("cunt")

    def test_blocks_slut(self):
        self._assert_blocked("slut")

    def test_blocks_whore(self):
        self._assert_blocked("whore")

    def test_blocks_bastard(self):
        self._assert_blocked("bastard")

    # --- Sexual content ---
    def test_blocks_porn(self):
        self._assert_blocked("porn")

    def test_blocks_sex(self):
        self._assert_blocked("sex")

    def test_blocks_penis(self):
        self._assert_blocked("penis")

    def test_blocks_vagina(self):
        self._assert_blocked("vagina")

    def test_blocks_rape(self):
        self._assert_blocked("rape")

    def test_blocks_pervert(self):
        self._assert_blocked("pervert")

    def test_blocks_fetish(self):
        self._assert_blocked("fetish")

    # --- Violence ---
    def test_blocks_kill(self):
        self._assert_blocked("kill")

    def test_blocks_murder(self):
        self._assert_blocked("murder")

    def test_blocks_suicide(self):
        self._assert_blocked("suicide")

    def test_blocks_stab(self):
        self._assert_blocked("stab")

    def test_blocks_gun(self):
        self._assert_blocked("gun")

    def test_blocks_bomb(self):
        self._assert_blocked("bomb")

    def test_blocks_torture(self):
        self._assert_blocked("torture")

    def test_blocks_genocide(self):
        self._assert_blocked("genocide")

    # --- Drugs / alcohol ---
    def test_blocks_cocaine(self):
        self._assert_blocked("cocaine")

    def test_blocks_weed(self):
        self._assert_blocked("weed")

    def test_blocks_meth(self):
        self._assert_blocked("meth")

    def test_blocks_heroin(self):
        self._assert_blocked("heroin")

    def test_blocks_drunk(self):
        self._assert_blocked("drunk")

    def test_blocks_overdose(self):
        self._assert_blocked("overdose")

    def test_blocks_addiction(self):
        self._assert_blocked("addiction")

    def test_blocks_alcohol(self):
        self._assert_blocked("alcohol")

    def test_blocks_vape(self):
        self._assert_blocked("vape")

    # --- Hate speech / slurs ---
    def test_blocks_nigger(self):
        self._assert_blocked("nigger")

    def test_blocks_faggot(self):
        self._assert_blocked("faggot")

    def test_blocks_retard(self):
        self._assert_blocked("retard")

    def test_blocks_nazi(self):
        self._assert_blocked("nazi")

    def test_blocks_racist(self):
        self._assert_blocked("racist")

    def test_blocks_chink(self):
        self._assert_blocked("chink")

    def test_blocks_bigot(self):
        self._assert_blocked("bigot")

    # --- Disturbing content ---
    def test_blocks_gore(self):
        self._assert_blocked("gore")

    def test_blocks_corpse(self):
        self._assert_blocked("corpse")

    def test_blocks_sadist(self):
        self._assert_blocked("sadist")

    # --- Safe words must still pass ---
    def test_allows_apple(self):
        self._assert_allowed("apple")

    def test_allows_elephant(self):
        self._assert_allowed("elephant")

    def test_allows_beautiful(self):
        self._assert_allowed("beautiful")

    def test_allows_rainbow(self):
        self._assert_allowed("rainbow")

    def test_allows_adventure(self):
        self._assert_allowed("adventure")

    def test_allows_science(self):
        self._assert_allowed("science")

    def test_allows_butterfly(self):
        self._assert_allowed("butterfly")

    def test_allows_ocean(self):
        self._assert_allowed("ocean")


if __name__ == "__main__":
    unittest.main()
