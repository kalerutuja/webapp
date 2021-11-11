from app import create_app
import unittest
import json


class SignupTest(unittest.TestCase):
    app = create_app()

    def test_index(self):
        self.app = SignupTest.app.test_client()
        response = self.app.get("/v1/pic")
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    def test_index_content(self):
        self.app = SignupTest.app.test_client()
        response = self.app.get("/v1/pic")
        self.assertEqual(response.content_type, "application/json")


if __name__ == "__main__":
    unittest.main()
