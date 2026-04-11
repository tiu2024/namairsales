from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.index, name="index"),
    path("sotuvlar/", views.salesman_sales, name="salesman_sales"),
    path("sotuvlar/yangi/", views.sale_form_get, name="sale_form"),
    path("sotuvlar/qoshish/", views.sale_add, name="sale_add"),
    path("sotuvlar/barchasi/", views.accountant_sales, name="accountant_sales"),
    path("sotuvlar/<int:pk>/hisob/", views.sale_link_account, name="sale_link_account"),
    path("yetkazib-beruvchilar/", views.supplier_list, name="supplier_list"),
    path("yetkazib-beruvchilar/<int:pk>/", views.supplier_detail, name="supplier_detail"),
    path("agentlar/", views.agent_list, name="agent_list"),
    path("agentlar/<int:pk>/", views.agent_detail, name="agent_detail"),
]
