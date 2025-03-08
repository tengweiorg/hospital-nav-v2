from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="用户")
    department = models.CharField(max_length=100, blank=True, verbose_name="部门")
    position = models.CharField(max_length=100, blank=True, verbose_name="职位")
    
    class Meta:
        verbose_name = "用户资料"
        verbose_name_plural = "用户资料"
    
    def __str__(self):
        return f"{self.user.username}的个人资料"
