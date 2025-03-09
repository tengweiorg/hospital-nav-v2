from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """当用户创建时，自动创建对应的用户资料（如果不存在）"""
    if created:
        # 使用get_or_create而不是直接create，避免重复创建
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """当用户保存时，同时保存用户资料"""
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        # 如果用户资料不存在，创建一个
        UserProfile.objects.create(user=instance) 