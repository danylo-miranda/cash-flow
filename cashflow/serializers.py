from rest_framework import serializers


class CashFlowSummaryEntrySerializer(serializers.Serializer):
    date = serializers.DateField()
    inflow = serializers.DecimalField(max_digits=14, decimal_places=2)
    outflow = serializers.DecimalField(max_digits=14, decimal_places=2)
    net = serializers.DecimalField(max_digits=14, decimal_places=2)
    balance = serializers.DecimalField(max_digits=14, decimal_places=2)

