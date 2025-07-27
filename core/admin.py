from django.contrib import admin

# Change admin header and title
admin.site.site_header = "GAZA BUSINESS SERVICE ENTRS. Admin Panel"
admin.site.site_title = "GAZA BUSINESS SERVICE ENTRS."
admin.site.index_title = "Welcome to GAZA BUSINESS SERVICE ENTRS. Admin Panel"

from .models import User, Item, Sale, SaleItem

# Register User model
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    search_fields = ('username', 'email')

# Register Item model
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock_qty')
    search_fields = ('name',)
    list_filter = ('price',)

# Register Sale model
class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'payment_type', 'date')
    list_filter = ('payment_type', 'date')
    search_fields = ('user__username',)
    inlines = [SaleItemInline]

# Register SaleItem model (optional, because it's inline)
@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ('sale', 'item', 'quantity', 'unit_price')

