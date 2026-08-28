import unittest

from backend.api.routers.chat import clean_reply, response_language
from backend.api.schemas.schemas import Language


class ChatHelpersTest(unittest.TestCase):
    def test_response_language_uses_requested_language(self):
        self.assertEqual(response_language(Language.RU), "Russian")
        self.assertEqual(response_language(Language.EN), "English")

    def test_clean_reply_removes_markdown(self):
        self.assertEqual(clean_reply("## Advice\n\n- Keep it simple."), "Advice\nKeep it simple.")


if __name__ == "__main__":
    unittest.main()
