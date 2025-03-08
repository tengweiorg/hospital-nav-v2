from django.contrib import admin
from .models import Category, Link

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'order', 'pinyin')
    search_fields = ('name', 'pinyin')
    ordering = ('order', 'name')

@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url', 'visibility', 'order')
    list_filter = ('category', 'visibility', 'created_at')
    search_fields = ('title', 'description', 'url', 'pinyin')
    ordering = ('category', 'order', 'title')
    readonly_fields = ('pinyin', 'created_at', 'updated_at')
