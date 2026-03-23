from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from organizations.models import Membership, Organization

from .models import Account, AccountType, Category, Transaction, TransactionType


class TransactionApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="finance", password="pass123")
        self.organization = Organization.objects.create(name="Org Finance")
        Membership.objects.create(user=self.user, organization=self.organization)
        self.account = Account.objects.create(
            organization=self.organization,
            name="Conta Receitas",
            type=AccountType.RECEITA,
        )
        self.category = Category.objects.create(
            organization=self.organization,
            name="Categoria Local",
        )

    def test_create_transaction(self):
        self.client.force_authenticate(self.user)
        payload = {
            "organization": self.organization.id,
            "account": self.account.id,
            "kind": TransactionType.RECEITA,
            "status": "CONFIRMED",
            "amount": "1500.00",
            "competence_date": date.today().isoformat(),
            "description": "Pagamento cliente",
        }

        response = self.client.post(reverse("transaction-list"), data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(Transaction.objects.first().created_by, self.user)

    def test_create_transaction_requires_active_membership(self):
        outsider = get_user_model().objects.create_user(username="outsider", password="pass123")
        self.client.force_authenticate(outsider)
        payload = {
            "organization": self.organization.id,
            "account": self.account.id,
            "kind": TransactionType.RECEITA,
            "amount": "500.00",
            "competence_date": date.today().isoformat(),
        }

        response = self.client.post(reverse("transaction-list"), data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("organization", response.data)

    def test_create_transaction_rejects_cross_organization_account(self):
        self.client.force_authenticate(self.user)
        second_org = Organization.objects.create(name="Org Secundaria")
        Membership.objects.create(user=self.user, organization=second_org)
        foreign_account = Account.objects.create(
            organization=second_org,
            name="Conta Externa",
            type=AccountType.RECEITA,
        )
        payload = {
            "organization": self.organization.id,
            "account": foreign_account.id,
            "kind": TransactionType.RECEITA,
            "amount": "700.00",
            "competence_date": date.today().isoformat(),
        }

        response = self.client.post(reverse("transaction-list"), data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("account", response.data)

    def test_create_transaction_rejects_cross_organization_category(self):
        self.client.force_authenticate(self.user)
        second_org = Organization.objects.create(name="Org Categorias")
        Membership.objects.create(user=self.user, organization=second_org)
        foreign_category = Category.objects.create(
            organization=second_org,
            name="Categoria Externa",
        )
        payload = {
            "organization": self.organization.id,
            "account": self.account.id,
            "category": foreign_category.id,
            "kind": TransactionType.RECEITA,
            "amount": "700.00",
            "competence_date": date.today().isoformat(),
        }

        response = self.client.post(reverse("transaction-list"), data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("category", response.data)

    def test_list_transactions_requires_membership(self):
        other_user = get_user_model().objects.create_user(username="other", password="pass")
        self.client.force_authenticate(other_user)
        response = self.client.get(reverse("transaction-list"), data={"organization": self.organization.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
