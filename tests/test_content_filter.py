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


if __name__ == "__main__":
    unittest.main()
