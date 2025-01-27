import unittest
import requests

class TestSignIn(unittest.TestCase):
    BASE_URL = "http://localhost:5000/api/auth/signin"  # Update with your actual base URL

    def test_sign_in(self):
        # Replace with a valid token for the dummy user
        dummy_user_data = {
            "id_token": "VALID_ID_TOKEN"  # Use a valid ID token here
        }

        response = requests.post(self.BASE_URL, json=dummy_user_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("email", response.json())
        self.assertIn("user_id", response.json())

if __name__ == "__main__":
    unittest.main()
