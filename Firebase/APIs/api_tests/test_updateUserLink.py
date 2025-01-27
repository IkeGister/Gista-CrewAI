import unittest
import requests

class TestUpdateUserLink(unittest.TestCase):
    BASE_URL = "http://localhost:5000/api/links/store"  # Update with your actual base URL
    USER_ID = "gister12346"  # Use the same dummy user ID

    def test_update_link(self):
        # Dummy link data to update
        link_data = {
            "user_id": self.USER_ID,
            "link": "https://example.com/new-link"
        }

        response = requests.post(self.BASE_URL, json=link_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Link stored successfully")

if __name__ == "__main__":
    unittest.main()
