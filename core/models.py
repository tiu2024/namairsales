from datetime import date

from django.conf import settings
from django.db import models

UZS = "UZS"
USD = "USD"
CURRENCY_CHOICES = [(UZS, "So'm"), (USD, "Dollar")]


class FinancialAccount(models.Model):
    CASH = "CASH"
    PLASTIC = "PLASTIC"
    BANK = "BANK"
    TYPE_CHOICES = [(CASH, "Naqd"), (PLASTIC, "Plastik"), (BANK, "Bank")]

    name = models.CharField(max_length=100, unique=True)
    account_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    balance = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.name} ({self.currency})"


class Supplier(models.Model):
    name = models.CharField(max_length=100, unique=True)
    phone = models.CharField(max_length=20, blank=True)
    note = models.TextField(blank=True)
    initial_balance_uzs = models.DecimalField(
        max_digits=16, decimal_places=2, default=0
    )
    initial_balance_usd = models.DecimalField(
        max_digits=16, decimal_places=2, default=0
    )

    def __str__(self):
        return self.name

    def balance_uzs(self):
        from django.db.models import Sum

        sales = (
            self.sale_set.filter(acquired_currency=UZS).aggregate(
                total=Sum("acquired_price")
            )["total"]
            or 0
        )
        # total_cost = acquired_price * quantity — need to account for quantity
        sales = self.sale_set.filter(acquired_currency=UZS)
        sales_total = sum(s.total_cost for s in sales)
        payments = (
            self.supplierpayment_set.filter(currency=UZS).aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )
        return self.initial_balance_uzs + sales_total - payments

    def balance_usd(self):
        from django.db.models import Sum

        sales = self.sale_set.filter(acquired_currency=USD)
        sales_total = sum(s.total_cost for s in sales)
        payments = (
            self.supplierpayment_set.filter(currency=USD).aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )
        return self.initial_balance_usd + sales_total - payments


class Agent(models.Model):
    name = models.CharField(max_length=100, unique=True)
    phone = models.CharField(max_length=20, blank=True)
    note = models.TextField(blank=True)
    initial_balance_uzs = models.DecimalField(
        max_digits=16, decimal_places=2, default=0
    )
    initial_balance_usd = models.DecimalField(
        max_digits=16, decimal_places=2, default=0
    )

    def __str__(self):
        return f"{self.name}"

    def balance_uzs(self):
        from django.db.models import Sum

        sales = (
            self.sale_set.filter(sold_currency=UZS).aggregate(total=Sum("sold_price"))[
                "total"
            ]
            or 0
        )
        payments = (
            self.agentpayment_set.filter(currency=UZS).aggregate(total=Sum("amount"))[
                "total"
            ]
            or 0
        )
        return self.initial_balance_uzs + sales - payments

    def balance_usd(self):
        from django.db.models import Sum

        sales = (
            self.sale_set.filter(sold_currency=USD).aggregate(total=Sum("sold_price"))[
                "total"
            ]
            or 0
        )
        payments = (
            self.agentpayment_set.filter(currency=USD).aggregate(total=Sum("amount"))[
                "total"
            ]
            or 0
        )
        return self.initial_balance_usd + sales - payments


class Sale(models.Model):
    TICKET = "TICKET"
    UMRA = "UMRA"
    TOUR = "TOUR"
    PRODUCT_CHOICES = [(TICKET, "Aviabilet"), (UMRA, "Umra"), (TOUR, "Turi")]

    AGENT = "AGENT"
    WALKIN = "WALKIN"
    CUSTOMER_CHOICES = [(AGENT, "Agent"), (WALKIN, "Keluvchi")]

    salesman = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="sales"
    )
    date = models.DateField(default=date.today)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    product_type = models.CharField(max_length=10, choices=PRODUCT_CHOICES)
    destination = models.CharField(max_length=200)
    commentary = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=1)
    acquired_price = models.DecimalField(max_digits=16, decimal_places=2)
    acquired_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    customer_type = models.CharField(max_length=10, choices=CUSTOMER_CHOICES)
    agent = models.ForeignKey(Agent, on_delete=models.PROTECT, null=True, blank=True)
    customer_name = models.CharField(max_length=200, blank=True)
    customer_passport = models.CharField(max_length=50, blank=True)
    sold_price = models.DecimalField(max_digits=16, decimal_places=2)
    sold_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    financial_account = models.ForeignKey(
        FinancialAccount, on_delete=models.PROTECT, null=True, blank=True
    )
    linked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="linked_sales",
    )
    linked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_cost(self):
        return self.acquired_price * self.quantity

    @property
    def profit(self):
        if self.acquired_currency == self.sold_currency:
            return (self.sold_price - self.acquired_price) * self.quantity
        return None

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.customer_type == self.AGENT and not self.agent:
            raise ValidationError("Agent mijoz uchun agent tanlanishi shart.")
        if self.customer_type == self.WALKIN and self.agent:
            raise ValidationError("Keluvchi mijoz uchun agent tanlanmasligi kerak.")
        if self.customer_type == self.WALKIN and not self.customer_name:
            raise ValidationError("Keluvchi mijoz uchun ism kiritilishi shart.")

    def __str__(self):
        return f"{self.date} — {self.supplier} — {self.destination}"


class SupplierPayment(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    financial_account = models.ForeignKey(FinancialAccount, on_delete=models.PROTECT)
    date = models.DateField()
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date} — {self.supplier} — {self.amount} {self.currency}"


class AgentPayment(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    financial_account = models.ForeignKey(FinancialAccount, on_delete=models.PROTECT)
    date = models.DateField()
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date} — {self.agent} — {self.amount} {self.currency}"


class Expenditure(models.Model):
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    financial_account = models.ForeignKey(FinancialAccount, on_delete=models.PROTECT)
    description = models.CharField(max_length=300)
    date = models.DateField()
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date} — {self.description} — {self.amount} {self.currency}"


class BalanceLog(models.Model):
    SALE = "sale"
    EXPENDITURE = "expenditure"
    SUPPLIER_PAYMENT = "supplier_payment"
    AGENT_PAYMENT = "agent_payment"
    REVERSAL = "reversal"
    REASON_CHOICES = [
        (SALE, "Sotuv"),
        (EXPENDITURE, "Xarajat"),
        (SUPPLIER_PAYMENT, "Yetkazib beruvchi to'lovi"),
        (AGENT_PAYMENT, "Agent to'lovi"),
        (REVERSAL, "Teskari qaytarish"),
    ]

    account = models.ForeignKey(FinancialAccount, on_delete=models.PROTECT)
    change = models.DecimalField(max_digits=16, decimal_places=2)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.created_at:%d.%m.%Y} — {self.reason} — {self.change}"
