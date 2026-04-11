from datetime import date

from django import forms

from .models import Agent, AgentPayment, Expenditure, FinancialAccount, Sale, Supplier, SupplierPayment


class SaleForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.TextInput(attrs={"data-flatpickr": "", "placeholder": "KK.OO.YYYY"}),
        input_formats=["%d.%m.%Y"],
        initial=date.today,
    )

    class Meta:
        model = Sale
        fields = [
            "date",
            "supplier",
            "product_type",
            "destination",
            "commentary",
            "quantity",
            "acquired_price",
            "acquired_currency",
            "customer_type",
            "agent",
            "customer_name",
            "customer_passport",
            "sold_price",
            "sold_currency",
        ]
        widgets = {
            "commentary": forms.Textarea(attrs={"rows": 2}),
            "quantity": forms.NumberInput(attrs={"min": 1}),
            "acquired_price": forms.NumberInput(attrs={"step": "0.01"}),
            "sold_price": forms.NumberInput(attrs={"step": "0.01"}),
            "customer_name": forms.TextInput(
                attrs={"x-bind:disabled": "customerType !== 'WALKIN'"}
            ),
            "customer_passport": forms.TextInput(
                attrs={"x-bind:disabled": "customerType !== 'WALKIN'"}
            ),
        }

    def clean(self):
        cleaned = super().clean()
        ct = cleaned.get("customer_type")
        if ct == Sale.AGENT and not cleaned.get("agent"):
            self.add_error("agent", "Agent mijoz uchun agent tanlanishi shart.")
        if ct == Sale.WALKIN and cleaned.get("agent"):
            self.add_error("agent", "Keluvchi mijoz uchun agent tanlanmasligi kerak.")
        if ct == Sale.WALKIN and not cleaned.get("customer_name"):
            self.add_error("customer_name", "Keluvchi mijoz uchun ism kiritilishi shart.")
        return cleaned


class AgentForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = ['name', 'phone', 'note', 'initial_balance_uzs', 'initial_balance_usd']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 2}),
            'initial_balance_uzs': forms.NumberInput(attrs={'step': '0.01'}),
            'initial_balance_usd': forms.NumberInput(attrs={'step': '0.01'}),
        }


class AgentPaymentForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.TextInput(attrs={"data-flatpickr": "", "placeholder": "KK.OO.YYYY"}),
        input_formats=["%d.%m.%Y"],
        initial=date.today,
    )

    class Meta:
        model = AgentPayment
        fields = ["amount", "currency", "financial_account", "date", "note"]
        widgets = {
            "amount": forms.NumberInput(attrs={"step": "0.01", "min": "0.01"}),
            "note": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["financial_account"].queryset = FinancialAccount.objects.filter(is_active=True)

    def clean(self):
        cleaned = super().clean()
        currency = cleaned.get("currency")
        account = cleaned.get("financial_account")
        if currency and account and account.currency != currency:
            self.add_error(
                "financial_account",
                "Hisob valyutasi to'lov valyutasiga mos kelishi kerak.",
            )
        return cleaned


class ExpenditureForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.TextInput(attrs={"data-flatpickr": "", "placeholder": "KK.OO.YYYY"}),
        input_formats=["%d.%m.%Y"],
        initial=date.today,
    )

    class Meta:
        model = Expenditure
        fields = ["amount", "currency", "financial_account", "date", "description"]
        widgets = {
            "amount": forms.NumberInput(attrs={"step": "0.01", "min": "0.01"}),
            "description": forms.TextInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["financial_account"].queryset = FinancialAccount.objects.filter(is_active=True)

    def clean(self):
        cleaned = super().clean()
        currency = cleaned.get("currency")
        account = cleaned.get("financial_account")
        if currency and account and account.currency != currency:
            self.add_error(
                "financial_account",
                "Hisob valyutasi xarajat valyutasiga mos kelishi kerak.",
            )
        return cleaned


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'phone', 'note', 'initial_balance_uzs', 'initial_balance_usd']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 2}),
            'initial_balance_uzs': forms.NumberInput(attrs={'step': '0.01'}),
            'initial_balance_usd': forms.NumberInput(attrs={'step': '0.01'}),
        }


class SupplierPaymentForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.TextInput(attrs={"data-flatpickr": "", "placeholder": "KK.OO.YYYY"}),
        input_formats=["%d.%m.%Y"],
        initial=date.today,
    )

    class Meta:
        model = SupplierPayment
        fields = ["amount", "currency", "financial_account", "date", "note"]
        widgets = {
            "amount": forms.NumberInput(attrs={"step": "0.01", "min": "0.01"}),
            "note": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["financial_account"].queryset = FinancialAccount.objects.filter(is_active=True)

    def clean(self):
        cleaned = super().clean()
        currency = cleaned.get("currency")
        account = cleaned.get("financial_account")
        if currency and account and account.currency != currency:
            self.add_error(
                "financial_account",
                "Hisob valyutasi to'lov valyutasiga mos kelishi kerak.",
            )
        return cleaned


class FinancialAccountForm(forms.ModelForm):
    class Meta:
        model = FinancialAccount
        fields = ["name", "account_type", "currency"]
