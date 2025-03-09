from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': '名',
            'last_name': '姓',
            'email': '电子邮箱',
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['department', 'position']
        labels = {
            'department': '部门',
            'position': '职位',
        } 