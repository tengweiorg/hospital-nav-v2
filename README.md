# 医院内部导航站

![版本](https://img.shields.io/badge/版本-1.0.0-blue)
![Django](https://img.shields.io/badge/Django-5.1.7-green)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.x-blueviolet)
![HTMX](https://img.shields.io/badge/HTMX-1.9.2-orange)
![SQLite](https://img.shields.io/badge/SQLite-3.41.2-blue)

医院内部导航站是一个专为医院内部员工设计的网站导航系统，提供集中、高效的链接管理和资源访问平台。

![screenshot](screenshot.png)

## 功能特点

- 🔍 **分类浏览**：链接按照不同分类组织，便于查找
- 🔥 **热门链接**：自动展示点击量最高的链接
- 📌 **链接置顶**：重要链接可置顶显示
- 🔎 **实时搜索**：无刷新搜索体验，支持拼音搜索
- 📁 **文件管理**：支持文件上传、下载和分享
- 👤 **用户管理**：用户认证和个人资料管理
- 📊 **使用统计**：记录链接点击和文件下载次数
- 📱 **响应式设计**：适配各种设备屏幕

## 技术栈

- **后端**：Django 5.1.7 + Django-Ninja
- **前端**：HTML + TailwindCSS + HTMX + JavaScript
- **数据库**：SQLite (开发) / PostgreSQL (生产)

## 安装指南

### 前提条件

- Python 3.10+
- pip
- Git

### 安装步骤

1. **克隆仓库**

```bash
git clone https://github.com/yourusername/hospital-navigator.git
cd hospital-navigator
```

2. **创建虚拟环境**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. **安装依赖**

```bash
pip install -r requirements.txt
```

4. **创建必要的目录**

```bash
mkdir -p media/downloads media/link_icons static/img staticfiles
```

5. **初始化数据库**

```bash
python manage.py migrate
```

6. **创建超级用户**

```bash
python manage.py createsuperuser
```

7. **收集静态文件**

```bash
python manage.py collectstatic
```

8. **启动开发服务器**

```bash
python manage.py runserver
```

现在，您可以访问 http://127.0.0.1:8000/ 查看网站，或访问 http://127.0.0.1:8000/admin/ 进入管理后台。

## 项目结构

```
hospital_navigator/
├── accounts/                  # 用户账户相关应用
│   ├── admin.py               # 用户管理后台配置
│   ├── forms.py               # 用户表单定义
│   ├── models.py              # 用户模型定义
│   └── signals.py             # 用户信号处理
├── navigator/                 # 主导航应用
│   ├── admin.py               # 导航管理后台配置
│   ├── models.py              # 导航模型定义
│   ├── urls.py                # URL路由配置
│   ├── views.py               # 视图函数
│   └── templates/             # 模板文件
├── hospital_navigator/        # 项目核心配置
│   ├── api.py                 # API定义
│   ├── middleware.py          # 中间件
│   ├── settings.py            # 项目设置
│   └── urls.py                # 主URL配置
├── static/                    # 静态文件
├── templates/                 # 全局模板
├── media/                     # 媒体文件存储（需手动创建）
├── staticfiles/               # 收集的静态文件（需手动创建）
├── requirements.txt           # 项目依赖
└── manage.py                  # Django管理脚本
```

## 首次运行注意事项

首次运行项目时，您需要：

1. 确保已创建所有必要的目录（media, staticfiles 等）
2. 在管理后台创建至少一个分类和链接，以便首页正常显示
3. 如果使用文件功能，需要创建至少一个文件夹

## 使用指南

### 管理员

1. **添加分类**：在管理后台创建链接分类
2. **添加链接**：为每个分类添加链接，设置标题、URL 和描述
3. **管理文件**：创建文件夹并上传文件
4. **用户管理**：创建和管理用户账户

### 用户

1. **浏览链接**：通过分类浏览或使用搜索功能查找链接
2. **访问文件**：浏览、下载和分享文件
3. **个人资料**：管理个人信息和部门职位

## 配置选项

主要配置文件位于 `hospital_navigator/settings.py`，可以根据需要修改以下设置：

- `DEBUG`：开发模式开关
- `ALLOWED_HOSTS`：允许访问的主机名
- `DATABASES`：数据库配置
- `STATIC_URL` 和 `MEDIA_URL`：静态文件和媒体文件 URL

## 部署指南

### 生产环境设置

1. **修改设置**

```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
SECRET_KEY = 'your-secure-key'
```

2. **配置数据库**

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'hospital_navigator',
        'USER': 'db_user',
        'PASSWORD': 'db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

3. **配置 Web 服务器**

推荐使用 Nginx + Gunicorn 部署：

```bash
# 安装Gunicorn
pip install gunicorn

# 启动Gunicorn
gunicorn hospital_navigator.wsgi:application --bind 0.0.0.0:8000
```

Nginx 配置示例：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /path/to/your/staticfiles/;
    }

    location /media/ {
        alias /path/to/your/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 常见问题

**Q: 如何生成 requirements.txt 文件?**  
A: 在激活的虚拟环境中运行 `pip freeze > requirements.txt`

**Q: 如何重置管理员密码?**  
A: 使用以下命令：`python manage.py changepassword admin`

**Q: 如何备份数据?**  
A: 使用 Django 的 dumpdata 命令：`python manage.py dumpdata > backup.json`

**Q: 如何恢复数据?**  
A: 使用 loaddata 命令：`python manage.py loaddata backup.json`

**Q: 为什么我的静态文件没有加载?**  
A: 确保运行了 `python manage.py collectstatic` 命令

**Q: 上传的文件在哪里?**  
A: 上传的文件存储在 `media/downloads/` 目录中
