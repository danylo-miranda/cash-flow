from django.test import TestCase


class RootUrlTests(TestCase):
    def test_root_returns_login_page(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login")

    def test_app_route_returns_dashboard_page(self):
        response = self.client.get("/app/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Painel Operacional")
