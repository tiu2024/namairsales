from django.db import transaction

from .models import AgentPayment, BalanceLog, Expenditure, FinancialAccount, Sale, SupplierPayment


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
def link_sale_to_account(*, sale, financial_account, user):
    from django.utils import timezone
    if financial_account.currency != sale.sold_currency:
        raise ValueError("Hisob valyutasi sotuv valyutasiga mos emas.")
    # No-op if already linked to the same account
    if sale.financial_account_id == financial_account.pk:
        return
    # Reverse previous link if switching accounts
    if sale.financial_account_id:
        old_account = FinancialAccount.objects.select_for_update().get(pk=sale.financial_account_id)
        old_account.balance -= sale.sold_price
        old_account.save(update_fields=["balance"])
        BalanceLog.objects.create(
            account=old_account,
            change=-sale.sold_price,
            reason=BalanceLog.REVERSAL,
            actor=user,
        )
    account = FinancialAccount.objects.select_for_update().get(pk=financial_account.pk)
    sale.financial_account = account
    sale.linked_by = user
    sale.linked_at = timezone.now()
    sale.save(update_fields=["financial_account", "linked_by", "linked_at"])
    account.balance += sale.sold_price
    account.save(update_fields=["balance"])
    BalanceLog.objects.create(
        account=account,
        change=sale.sold_price,
        reason=BalanceLog.SALE,
        actor=user,
    )


@transaction.atomic
def unlink_sale_from_account(*, sale, user):
    if not sale.financial_account_id:
        return
    account = FinancialAccount.objects.select_for_update().get(pk=sale.financial_account_id)
    account.balance -= sale.sold_price
    account.save(update_fields=["balance"])
    BalanceLog.objects.create(
        account=account,
        change=-sale.sold_price,
        reason=BalanceLog.REVERSAL,
        actor=user,
    )
    sale.financial_account = None
    sale.linked_by = None
    sale.linked_at = None
    sale.save(update_fields=["financial_account", "linked_by", "linked_at"])


@transaction.atomic
def record_expenditure(*, amount, currency, financial_account, date, description, user):
    account = FinancialAccount.objects.select_for_update().get(pk=financial_account.pk)
    expenditure = Expenditure.objects.create(
        amount=amount,
        currency=currency,
        financial_account=account,
        date=date,
        description=description,
        registered_by=user,
    )
    account.balance -= amount
    account.save(update_fields=["balance"])
    BalanceLog.objects.create(
        account=account,
        change=-amount,
        reason=BalanceLog.EXPENDITURE,
        actor=user,
    )
    return expenditure


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
