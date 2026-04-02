from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.shortcuts import redirect, render


def index(request):
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    return redirect("core:salesman_sales")

from .forms import SaleForm
from .models import Agent, Sale, Supplier


@login_required
def salesman_sales(request):
    # Parse filter params
    date_from_str = request.GET.get("date_from", "").strip()
    date_to_str   = request.GET.get("date_to", "").strip()
    currency      = request.GET.get("currency", "").strip()
    agent_id      = request.GET.get("agent", "").strip()
    supplier_id   = request.GET.get("supplier", "").strip()

    def parse_date(s):
        try:
            return datetime.strptime(s, "%d.%m.%Y").date()
        except ValueError:
            return None

    date_from = parse_date(date_from_str)
    date_to   = parse_date(date_to_str)

    # Base queryset
    all_sales = (
        Sale.objects.filter(salesman=request.user)
        .select_related("supplier", "agent")
        .order_by("-date", "-created_at")
    )

    # Apply filters
    if date_from:
        all_sales = all_sales.filter(date__gte=date_from)
    if date_to:
        all_sales = all_sales.filter(date__lte=date_to)
    if currency in ("UZS", "USD"):
        all_sales = all_sales.filter(sold_currency=currency)
    if agent_id.isdigit():
        all_sales = all_sales.filter(agent_id=int(agent_id))
    if supplier_id.isdigit():
        all_sales = all_sales.filter(supplier_id=int(supplier_id))

    # Aggregates (scoped to filtered queryset)
    total_sold_uzs = all_sales.filter(sold_currency="UZS").aggregate(
        t=Sum("sold_price"))["t"] or 0
    total_sold_usd = all_sales.filter(sold_currency="USD").aggregate(
        t=Sum("sold_price"))["t"] or 0

    _profit_expr = ExpressionWrapper(
        (F("sold_price") - F("acquired_price")) * F("quantity"),
        output_field=DecimalField(),
    )
    profit_uzs = (
        all_sales.filter(acquired_currency="UZS", sold_currency="UZS")
        .annotate(lp=_profit_expr)
        .aggregate(t=Sum("lp"))["t"] or 0
    )
    profit_usd = (
        all_sales.filter(acquired_currency="USD", sold_currency="USD")
        .annotate(lp=_profit_expr)
        .aggregate(t=Sum("lp"))["t"] or 0
    )

    paginator = Paginator(all_sales, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    params = request.GET.copy()
    params.pop("page", None)
    filter_query = params.urlencode()

    return render(request, "core/salesman_sales.html", {
        "sales": page_obj,
        "page_obj": page_obj,
        "form": SaleForm(),
        "total_sold_uzs": total_sold_uzs,
        "total_sold_usd": total_sold_usd,
        "profit_uzs": profit_uzs,
        "profit_usd": profit_usd,
        "filter_date_from": date_from_str,
        "filter_date_to": date_to_str,
        "filter_currency": currency,
        "filter_agent_id": agent_id,
        "filter_supplier_id": supplier_id,
        "all_agents": Agent.objects.order_by("name"),
        "all_suppliers": Supplier.objects.order_by("name"),
        "filter_query": filter_query,
    })


@login_required
def sale_form_get(request):
    if not request.headers.get("HX-Request"):
        return redirect("core:salesman_sales")
    return render(request, "core/partials/sale_form.html", {"form": SaleForm()})


@login_required
def sale_add(request):
    if not request.headers.get("HX-Request"):
        return redirect("core:salesman_sales")
    form = SaleForm(request.POST)
    if form.is_valid():
        sale = form.save(commit=False)
        sale.salesman = request.user
        sale.save()
        sale = Sale.objects.select_related("supplier", "agent").get(pk=sale.pk)
        return render(request, "core/partials/sale_row.html", {"sale": sale})
    response = render(request, "core/partials/sale_form.html", {"form": form}, status=400)
    response["HX-Reswap"] = "none"
    return response
