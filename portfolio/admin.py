from django.contrib import admin
from portfolio.models import User, Stock, Trade

# Register your models here.
admin.site.register(User)
admin.site.register(Stock)
admin.site.register(Trade)