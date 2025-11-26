from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import UserRole


class UserModelTests(TestCase):
    def test_default_role_is_analyst(self):
        User = get_user_model()
        user = User.objects.create_user(username="tester", password="strong-pass")
        self.assertEqual(user.role, UserRole.ANALISTA)

    def test_custom_role_persists(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="admin",
            password="strong-pass",
            role=UserRole.ADMIN,
        )
        self.assertEqual(user.role, UserRole.ADMIN)
