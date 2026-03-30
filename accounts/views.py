from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render

from .forms import LoginForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect("core:salesman_sales")
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )
        if user is not None:
            login(request, user)
            return redirect(request.GET.get("next") or "core:salesman_sales")
        form.add_error(None, "error")
    return render(request, "accounts/login.html", {"form": form})
