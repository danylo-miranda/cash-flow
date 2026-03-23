from django.test import TestCase


class RootUrlTests(TestCase):
    def test_root_returns_public_api_overview(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertEqual(response.json()["endpoints"]["api"], "/api/")
