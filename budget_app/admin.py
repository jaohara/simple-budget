from django.contrib import admin
from .models import Category, Transaction, Bill, UserRecord

admin.site.register(Category)
admin.site.register(Transaction)
admin.site.register(Bill)
admin.site.register(UserRecord)
