"""
URL configuration for Blog_2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, re_path, include
from blog import views as blog_views
from register import views as register_views
from room import views as room_views
from django.contrib.auth.views import LoginView

urlpatterns = [
    #re_path(r'^post/(.*)$', blog_views.post), #using regex pattern
    path('post/<slug:slug>/', blog_views.post), #without regex
    path('all_posts/', blog_views.all_posts),
    path('', blog_views.home, name='home'),
    #path('', blog_views.index),
    path('writer_panel/', blog_views.writer_panel, name='writer_panel'),
    path('editor_panel/', blog_views.editor_panel, name='editor_panel'),
    path('profile/', blog_views.profile, name='profile'),
    path('voting/', blog_views.voting, name='voting'),
    path('admin/', admin.site.urls),
    path('settings/', blog_views.settings, name='settings'),
    path('admin_tools_stats/', include('admin_tools_stats.urls')),
    path('register/', include('register.urls')),
    path('photo/upload/', room_views.photo_upload, name='photo_upload'),
    path('', include("django.contrib.auth.urls")),
    path('login/', LoginView.as_view(template_name='./registration/login.html'), name='login'),
    path('upload-file/', blog_views.upload_file, name='upload_file'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

