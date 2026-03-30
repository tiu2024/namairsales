from django.contrib import admin

from .models import (
    Agent,
    AgentPayment,
    BalanceLog,
    Expenditure,
    FinancialAccount,
    Sale,
    Supplier,
    SupplierPayment,
)

admin.site.register(FinancialAccount)
admin.site.register(Supplier)
admin.site.register(Agent)
admin.site.register(Expenditure)
admin.site.register(BalanceLog)


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_select_related = ("supplier", "agent", "salesman")


@admin.register(SupplierPayment)
class SupplierPaymentAdmin(admin.ModelAdmin):
    list_select_related = ("supplier",)


@admin.register(AgentPayment)
class AgentPaymentAdmin(admin.ModelAdmin):
    list_select_related = ("agent",)
