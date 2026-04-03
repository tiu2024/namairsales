from django.db import transaction

from .models import AgentPayment, BalanceLog, FinancialAccount, SupplierPayment


@transaction.atomic
def record_supplier_payment(*, supplier, amount, currency, financial_account, date, note, user):
    account = FinancialAccount.objects.select_for_update().get(pk=financial_account.pk)
    payment = SupplierPayment.objects.create(
        supplier=supplier,
        amount=amount,
        currency=currency,
        financial_account=account,
        date=date,
        note=note,
        created_by=user,
    )
    account.balance -= amount
    account.save(update_fields=["balance"])
    BalanceLog.objects.create(
        account=account,
        change=-amount,
        reason=BalanceLog.SUPPLIER_PAYMENT,
        actor=user,
    )
    return payment


@transaction.atomic
def record_agent_payment(*, agent, amount, currency, financial_account, date, note, user):
    account = FinancialAccount.objects.select_for_update().get(pk=financial_account.pk)
    payment = AgentPayment.objects.create(
        agent=agent,
        amount=amount,
        currency=currency,
        financial_account=account,
        date=date,
        note=note,
        created_by=user,
    )
    account.balance += amount
    account.save(update_fields=["balance"])
    BalanceLog.objects.create(
        account=account,
        change=amount,
        reason=BalanceLog.AGENT_PAYMENT,
        actor=user,
    )
    return payment
