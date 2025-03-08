from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime

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
    return render(request, 'navigator/profile.html')
