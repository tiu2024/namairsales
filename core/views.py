from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


def index(request):
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    return redirect("core:salesman_sales")

from .forms import SaleForm
from .models import Sale


@login_required
def salesman_sales(request):
    sales = (
        Sale.objects.filter(salesman=request.user)
        .select_related("supplier", "agent")
        .order_by("-date", "-created_at")
    )
    return render(request, "core/salesman_sales.html", {"sales": sales})


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
    response = render(request, "core/partials/sale_form.html", {"form": form})
    response["HX-Retarget"] = "#form-slot"
    response["HX-Reswap"] = "innerHTML"
    return response
