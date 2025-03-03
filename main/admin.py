from django.utils.html import format_html
from django.contrib import admin
from .models import *

class CategoryModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'preview']

    def preview(self, obj):
        if obj.logo :
            return format_html(f"<img width=50 height=50 src='{obj.logo.url}'>")
        else:
            return  'No logo'
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'preview']

    def preview(self, obj):
        return format_html(f"<img width=50 height=50 src='{obj.image.url}'>")
    
    def category(self, obj):
        return obj.price
    
    def get_price(self, obj):
        return obj.price

class PosterModelAdmin(admin.ModelAdmin):
    list_display = ['preview']

    def preview(self, obj):
        return format_html(f"<img width=50 height=50 src='{obj.image.url}'>")


class BranchModelAdmin(admin.ModelAdmin):
    pass

class SettingsModelAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        count = SettingsModel.objects.all().count()
        if count >= 1:
            return False
        return True

admin.site.register(CategoryModel, CategoryModelAdmin)
admin.site.register(UserModel)
admin.site.register(ProductModel, ProductModelAdmin)
admin.site.register(OrderModel)
admin.site.register(PosterModel, PosterModelAdmin)
admin.site.register(BranchModel, BranchModelAdmin)
admin.site.register(SettingsModel, SettingsModelAdmin)


