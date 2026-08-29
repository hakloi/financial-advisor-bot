import unittest # Standard framework for writing and running automated unit tests

from backend.api.routers.chat import clean_reply, response_language # Functions to test
from backend.api.schemas.schemas import Language # Import Enum class for supported languages to test 


# Class for testing the chat helper functions
class ChatHelpersTest(unittest.TestCase):
    # Test that the response_language function returns the correct language name based on the requested language
    def test_response_language_uses_requested_language(self):
        self.assertEqual(response_language(Language.RU), "Russian")
        self.assertEqual(response_language(Language.EN), "English")

    # Test that the clean_reply function removes markdown formatting from the response
    def test_clean_reply_removes_markdown(self):
        self.assertEqual(clean_reply("## Advice\n\n- Keep it simple."), "Advice\nKeep it simple.")


if __name__ == "__main__":
    unittest.main()
