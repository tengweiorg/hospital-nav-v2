from django.contrib import admin
from .models import Category, Link

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_class', 'order', 'pinyin')
    search_fields = ('name', 'pinyin')
    ordering = ('order', 'name')

@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url', 'visibility', 'is_pinned', 'click_count', 'order')
    list_filter = ('category', 'visibility', 'is_pinned', 'created_at')
    search_fields = ('title', 'description', 'url', 'pinyin')
    ordering = ('-is_pinned', 'category', 'order', 'title')
    readonly_fields = ('pinyin', 'created_at', 'updated_at', 'click_count')
    list_editable = ('is_pinned', 'order')
    actions = ['pin_links', 'unpin_links']
    
    def pin_links(self, request, queryset):
        queryset.update(is_pinned=True)
        self.message_user(request, f"{queryset.count()} 个链接已置顶")
    pin_links.short_description = "置顶选中的链接"
    
    def unpin_links(self, request, queryset):
        queryset.update(is_pinned=False)
        self.message_user(request, f"{queryset.count()} 个链接已取消置顶")
    unpin_links.short_description = "取消选中链接的置顶"
