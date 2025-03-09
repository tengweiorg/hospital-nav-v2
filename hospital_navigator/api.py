from ninja import NinjaAPI, Router, Schema
from ninja.security import django_auth
from ninja.responses import Response
from typing import List, Optional, Dict, Any, Union
from navigator.models import Category, Link
from django.db.models import Q, F, Count
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# 创建API实例，不支持登录认证
api = NinjaAPI(
    title="医院导航API", 
    version="1.0.0",
    csrf=True,
    docs_url="/api/docs"
)

# 创建路由器进行功能分组
category_router = Router(tags=["分类"])
link_router = Router(tags=["链接"])
user_router = Router(tags=["用户"])
htmx_router = Router(tags=["HTMX端点"])

# ========== Schema定义 ==========

class ErrorResponse(Schema):
    message: str
    
class LinkSchema(Schema):
    id: int
    title: str
    url: str
    description: Optional[str] = None
    icon_class: Optional[str] = None
    visibility: str
    click_count: Optional[int] = 0
    category_id: int
    
class LinkCreateSchema(Schema):
    title: str
    url: str
    description: Optional[str] = None
    icon_class: Optional[str] = None
    visibility: str = "public"
    category_id: int
    
class LinkUpdateSchema(Schema):
    title: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    icon_class: Optional[str] = None
    visibility: Optional[str] = None
    
class CategorySchema(Schema):
    id: int
    name: str
    icon_class: Optional[str] = None
    links: List[LinkSchema]
    
class CategoryCreateSchema(Schema):
    name: str
    icon_class: Optional[str] = None
    
class CategoryUpdateSchema(Schema):
    name: Optional[str] = None
    icon_class: Optional[str] = None
    
class UserProfileSchema(Schema):
    department: Optional[str] = None
    position: Optional[str] = None
    
class UserSchema(Schema):
    username: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile: Optional[UserProfileSchema] = None
    is_staff: bool = False

# ========== API端点 ==========

# 分类相关API
@category_router.get("/", response=List[CategorySchema])
def list_categories(request):
    """获取所有分类及其链接"""
    categories = Category.objects.all().order_by('order', 'name')
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
            "icon_class": category.icon_class,
            "links": [
                {
                    "id": link.id,
                    "title": link.title,
                    "url": link.url,
                    "description": link.description,
                    "icon_class": link.icon_class,
                    "visibility": link.visibility,
                    "click_count": link.click_count,
                    "category_id": category.id
                }
                for link in links.order_by('-click_count', 'title')
            ]
        }
        result.append(cat_data)
    
    return result

@category_router.get("/{int:category_id}", response=CategorySchema)
def get_category(request, category_id: int):
    """获取单个分类详情"""
    category = get_object_or_404(Category, id=category_id)
    
    # 根据用户登录状态过滤链接
    if request.user.is_authenticated:
        links = category.links.all()
    else:
        links = category.links.filter(visibility='public')
    
    return {
        "id": category.id,
        "name": category.name,
        "icon_class": category.icon_class,
        "links": [
            {
                "id": link.id,
                "title": link.title,
                "url": link.url,
                "description": link.description,
                "icon_class": link.icon_class,
                "visibility": link.visibility,
                "click_count": link.click_count,
                "category_id": category.id
            }
            for link in links.order_by('-click_count', 'title')
        ]
    }

@category_router.post("/", response={201: CategorySchema}, auth=django_auth)
def create_category(request, data: CategoryCreateSchema):
    """创建新分类(需要管理员权限)"""
    if not request.user.is_staff:
        return Response({"message": "没有权限执行此操作"}, status=403)
    
    category = Category.objects.create(
        name=data.name,
        icon_class=data.icon_class
    )
    
    return 201, {
        "id": category.id,
        "name": category.name,
        "icon_class": category.icon_class,
        "links": []
    }

# 链接相关API
@link_router.get("/search", response=List[Dict[str, Any]])
def search_links(request, q: str = ""):
    """搜索链接的API端点"""
    if not q or len(q) < 1:
        return []
    
    # 搜索标题、描述和拼音
    links = Link.objects.filter(
        Q(title__icontains=q) | 
        Q(description__icontains=q) |
        Q(pinyin__icontains=q)
    ).select_related('category')
    
    # 检查可见性
    if not request.user.is_authenticated:
        links = links.filter(visibility='public')
    
    results = []
    for link in links[:15]:  # 限制返回15个结果
        results.append({
            "id": link.id,
            "title": link.title,
            "url": link.url,
            "description": link.description,
            "icon_class": link.icon_class,
            "category_name": link.category.name,
            "click_count": link.click_count
        })
    
    return results

@method_decorator(csrf_exempt, name="dispatch")
@link_router.post("/{int:link_id}/click", response={200: Dict[str, Any]})
def click_link(request, link_id: int):
    """记录链接点击"""
    link = get_object_or_404(Link, id=link_id)
    link.click_count = F('click_count') + 1
    link.save(update_fields=['click_count'])
    
    # 重新获取最新数据
    link.refresh_from_db()
    
    # 只返回新的点击计数值作为纯文本
    return {
        "id": link.id,
        "click_count": link.click_count,
        "html": str(link.click_count)  # 纯文本返回，用于直接插入
    }

@link_router.get("/popular", response=List[Dict[str, Any]])
def popular_links(request, limit: int = 10):
    """获取最热门的链接"""
    query = Link.objects.all().order_by('-click_count')
    
    # 检查可见性
    if not request.user.is_authenticated:
        query = query.filter(visibility='public')
    
    links = query[:limit]
    
    return [
        {
            "id": link.id,
            "title": link.title,
            "url": link.url,
            "description": link.description,
            "icon_class": link.icon_class,
            "click_count": link.click_count,
            "category_id": link.category_id
        }
        for link in links
    ]

# 用户相关API
@user_router.get("/me", response=UserSchema, auth=django_auth)
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
        "profile": profile_data,
        "is_staff": user.is_staff
    }

# HTMX相关端点
@htmx_router.get("/categories")
def htmx_categories(request):
    """获取分类列表，HTMX端点"""
    categories = Category.objects.all().order_by('order', 'name')
    result = []
    
    for category in categories:
        # 根据用户登录状态过滤链接
        if request.user.is_authenticated:
            links = category.links.all()
        else:
            links = category.links.filter(visibility='public')
        
        if not links.exists():
            continue  # 跳过没有链接的分类
        
        result.append({
            "id": category.id,
            "name": category.name,
            "icon_class": category.icon_class,
            "links": list(links.order_by('-click_count', 'title'))
        })
    
    # 渲染HTML片段
    html = render_to_string('navigator/partials/categories.html', {
        'categories': result
    })
    
    return HttpResponse(html)

@htmx_router.get("/search")
def htmx_search(request, q: str = ""):
    """HTMX搜索端点，返回HTML片段"""
    if not q or len(q) < 1:
        return HttpResponse("")
    
    # 搜索标题、描述和拼音
    links = Link.objects.filter(
        Q(title__icontains=q) | 
        Q(description__icontains=q) |
        Q(pinyin__icontains=q)
    ).select_related('category')
    
    # 检查可见性
    if not request.user.is_authenticated:
        links = links.filter(visibility='public')
    
    # 渲染HTML片段
    html = render_to_string('navigator/partials/search_results.html', {
        'links': links[:15]
    })
    
    return HttpResponse(html)

@htmx_router.get("/popular")
def htmx_popular_links(request, limit: int = 10):
    """获取热门链接的HTMX端点"""
    # 先获取置顶链接
    pinned_links = Link.objects.filter(is_pinned=True)
    
    # 检查可见性
    if not request.user.is_authenticated:
        pinned_links = pinned_links.filter(visibility='public')
    
    # 获取非置顶但热门的链接
    remaining_count = max(0, limit - pinned_links.count())
    if remaining_count > 0:
        hot_links = Link.objects.filter(is_pinned=False).order_by('-click_count')
        if not request.user.is_authenticated:
            hot_links = hot_links.filter(visibility='public')
        hot_links = hot_links[:remaining_count]
    else:
        hot_links = Link.objects.none()
    
    # 合并置顶和热门链接
    links = list(pinned_links) + list(hot_links)
    
    # 渲染HTML片段
    html = render_to_string('navigator/partials/popular_links.html', {
        'links': links
    })
    
    return HttpResponse(html)

# 注册路由器
api.add_router("/categories", category_router)
api.add_router("/links", link_router)
api.add_router("/users", user_router)
api.add_router("/htmx", htmx_router) 