from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from datetime import datetime
from accounts.forms import UserForm, ProfileForm
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Link, Category, Folder, File
from django.db.models import Q, F
import locale

# Create your views here.

def index(request):
    """首页视图"""
    # 获取客户端IP地址
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    # 获取当前时间
    try:
        locale.setlocale(locale.LC_TIME, 'zh_CN.UTF-8')  # 设置中文环境
    except:
        pass  # 如果失败，保持默认环境
        
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    
    # 自定义星期几
    weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
    weekday = weekdays[now.weekday()]
    
    current_date = f"{now.year}年{now.month}月{now.day}日 {weekday}"
    
    # 获取热门链接
    if request.user.is_authenticated:
        popular_links = Link.objects.all().order_by('-click_count')[:9]
    else:
        popular_links = Link.objects.filter(visibility='public').order_by('-click_count')[:9]
    
    context = {
        'client_ip': ip,
        'current_time': current_time,
        'current_date': current_date,
        'popular_links': popular_links  # 添加热门链接到上下文
    }
    
    return render(request, 'navigator/index.html', context)

@login_required
def profile(request):
    """用户资料页面，需要登录"""
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "个人资料已更新！")
            return redirect('profile')
        else:
            messages.error(request, "更新失败，请检查表单内容！")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    
    return render(request, 'navigator/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def custom_login(request):
    """自定义登录视图，处理"记住我"功能"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # 检查"记住我"是否被选中
            remember_me = request.POST.get('remember_me')
            
            # 如果没有选择"记住我"，设置会话在浏览器关闭时过期
            if remember_me is None:
                request.session.set_expiry(0)
            
            # 执行登录
            login(request, user)
            
            # 获取next参数或默认重定向到首页
            next_url = request.POST.get('next', '/')
            return redirect(next_url)
        
        # 认证失败
        return render(request, 'navigator/login.html', {
            'form_errors': True,
            'next': request.POST.get('next', '/')
        })
    
    # GET请求直接展示登录页
    return render(request, 'navigator/login.html', {
        'next': request.GET.get('next', '/')
    })

@require_POST
def increment_click_count(request, link_id):
    """记录链接点击次数的API端点"""
    try:
        # 记录请求信息
       
        # 使用F表达式更新计数
        Link.objects.filter(id=link_id).update(click_count=F('click_count') + 1)
        
        # 获取更新后的链接
        link = Link.objects.get(id=link_id)
        
        return JsonResponse({
            'status': 'success',
            'click_count': link.click_count
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def get_categories(request):
    categories = Category.objects.all().order_by('order', 'name')
    data = []
    
    for category in categories:
        links = []
        for link in category.links.all():
            # 检查链接可见性
            if link.visibility == 'all' or (link.visibility == 'authenticated' and request.user.is_authenticated):
                links.append({
                    'id': link.id,
                    'title': link.title,
                    'url': link.url,
                    'description': link.description,
                    'icon_class': link.icon_class,
                    'click_count': link.click_count  # 添加点击次数
                })
        
        data.append({
            'id': category.id,
            'name': category.name,
            'icon_class': category.icon_class,
            'links': links
        })
    
    return JsonResponse(data, safe=False)

# 添加HTMX视图函数
def htmx_categories(request):
    """HTMX分类视图，返回HTML片段"""
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
            
        # 转换查询集为列表以便在模板中使用
        links_list = [{
            'id': link.id,
            'title': link.title,
            'url': link.url,
            'description': link.description,
            'icon_class': link.icon_class,
            'click_count': link.click_count
        } for link in links.order_by('-click_count', 'title')]
        
        result.append({
            "id": category.id,
            "name": category.name,
            "icon_class": category.icon_class,
            "links": links_list
        })
    
    return render(request, 'navigator/partials/categories.html', {
        'categories': result
    }, content_type='text/html')

def htmx_search(request):
    """HTMX搜索视图"""
    query = request.GET.get('q', '')
   
    
    if not query or len(query) < 1:
       
        return HttpResponse('', content_type='text/html')
    
    # 搜索标题、描述和拼音（恢复拼音搜索功能）
    links = Link.objects.filter(
        Q(title__icontains=query) | 
        Q(description__icontains=query) |
        Q(pinyin__icontains=query)  # 恢复拼音搜索
    )
    
   
    
    # 检查可见性
    if not request.user.is_authenticated:
        links = links.filter(visibility='public')
       
    
    # 渲染搜索结果
    html = render(request, 'navigator/partials/search_results.html', {
        'links': links[:15],
        'query': query  # 传递查询参数到模板
    }, content_type='text/html')
    
    return html

def htmx_popular(request):
    """HTMX热门链接视图，返回HTML片段"""
    # 先获取置顶链接
    if request.user.is_authenticated:
        pinned_links = Link.objects.filter(is_pinned=True).order_by('-click_count')
    else:
        pinned_links = Link.objects.filter(is_pinned=True, visibility='public').order_by('-click_count')
    
    # 获取非置顶但热门的链接
    remaining_count = max(0, 10 - pinned_links.count())
    if remaining_count > 0:
        if request.user.is_authenticated:
            hot_links = Link.objects.filter(is_pinned=False).order_by('-click_count')[:remaining_count]
        else:
            hot_links = Link.objects.filter(is_pinned=False, visibility='public').order_by('-click_count')[:remaining_count]
    else:
        hot_links = Link.objects.none()
    
    # 合并置顶和热门链接数据
    links_list = []
    
    # 添加置顶链接
    for link in pinned_links:
        links_list.append({
            'id': link.id,
            'title': link.title,
            'url': link.url,
            'description': link.description,
            'icon_class': link.icon_class,
            'click_count': link.click_count,
            'is_pinned': True  # 明确标记为置顶
        })
    
    # 添加非置顶热门链接
    for link in hot_links:
        links_list.append({
            'id': link.id,
            'title': link.title,
            'url': link.url,
            'description': link.description,
            'icon_class': link.icon_class,
            'click_count': link.click_count,
            'is_pinned': False
        })
    
    return render(request, 'navigator/partials/popular_links.html', {
        'links': links_list
    }, content_type='text/html')

def file_browser(request, folder_id=None):
    """文件浏览器视图"""
    if folder_id:
        current_folder = get_object_or_404(Folder, id=folder_id)
        # 获取当前文件夹的子文件夹
        subfolders = current_folder.subfolders.all()
        # 获取当前文件夹的文件
        files = current_folder.files.all()
        # 获取父文件夹，用于导航
        parent_folder = current_folder.parent
    else:
        # 根文件夹
        current_folder = None
        # 获取顶级文件夹（没有父文件夹的文件夹）
        subfolders = Folder.objects.filter(parent=None)
        files = File.objects.filter(folder=None)
        parent_folder = None
    
    return render(request, 'navigator/file_browser.html', {
        'current_folder': current_folder,
        'subfolders': subfolders,
        'files': files,
        'parent_folder': parent_folder
    })

def download_file(request, file_id):
    """文件下载视图"""
    file_obj = get_object_or_404(File, id=file_id)
    
    # 增加下载计数
    file_obj.download_count += 1
    file_obj.save(update_fields=['download_count'])
    
    # 返回文件响应
    response = FileResponse(file_obj.file.open(), as_attachment=True, filename=file_obj.name)
    return response

def file_view(request, file_id):
    """直接访问文件视图"""
    file_obj = get_object_or_404(File, id=file_id)
    
    # 增加查看计数
    file_obj.view_count = F('view_count') + 1 if hasattr(file_obj, 'view_count') else 1
    file_obj.save(update_fields=['view_count'] if hasattr(file_obj, 'view_count') else [])
    
    # 生成文件直接URL
    file_url = request.build_absolute_uri(file_obj.file.url)
    
    return render(request, 'navigator/file_view.html', {
        'file': file_obj,
        'file_url': file_url
    })
