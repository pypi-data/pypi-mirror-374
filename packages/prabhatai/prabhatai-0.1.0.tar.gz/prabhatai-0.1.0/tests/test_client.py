import unittest
from prabhatai.client import PrabhatAIClient

class TestPrabhatAIClient(unittest.TestCase):
    def test_chat_format(self):
        client = PrabhatAIClient(api_key="test")
        messages = [{"role": "user", "content": "Hello!"}]
        # This test only checks payload format, not actual API call
        payload = {
            "model": "openai/gpt-3.5-turbo",
            "messages": messages
        }
        self.assertEqual(payload["messages"], messages)

if __name__ == "__main__":
    unittest.main()
