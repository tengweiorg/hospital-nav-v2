from django.db import models
from django.contrib.auth.models import User
from pypinyin import lazy_pinyin

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="分类名称")
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome图标类名", verbose_name="图标类名")
    order = models.PositiveIntegerField(default=0, verbose_name="排序")
    pinyin = models.CharField(max_length=200, blank=True, verbose_name="拼音", help_text="自动生成，用于搜索")
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = "分类"
        verbose_name_plural = "分类"
    
    def save(self, *args, **kwargs):
        # 生成拼音
        self.pinyin = ''.join(lazy_pinyin(self.name))
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Link(models.Model):
    VISIBILITY_CHOICES = (
        ('public', '所有人可见'),
        ('authenticated', '仅登录用户可见'),
    )
    
    title = models.CharField(max_length=200, verbose_name="标题")
    url = models.URLField(verbose_name="链接地址")
    description = models.TextField(blank=True, verbose_name="描述")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='links', verbose_name="所属分类")
    icon = models.ImageField(upload_to='link_icons/', blank=True, null=True, verbose_name="图标")
    icon_class = models.CharField(max_length=50, blank=True, help_text="FontAwesome图标类名", verbose_name="图标类名")
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public', verbose_name="可见性")
    order = models.PositiveIntegerField(default=0, verbose_name="排序")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    pinyin = models.CharField(max_length=500, blank=True, verbose_name="拼音", help_text="自动生成，用于搜索")
    click_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['category', 'order', 'title']
        verbose_name = "链接"
        verbose_name_plural = "链接"
    
    def save(self, *args, **kwargs):
        # 生成拼音
        self.pinyin = ''.join(lazy_pinyin(self.title))
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
