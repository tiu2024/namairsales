from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.index, name="index"),
    path("sotuvlar/", views.salesman_sales, name="salesman_sales"),
    path("sotuvlar/yangi/", views.sale_form_get, name="sale_form"),
    path("sotuvlar/qoshish/", views.sale_add, name="sale_add"),
]
