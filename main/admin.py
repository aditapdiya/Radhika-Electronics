from django.contrib import admin
from .models import Category, Brand, Product, Order, Feedback, Wishlist, UserProfile



class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'mobile', 'address')
    search_fields = ('user__username', 'mobile', 'address')
    list_filter = ('user',)

admin.site.register(UserProfile, UserProfileAdmin)

# Register your models here.
admin.site.register(Wishlist)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Feedback)