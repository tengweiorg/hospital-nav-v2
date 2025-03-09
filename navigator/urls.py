from django.urls import path
from . import views

urlpatterns = [
    # 根路径指向 index 视图
    path('', views.index, name='index'),
    
    # API 端点用于记录点击次数
    path('api/link/<int:link_id>/click/', views.increment_click_count, name='increment_click_count'),
    
    # API 端点用于获取分类数据
    path('api/categories', views.get_categories, name='get_categories'),
    
    # 添加HTMX端点
    path('api/htmx/categories', views.htmx_categories, name='htmx_categories'),
    path('api/htmx/search', views.htmx_search, name='htmx_search'),
    path('api/htmx/popular', views.htmx_popular, name='htmx_popular'),
] 