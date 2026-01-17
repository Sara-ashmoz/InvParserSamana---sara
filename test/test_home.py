import unittest
from fastapi.testclient import TestClient
from app import app

class TestHome(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_home(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"msg": "Hello World"})
