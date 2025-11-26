from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from organizations.models import Membership, Organization

from .models import Account, AccountType, Transaction, TransactionType


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

    def test_list_transactions_requires_membership(self):
        other_user = get_user_model().objects.create_user(username="other", password="pass")
        self.client.force_authenticate(other_user)
        response = self.client.get(reverse("transaction-list"), data={"organization": self.organization.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
