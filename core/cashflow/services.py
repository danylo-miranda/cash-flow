from datetime import timedelta
from decimal import Decimal

from django.db.models import Q, Sum

from ledger.models import Transaction, TransactionType
from organizations.models import Organization


def generate_cashflow_summary(organization: Organization, start_date, end_date):
    """
    Consolida entradas e saídas por dia dentro do intervalo fornecido.
    """

    if start_date > end_date:
        raise ValueError("A data inicial deve ser anterior à final.")

    queryset = Transaction.objects.filter(
        organization=organization,
        competence_date__range=(start_date, end_date),
    )

    aggregates = (
        queryset.values("competence_date")
        .annotate(
            inflow=Sum(
                "amount",
                filter=Q(kind__in=[TransactionType.RECEITA]),
            ),
            outflow=Sum(
                "amount",
                filter=Q(kind__in=[TransactionType.DESPESA, TransactionType.CUSTO, TransactionType.IMPOSTO, TransactionType.INVESTIMENTO]),
            ),
        )
        .order_by("competence_date")
    )

    data_by_date = {
        item["competence_date"]: {
            "inflow": item["inflow"] or Decimal("0.00"),
            "outflow": item["outflow"] or Decimal("0.00"),
        }
        for item in aggregates
    }

    results = []
    cursor = start_date
    balance = Decimal("0.00")

    while cursor <= end_date:
        values = data_by_date.get(
            cursor,
            {
                "inflow": Decimal("0.00"),
                "outflow": Decimal("0.00"),
            },
        )
        net = values["inflow"] - values["outflow"]
        balance += net
        results.append(
            {
                "date": cursor,
                "inflow": values["inflow"],
                "outflow": values["outflow"],
                "net": net,
                "balance": balance,
            }
        )
        cursor += timedelta(days=1)

    return results

