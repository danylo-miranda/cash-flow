from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from organizations.models import Membership, Organization

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


class UserApiTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.request_user = User.objects.create_user(username="requester", password="strong-pass")
        self.teammate = User.objects.create_user(username="teammate", password="strong-pass")
        self.outsider = User.objects.create_user(username="outsider", password="strong-pass")

        organization = Organization.objects.create(name="Shared Org")
        Membership.objects.create(user=self.request_user, organization=organization, is_active=True)
        Membership.objects.create(user=self.teammate, organization=organization, is_active=True)

    def test_list_users_only_returns_same_organization_members(self):
        self.client.force_authenticate(self.request_user)
        response = self.client.get(reverse("user-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = {item["username"] for item in response.data}
        self.assertIn("requester", usernames)
        self.assertIn("teammate", usernames)
        self.assertNotIn("outsider", usernames)
