from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.index, name="index"),
    path("sotuvlar/", views.salesman_sales, name="salesman_sales"),
    path("sotuvlar/yangi/", views.sale_form_get, name="sale_form"),
    path("sotuvlar/qoshish/", views.sale_add, name="sale_add"),
    path("sotuvlar/barchasi/", views.accountant_sales, name="accountant_sales"),
    path("sotuvlar/barchasi/export/", views.accountant_sales_export, name="accountant_sales_export"),
    path("sotuvlar/export/", views.salesman_sales_export, name="salesman_sales_export"),
    path("sotuvlar/<int:pk>/hisob/", views.sale_link_account, name="sale_link_account"),
    path("sotuvlar/<int:pk>/tahrirlash/", views.sale_edit, name="sale_edit"),
    path("sotuvlar/<int:pk>/ochirish/", views.sale_delete, name="sale_delete"),
    path("yetkazib-beruvchilar/", views.supplier_list, name="supplier_list"),
    path("yetkazib-beruvchilar/<int:pk>/", views.supplier_detail, name="supplier_detail"),
    path("yetkazib-beruvchilar/<int:pk>/export/", views.supplier_detail_export, name="supplier_detail_export"),
    path("yetkazib-beruvchilar/<int:pk>/tahrirlash/", views.supplier_edit, name="supplier_edit"),
    path("yetkazib-beruvchilar/<int:pk>/ochirish/", views.supplier_delete, name="supplier_delete"),
    path("agentlar/", views.agent_list, name="agent_list"),
    path("agentlar/<int:pk>/", views.agent_detail, name="agent_detail"),
    path("agentlar/<int:pk>/export/", views.agent_detail_export, name="agent_detail_export"),
    path("agentlar/<int:pk>/tahrirlash/", views.agent_edit, name="agent_edit"),
    path("agentlar/<int:pk>/ochirish/", views.agent_delete, name="agent_delete"),
    path("xarajatlar/", views.expenditure_list, name="expenditure_list"),
    path("xarajatlar/export/", views.expenditure_export, name="expenditure_export"),
    path("xarajatlar/<int:pk>/tahrirlash/", views.expenditure_edit, name="expenditure_edit"),
    path("xarajatlar/<int:pk>/arxivlash/", views.expenditure_archive, name="expenditure_archive"),
    path("sotuvchilar/", views.salesman_list, name="salesman_list"),
    path("sotuvchilar/<int:pk>/tahrirlash/", views.salesman_edit, name="salesman_edit"),
    path("sotuvchilar/<int:pk>/ochirish/", views.salesman_deactivate, name="salesman_deactivate"),
    path("hisob-raqamlar/", views.financial_account_list, name="financial_account_list"),
    path("hisob-raqamlar/<int:pk>/", views.financial_account_detail, name="financial_account_detail"),
    path("hisob-raqamlar/<int:pk>/tahrirlash/", views.financial_account_edit, name="financial_account_edit"),
    path("hisob-raqamlar/<int:pk>/arxivlash/", views.financial_account_archive, name="financial_account_archive"),
]
