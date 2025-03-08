from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = '用户资料'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_department')
    
    def get_department(self, obj):
        try:
            return obj.profile.department
        except UserProfile.DoesNotExist:
            return ''
    get_department.short_description = '部门'

# 重新注册User模型
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
