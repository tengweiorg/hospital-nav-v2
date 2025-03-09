from ninja import NinjaAPI, Schema
from ninja.security import django_auth
from typing import List, Optional, Dict, Any
from navigator.models import Category, Link
from django.db.models import Q
from django.shortcuts import get_object_or_404

api = NinjaAPI(title="医院导航API", version="1.0.0")

# Schema定义
class LinkSchema(Schema):
    id: int
    title: str
    url: str
    description: Optional[str] = None
    icon_class: Optional[str] = None
    visibility: str

class CategorySchema(Schema):
    id: int
    name: str
    icon: Optional[str] = None
    links: List[LinkSchema]

class UserProfileSchema(Schema):
    department: Optional[str] = None
    position: Optional[str] = None

class UserSchema(Schema):
    username: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile: Optional[UserProfileSchema] = None

# API端点
@api.get("/categories", response=List[CategorySchema])
def list_categories(request):
    """获取所有分类及其链接"""
    categories = Category.objects.all()
    result = []
    
    for category in categories:
        # 根据用户登录状态过滤链接
        if request.user.is_authenticated:
            links = category.links.all()
        else:
            links = category.links.filter(visibility='public')
        
        if not links.exists():
            continue  # 跳过没有链接的分类
        
        cat_data = {
            "id": category.id,
            "name": category.name,
            "icon": category.icon,
            "links": [
                {
                    "id": link.id,
                    "title": link.title,
                    "url": link.url,
                    "description": link.description,
                    "icon_class": link.icon_class,
                    "visibility": link.visibility
                }
                for link in links
            ]
        }
        result.append(cat_data)
    
    return result

@api.get("/search")
def search_links(request, q: str = ""):
    """搜索链接的API端点"""
    if not q or len(q) < 1:
        return []
    
    # 搜索标题、描述和拼音
    links = Link.objects.filter(
        Q(title__icontains=q) | 
        Q(description__icontains=q) |
        Q(pinyin__icontains=q)
    )
    
    # 检查可见性
    if not request.user.is_authenticated:
        links = links.filter(visibility='public')
    
    results = []
    for link in links[:10]:  # 限制返回10个结果
        results.append({
            "id": link.id,
            "title": link.title,
            "url": link.url,
            "description": link.description,
            "icon_class": link.icon_class,
            "category_name": link.category.name
        })
    
    return results

@api.get("/user", response=UserSchema, auth=django_auth)
def get_user_info(request):
    """获取当前用户信息，需要登录"""
    user = request.user
    
    try:
        profile = user.profile
        profile_data = {
            "department": profile.department,
            "position": profile.position
        }
    except Exception:
        profile_data = None
    
    return {
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "profile": profile_data
    } 