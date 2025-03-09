"""
URL configuration for hospital_navigator project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .api import api
from navigator.views import profile, custom_login
from django.contrib.auth import views as auth_views

# 自定义Admin站点标题和头部
admin.site.site_header = '医院内部导航站管理系统'  # 登录页和管理页面顶部标题
admin.site.site_title = '医院导航管理'  # 浏览器标签标题
admin.site.index_title = '管理中心'  # 管理页面的主标题

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
    path('', include('navigator.urls')),
    path('profile/', profile, name='profile'),
    path('login/', custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/', http_method_names=['get', 'post']), name='logout'),
]

# 在开发环境中提供媒体文件
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
