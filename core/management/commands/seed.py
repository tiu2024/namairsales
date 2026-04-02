from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core.models import Agent, FinancialAccount, Sale, Supplier

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
        self._seed_sales()
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

    def _seed_sales(self):
        from datetime import date
        deleted, _ = Sale.objects.all().delete()
        if deleted:
            self.stdout.write(f"  deleted {deleted} existing sales")

        jasur   = User.objects.get(phone_number="901111111")
        dilnoza = User.objects.get(phone_number="902222222")
        bobur   = User.objects.get(phone_number="903333333")

        uzair = Supplier.objects.get(name="Uzbekistan Airways")
        fly   = Supplier.objects.get(name="FlyDubai")
        umra  = Supplier.objects.get(name="Umra Travel")

        sarvar = Agent.objects.get(name="Sarvar Ergashev")
        malika = Agent.objects.get(name="Malika Hasanova")
        otabek = Agent.objects.get(name="Otabek Normatov")

        def w(salesman, d, sup, dest, qty, ap, ac, sp, sc, name, pt="TICKET", note=""):
            r = dict(salesman=salesman, date=d, supplier=sup, product_type=pt,
                     destination=dest, quantity=qty, acquired_price=ap,
                     acquired_currency=ac, sold_price=sp, sold_currency=sc,
                     customer_type="WALKIN", customer_name=name)
            if note:
                r["commentary"] = note
            return r

        def a(salesman, d, sup, dest, qty, ap, ac, sp, sc, agent, pt="TICKET", note=""):
            r = dict(salesman=salesman, date=d, supplier=sup, product_type=pt,
                     destination=dest, quantity=qty, acquired_price=ap,
                     acquired_currency=ac, sold_price=sp, sold_currency=sc,
                     customer_type="AGENT", agent=agent)
            if note:
                r["commentary"] = note
            return r

        SALES = [
            # ── Jasur (25 sales) ───────────────────────────────────────────
            w(jasur, date(2026, 1,  5), fly,   "Toshkent–Dubai",     2, 1_800_000, "UZS", 2_100_000, "UZS", "Alisher Qodirov"),
            w(jasur, date(2026, 1, 12), uzair, "Toshkent–Moskva",    1, 1_250_000, "UZS", 1_480_000, "UZS", "Nodira Azimova"),
            w(jasur, date(2026, 1, 20), umra,  "Makka–Madina",       2, 9_000_000, "UZS", 10_200_000,"UZS", "Hamid va Zarnigor", pt="UMRA"),
            a(jasur, date(2026, 1, 25), fly,   "Toshkent–Istanbul",  1,       180, "USD",       215,  "USD", sarvar),
            w(jasur, date(2026, 2,  3), uzair, "Toshkent–Antaliya",  3, 2_100_000, "UZS", 2_450_000, "UZS", "Jahongir Ergashev"),
            a(jasur, date(2026, 2,  8), fly,   "Toshkent–Dubai",     2,       195, "USD",       230,  "USD", malika),
            w(jasur, date(2026, 2, 14), umra,  "Makka–Madina",       1,11_000_000, "UZS",12_500_000, "UZS", "Murod Xolmatov", pt="UMRA"),
            a(jasur, date(2026, 2, 19), uzair, "Toshkent–Frankfurt", 1,       310, "USD",       355,  "USD", otabek),
            w(jasur, date(2026, 2, 25), fly,   "Toshkent–Dubai",     1, 1_750_000, "UZS", 2_050_000, "UZS", "Sabina Yusupova"),
            a(jasur, date(2026, 3,  1), umra,  "Makka–Madina",       4, 8_800_000, "UZS", 9_500_000, "UZS", sarvar, pt="UMRA", note="Guruh, 4 kishi"),
            w(jasur, date(2026, 3,  6), uzair, "Toshkent–London",    1,       420, "USD",       480,  "USD", "Rustam Nazarov"),
            a(jasur, date(2026, 3, 10), fly,   "Toshkent–Istanbul",  2,       175, "USD",       210,  "USD", malika),
            w(jasur, date(2026, 3, 15), uzair, "Toshkent–Moskva",    1, 1_300_000, "UZS", 1_550_000, "UZS", "Dilorom Karimova"),
            a(jasur, date(2026, 3, 18), fly,   "Toshkent–Dubai",     3,       185, "USD",       220,  "USD", otabek),
            w(jasur, date(2026, 3, 22), umra,  "Makka–Madina",       2, 9_200_000, "UZS",10_400_000, "UZS", "Sherzod Holiqov", pt="UMRA"),
            a(jasur, date(2026, 3, 27), uzair, "Toshkent–Antaliya",  1, 2_000_000, "UZS", 2_350_000, "UZS", sarvar),
            w(jasur, date(2026, 3, 30), fly,   "Toshkent–Istanbul",  1,       190, "USD",       225,  "USD", "Barno Tursunova"),
            a(jasur, date(2026, 4,  2), umra,  "Makka–Madina",       1,10_500_000, "UZS",12_000_000, "UZS", malika, pt="UMRA"),
            w(jasur, date(2026, 4,  7), uzair, "Toshkent–Frankfurt", 2,       305, "USD",       360,  "USD", "Laziz Rahimov"),
            a(jasur, date(2026, 4, 10), fly,   "Toshkent–Dubai",     1, 1_820_000, "UZS", 2_120_000, "UZS", otabek),
            w(jasur, date(2026, 4, 14), uzair, "Toshkent–Antaliya",  2, 2_150_000, "UZS", 2_480_000, "UZS", "Kamola Mirzayeva"),
            a(jasur, date(2026, 4, 17), fly,   "Toshkent–Istanbul",  1,       200, "USD",       238,  "USD", sarvar),
            w(jasur, date(2026, 4, 20), umra,  "Makka–Madina",       3, 9_100_000, "UZS",10_300_000, "UZS", "Husan va Gulnora", pt="UMRA"),
            a(jasur, date(2026, 4, 24), uzair, "Toshkent–Moskva",    1, 1_280_000, "UZS", 1_520_000, "UZS", malika),
            w(jasur, date(2026, 4, 28), fly,   "Toshkent–Dubai",     2,       198, "USD",       235,  "USD", "Zafar Mahmudov"),

            # ── Dilnoza (25 sales) ────────────────────────────────────────
            w(dilnoza, date(2026, 1,  7), uzair, "Toshkent–Frankfurt", 1,  330, "USD",  375, "USD", "Feruza Rahimova"),
            a(dilnoza, date(2026, 1, 14), fly,   "Toshkent–Dubai",     2,  190, "USD",  228, "USD", malika),
            w(dilnoza, date(2026, 1, 21), umra,  "Makka–Madina",       1,  9_500_000, "UZS", 10_800_000, "UZS", "Maftuna Islomova", pt="UMRA"),
            a(dilnoza, date(2026, 1, 28), uzair, "Toshkent–Antaliya",  3,  2_050_000, "UZS", 2_380_000,  "UZS", sarvar),
            w(dilnoza, date(2026, 2,  4), fly,   "Toshkent–Istanbul",  1,  185, "USD",  220, "USD", "Otabek Yunusov"),
            a(dilnoza, date(2026, 2, 10), umra,  "Makka–Madina",       2,  9_800_000, "UZS", 11_000_000, "UZS", otabek, pt="UMRA"),
            w(dilnoza, date(2026, 2, 16), uzair, "Toshkent–Moskva",    1,  1_230_000, "UZS", 1_460_000,  "UZS", "Gulbahor Saidova"),
            a(dilnoza, date(2026, 2, 22), fly,   "Toshkent–Dubai",     1,  195, "USD",  232, "USD", malika),
            w(dilnoza, date(2026, 3,  2), umra,  "Makka–Madina",       1, 10_700_000, "UZS", 12_000_000, "UZS", "Baxtiyor Mirzayev", pt="UMRA"),
            a(dilnoza, date(2026, 3,  8), uzair, "Toshkent–Frankfurt", 1,  315, "USD",  360, "USD", sarvar),
            w(dilnoza, date(2026, 3, 13), fly,   "Toshkent–Istanbul",  2,  180, "USD",  215, "USD", "Shahlo Nazarova"),
            a(dilnoza, date(2026, 3, 18), uzair, "Toshkent–Antaliya",  2,  2_100_000, "UZS", 2_430_000,  "UZS", otabek),
            w(dilnoza, date(2026, 3, 23), fly,   "Toshkent–Dubai",     1,  1_780_000, "UZS", 2_090_000,  "UZS", "Iroda Toshmatova"),
            a(dilnoza, date(2026, 3, 28), umra,  "Makka–Madina",       3,  9_000_000, "UZS", 10_100_000, "UZS", malika, pt="UMRA", note="Oilaviy safari"),
            w(dilnoza, date(2026, 4,  3), uzair, "Toshkent–London",    1,  440, "USD",  500, "USD", "Javlon Ergashev"),
            a(dilnoza, date(2026, 4,  8), fly,   "Toshkent–Dubai",     2,  192, "USD",  228, "USD", sarvar),
            w(dilnoza, date(2026, 4, 12), umra,  "Makka–Madina",       2,  9_300_000, "UZS", 10_500_000, "UZS", "Nilufar Xasanova", pt="UMRA"),
            a(dilnoza, date(2026, 4, 16), uzair, "Toshkent–Moskva",    1,  1_260_000, "UZS", 1_490_000,  "UZS", otabek),
            w(dilnoza, date(2026, 4, 20), fly,   "Toshkent–Istanbul",  1,  188, "USD",  224, "USD", "Ulugbek Qodirov"),
            a(dilnoza, date(2026, 4, 23), uzair, "Toshkent–Antaliya",  3,  2_080_000, "UZS", 2_400_000,  "UZS", malika),
            w(dilnoza, date(2026, 4, 26), umra,  "Makka–Madina",       1, 11_200_000, "UZS", 12_700_000, "UZS", "Sarvinoz Aliyeva", pt="UMRA"),
            a(dilnoza, date(2026, 4, 29), fly,   "Toshkent–Dubai",     1,  197, "USD",  235, "USD", sarvar),

            # ── Bobur (25 sales) ─────────────────────────────────────────
            w(bobur, date(2026, 1,  8), umra,  "Makka–Madina",       1, 10_800_000, "UZS", 12_300_000, "UZS", "Hamid Yusupov", pt="UMRA"),
            a(bobur, date(2026, 1, 15), uzair, "Toshkent–Moskva",    1,  1_220_000, "UZS", 1_450_000,  "UZS", sarvar),
            w(bobur, date(2026, 1, 22), fly,   "Toshkent–Dubai",     2,  188, "USD",  225, "USD", "Zulfiya Normatova"),
            a(bobur, date(2026, 1, 29), umra,  "Makka–Madina",       2,  9_400_000, "UZS", 10_600_000, "UZS", otabek, pt="UMRA"),
            w(bobur, date(2026, 2,  5), uzair, "Toshkent–Frankfurt", 1,  325, "USD",  370, "USD", "Mansur Tursunov"),
            a(bobur, date(2026, 2, 11), fly,   "Toshkent–Istanbul",  1,  182, "USD",  218, "USD", malika),
            w(bobur, date(2026, 2, 17), uzair, "Toshkent–Antaliya",  2,  2_000_000, "UZS", 2_320_000,  "UZS", "Xurshida Mamatova"),
            a(bobur, date(2026, 2, 23), umra,  "Makka–Madina",       1, 10_200_000, "UZS", 11_500_000, "UZS", sarvar, pt="UMRA"),
            w(bobur, date(2026, 3,  3), fly,   "Toshkent–Dubai",     1,  1_760_000, "UZS", 2_060_000,  "UZS", "Dilshod Razzaqov"),
            a(bobur, date(2026, 3,  9), uzair, "Toshkent–London",    1,  430, "USD",  490, "USD", otabek),
            w(bobur, date(2026, 3, 14), umra,  "Makka–Madina",       3,  9_100_000, "UZS", 10_200_000, "UZS", "Rano va Behzod", pt="UMRA"),
            a(bobur, date(2026, 3, 19), fly,   "Toshkent–Dubai",     2,  193, "USD",  230, "USD", malika),
            w(bobur, date(2026, 3, 24), uzair, "Toshkent–Moskva",    1,  1_270_000, "UZS", 1_510_000,  "UZS", "Komiljon Hasanov"),
            a(bobur, date(2026, 3, 29), umra,  "Makka–Madina",       1, 10_900_000, "UZS", 12_400_000, "UZS", sarvar, pt="UMRA"),
            w(bobur, date(2026, 4,  4), fly,   "Toshkent–Istanbul",  1,  186, "USD",  222, "USD", "Nasiba Yuldasheva"),
            a(bobur, date(2026, 4,  9), uzair, "Toshkent–Antaliya",  2,  2_120_000, "UZS", 2_460_000,  "UZS", otabek),
            w(bobur, date(2026, 4, 13), umra,  "Makka–Madina",       2,  9_600_000, "UZS", 10_900_000, "UZS", "Salim Mirzayev", pt="UMRA"),
            a(bobur, date(2026, 4, 17), fly,   "Toshkent–Dubai",     1,  196, "USD",  234, "USD", malika),
            w(bobur, date(2026, 4, 21), uzair, "Toshkent–Frankfurt", 1,  335, "USD",  380, "USD", "Mohira Toshmatova"),
            a(bobur, date(2026, 4, 24), umra,  "Makka–Madina",       3,  8_900_000, "UZS", 10_000_000, "UZS", sarvar, pt="UMRA", note="Guruh safari"),
            w(bobur, date(2026, 4, 27), fly,   "Toshkent–Istanbul",  2,  184, "USD",  220, "USD", "Jasur Norqo'ziyev"),
            a(bobur, date(2026, 4, 29), uzair, "Toshkent–Moskva",    1,  1_240_000, "UZS", 1_470_000,  "UZS", otabek),
            w(bobur, date(2026, 4, 30), umra,  "Makka–Madina",       1, 11_100_000, "UZS", 12_600_000, "UZS", "Barno Alijonova", pt="UMRA"),
            a(bobur, date(2026, 3, 5),  fly,   "Toshkent–Dubai",     2,  191, "USD",  228, "USD", malika),
            w(bobur, date(2026, 2, 28), uzair, "Toshkent–Antaliya",  1,  2_080_000, "UZS", 2_410_000,  "UZS", "Eldor Xoliqov"),
        ]

        for data in SALES:
            Sale.objects.create(**data)
        self.stdout.write(f"  created {len(SALES)} seed sales")
