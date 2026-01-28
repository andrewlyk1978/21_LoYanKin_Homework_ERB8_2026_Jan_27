from import_export.admin import ImportExportModelAdmin

from django.contrib import admin

# Register your models here.


from .models import Customer, Product, Order


#(ImportExportModelAdmin)

@admin.register(Customer)
class CustomerAdmin(ImportExportModelAdmin):
    list_display = ("name", "email", "age", "city")
    search_fields = ("name", "email", "city")
    list_filter = ("city",)


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    list_display = ("name", "category", "price")
    search_fields = ("name", "category")
    list_filter = ("category",)


@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin):
    list_display = ("customer", "product", "quantity", "order_date")
    list_filter = ("order_date", "product__category")
    search_fields = ("customer__name", "product__name")
