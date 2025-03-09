from django.db import models
from django.contrib.auth.models import User
from pypinyin import lazy_pinyin
import os
from django.conf import settings
import uuid

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="分类名称")
    icon_class = models.CharField(max_length=50, blank=True, help_text="FontAwesome图标类名", verbose_name="图标类名")
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
    is_pinned = models.BooleanField(default=False, verbose_name="置顶显示", help_text="置顶的链接将优先显示在热门链接区域")
    
    class Meta:
        ordering = ['-is_pinned', '-click_count', 'order', 'title']
        verbose_name = "链接"
        verbose_name_plural = "链接"
    
    def save(self, *args, **kwargs):
        # 生成拼音
        self.pinyin = ''.join(lazy_pinyin(self.title))
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title

class Folder(models.Model):
    """文件夹模型"""
    name = models.CharField(max_length=100, verbose_name="文件夹名称")
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subfolders', verbose_name="父文件夹")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "文件夹"
        verbose_name_plural = "文件夹"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_full_path(self):
        """获取完整路径"""
        if self.parent:
            return os.path.join(self.parent.get_full_path(), self.name)
        return self.name
    
    @property
    def has_subfolders(self):
        """检查是否有子文件夹"""
        return self.subfolders.exists()
        
    @property
    def has_files(self):
        """检查是否有文件"""
        return self.files.exists()

class File(models.Model):
    """文件模型"""
    name = models.CharField(max_length=100, verbose_name="文件名")
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='files', verbose_name="所属文件夹")
    file = models.FileField(upload_to='downloads/', verbose_name="文件")
    description = models.TextField(blank=True, null=True, verbose_name="文件描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="上传时间")
    download_count = models.PositiveIntegerField(default=0, verbose_name="下载次数")
    share_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    view_count = models.PositiveIntegerField(default=0, verbose_name="查看次数")
    
    class Meta:
        verbose_name = "文件"
        verbose_name_plural = "文件"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_file_size(self):
        """获取文件大小"""
        try:
            return self.file.size
        except:
            return 0
            
    def get_file_extension(self):
        """获取文件扩展名"""
        return os.path.splitext(self.file.name)[1][1:].upper()

    def get_share_url(self):
        return f"/file/{self.id}/{self.share_code}/"
