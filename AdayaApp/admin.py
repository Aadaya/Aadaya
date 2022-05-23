from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from import_export.admin import ImportExportMixin

from .models import Account, Contact, UserProfile, Category, Product,Notification,TermsAndConditions


class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined', 'is_active')
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(Account, AccountAdmin)
admin.site.register(Contact)
admin.site.register(UserProfile)


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('category_name', 'slug')


admin.site.register(Category, CategoryAdmin)


class ProductAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = (
    'drug_code', 'product_name', 'batch', 'expiry_date', 'unit_quantity', 'MRP', 'Rate', 'stock', 'is_available',
    'created_date')
    list_filter = ('product_name', 'stock', 'expiry_date')


admin.site.register(Product, ProductAdmin)
admin.site.register(Notification)
admin.site.register(TermsAndConditions)