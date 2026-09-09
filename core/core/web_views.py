from django.conf import settings
from django.shortcuts import render
from ledger.models import Account, Category, Transaction
from ledger.serializers import (
    AccountSerializer,
    CategorySerializer,
    TransactionSerializer,
)


def login_page(request):
    context = {"google_client_id": settings.GOOGLE_CLIENT_ID}
    return render(request, "web/login.html", context)


def app_page(request):
    # Obtém o ID da organização via parâmetro ou usa 1 como padrão
    organization_id = request.GET.get("organization", 1)

    # Consulta e serializa os dados no próprio servidor
    categories = Category.objects.filter(organization_id=organization_id)
    accounts = Account.objects.filter(organization_id=organization_id)
    transactions = Transaction.objects.filter(organization_id=organization_id)

    context = {
        "organization_id": organization_id,
        "categories_payload": CategorySerializer(categories, many=True).data,
        "accounts_payload": AccountSerializer(accounts, many=True).data,
        "transactions_payload": TransactionSerializer(transactions, many=True).data,
    }

    return render(request, "web/app.html", context)
