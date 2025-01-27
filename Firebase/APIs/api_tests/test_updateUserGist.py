import unittest
import requests

class TestUpdateUserGist(unittest.TestCase):
    BASE_URL = "http://localhost:5000/api/gists/add"  # Update with your actual base URL
    USER_ID = "gister12346"  # Use the same dummy user ID

    def test_update_gist(self):
        # Dummy gist data to update
        gist_data = {
            "title": "New Gist Title",
            "imageUrl": "https://example.com/gist-image.jpg",
            "isFinished": False,
            "playbackDuration": 120,
            "playbackTime": 30,
            "segments": [
                {
                    "segment_duration": 60,
                    "segment_index": 0,
                    "segment_title": "First Segment"
                }
            ]
        }

        response = requests.post(f"{self.BASE_URL}/add/{self.USER_ID}", json=gist_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Gist added successfully")

if __name__ == "__main__":
    unittest.main()
