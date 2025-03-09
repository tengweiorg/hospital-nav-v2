from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from datetime import datetime
from accounts.forms import UserForm, ProfileForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Link, Category

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
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    context = {
        'client_ip': ip,
        'current_time': current_time
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

@csrf_exempt
@require_POST
def increment_click_count(request, link_id):
    try:
        link = Link.objects.get(id=link_id)
        link.click_count += 1
        link.save(update_fields=['click_count'])  # 只更新点击次数字段
        return JsonResponse({
            'success': True, 
            'click_count': link.click_count,
            'is_hot': link.click_count > 100
        })
    except Link.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Link not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

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
