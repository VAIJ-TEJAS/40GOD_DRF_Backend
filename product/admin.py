from django.contrib import admin
from .models import Product, Color, Image, Size, Tag
from category.models import Category


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1


class ColorInline(admin.TabularInline):
    model = Color
    extra = 1
    inlines = [
        ImageInline,
    ]


class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ColorInline,
    ]


class ColorAdmin(admin.ModelAdmin):
    inlines = [
        ImageInline,
    ]


admin.site.register(Tag)
admin.site.register(Size)
admin.site.register(Category)
admin.site.register(Image)
admin.site.register(Color, ColorAdmin)
admin.site.register(Product, ProductAdmin)
