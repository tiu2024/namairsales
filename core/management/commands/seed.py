from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core.models import Agent, FinancialAccount, Supplier

User = get_user_model()

SALESMEN = [
    {"phone_number": "901111111", "first_name": "Jasur", "last_name": "Toshmatov", "password": "test1234"},
    {"phone_number": "902222222", "first_name": "Dilnoza", "last_name": "Yusupova", "password": "test1234"},
    {"phone_number": "903333333", "first_name": "Bobur", "last_name": "Karimov", "password": "test1234"},
]

SUPPLIERS = [
    {
        "name": "Uzbekistan Airways",
        "phone": "711234567",
        "initial_balance_uzs": 12_500_000,
        "initial_balance_usd": 0,
    },
    {
        "name": "FlyDubai",
        "phone": "712345678",
        "initial_balance_uzs": 0,
        "initial_balance_usd": 3_200,
    },
    {
        "name": "Umra Travel",
        "phone": "713456789",
        "initial_balance_uzs": 45_000_000,
        "initial_balance_usd": 1_500,
    },
]

AGENTS = [
    {
        "name": "Sarvar Ergashev",
        "phone": "904444444",
        "initial_balance_uzs": 8_750_000,
        "initial_balance_usd": 0,
    },
    {
        "name": "Malika Hasanova",
        "phone": "905555555",
        "initial_balance_uzs": 0,
        "initial_balance_usd": 650,
    },
    {
        "name": "Otabek Normatov",
        "phone": "906666666",
        "initial_balance_uzs": 3_200_000,
        "initial_balance_usd": 200,
    },
]

ACCOUNTS = [
    {"name": "Asosiy kassa", "account_type": FinancialAccount.CASH, "currency": "UZS", "balance": 25_000_000},
    {"name": "Dollar kassa", "account_type": FinancialAccount.CASH, "currency": "USD", "balance": 5_000},
    {"name": "Korporativ karta", "account_type": FinancialAccount.PLASTIC, "currency": "UZS", "balance": 48_300_000},
    {"name": "USD plastik", "account_type": FinancialAccount.PLASTIC, "currency": "USD", "balance": 12_400},
    {"name": "Bank hisobi", "account_type": FinancialAccount.BANK, "currency": "UZS", "balance": 120_000_000},
]


class Command(BaseCommand):
    help = "Seed test data: 3 salesmen, 3 suppliers, 3 agents, 5 financial accounts"

    def handle(self, *args, **options):
        self._seed_salesmen()
        self._seed_suppliers()
        self._seed_agents()
        self._seed_accounts()
        self.stdout.write(self.style.SUCCESS("Seed completed."))

    def _seed_salesmen(self):
        for data in SALESMEN:
            phone = data["phone_number"]
            if User.objects.filter(phone_number=phone).exists():
                self.stdout.write(f"  skip salesman {phone} (already exists)")
                continue
            User.objects.create_user(
                phone_number=phone,
                password=data["password"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                role="SALESMAN",
            )
            self.stdout.write(f"  created salesman {data['first_name']} {data['last_name']} ({phone})")

    def _seed_suppliers(self):
        for data in SUPPLIERS:
            _, created = Supplier.objects.get_or_create(
                name=data["name"],
                defaults={
                    "phone": data["phone"],
                    "initial_balance_uzs": data["initial_balance_uzs"],
                    "initial_balance_usd": data["initial_balance_usd"],
                },
            )
            status = "created" if created else "skip (already exists)"
            self.stdout.write(f"  {status} supplier {data['name']}")

    def _seed_agents(self):
        for data in AGENTS:
            _, created = Agent.objects.get_or_create(
                name=data["name"],
                defaults={
                    "phone": data["phone"],
                    "initial_balance_uzs": data["initial_balance_uzs"],
                    "initial_balance_usd": data["initial_balance_usd"],
                },
            )
            status = "created" if created else "skip (already exists)"
            self.stdout.write(f"  {status} agent {data['name']}")

    def _seed_accounts(self):
        for data in ACCOUNTS:
            _, created = FinancialAccount.objects.get_or_create(
                name=data["name"],
                defaults={
                    "account_type": data["account_type"],
                    "currency": data["currency"],
                    "balance": data["balance"],
                },
            )
            status = "created" if created else "skip (already exists)"
            self.stdout.write(f"  {status} account {data['name']}")
