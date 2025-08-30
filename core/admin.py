from django.contrib import admin
from .models import Category, MenuItem, Bill, BillItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'active']
    list_filter = ['category', 'active']
    search_fields = ['name']


class BillItemInline(admin.TabularInline):
    model = BillItem
    extra = 0
    readonly_fields = ['unit_price', 'line_total']


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ['bill_no', 'customer_name', 'total', 'payment_method', 'created_at']
    list_filter = ['payment_method', 'created_at']
    search_fields = ['bill_no', 'customer_name', 'customer_contact']
    inlines = [BillItemInline]
