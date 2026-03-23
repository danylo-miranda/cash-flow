from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Membership, Organization


class OrganizationApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="owner", password="pass123")

    def test_create_organization_assigns_membership(self):
        self.client.force_authenticate(self.user)
        payload = {"name": "Finance Corp", "currency": "BRL", "timezone": "America/Sao_Paulo"}

        response = self.client.post(reverse("organization-list"), data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        organization = Organization.objects.get(pk=response.data["id"])
        membership_exists = Membership.objects.filter(user=self.user, organization=organization).exists()
        self.assertTrue(membership_exists)

    def test_list_only_user_organizations(self):
        self.client.force_authenticate(self.user)
        org_1 = Organization.objects.create(name="Org 1")
        org_2 = Organization.objects.create(name="Org 2")
        Membership.objects.create(user=self.user, organization=org_1)

        response = self.client.get(reverse("organization-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], org_1.id)


class MembershipApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="member", password="pass123")
        self.other_user = get_user_model().objects.create_user(username="other_member", password="pass123")
        self.organization = Organization.objects.create(name="Members Org")
        Membership.objects.create(user=self.user, organization=self.organization, is_active=False)
        Membership.objects.create(user=self.other_user, organization=self.organization, is_active=True)

    def test_inactive_requester_cannot_list_memberships(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse("membership-list"),
            data={"organization": self.organization.id},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
