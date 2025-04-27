from django.contrib import admin
from portfolio.models import User, Stock, Trade

# Register your models here.
class TradeAdmin(admin.ModelAdmin):
    list_display = ('get_user_name', 'get_stock_name', 'quantity', 'trade_price', 'direction', 'date')
    search_fields = ('user__name', 'stock__stock_name')
    list_filter = ('direction', 'date')

    @admin.display(description='User', ordering='user__name')
    def get_user_name(self, obj):
        return obj.user.name
    
    @admin.display(description='Stock', ordering='stock__stock_name')
    def get_stock_name(self, obj):
        return obj.stock.stock_name
    
class StockAdmin(admin.ModelAdmin):
    list_display = ('script_code', 'stock_name', 'price')
    search_fields = ('stock_name', 'stock_symbol')
    
admin.site.register(User)
admin.site.register(Stock, StockAdmin)
admin.site.register(Trade, TradeAdmin)