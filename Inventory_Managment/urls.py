"""Inventory_Managment URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from Inventory_mgmt import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home,),
    path('all/', views.all,),
    path('', include('django.contrib.auth.urls'),),
    path('add_item/', views.add_item, name='add_item',),
    path('view_item/<int:id>/', views.view_item, name='view_item',),
    path('view_item/', views.view_item,),
    path('edit_item/<int:id>/', views.edit_item, name='edit_item',),
    path('vendors/<str:vendor>/', views.vendors, name='vendors',),
    path('vendors/', views.vendors,),
    path('groups/', views.groups,),
    path('groups/<str:group>/', views.groups, name='groups',),
    path('usecases/', views.usecases,),
    path('usecases/<str:usecase>/', views.usecases, name='usecases',),
    path('locations/', views.locations,),
    path('locations/<str:location>/', views.locations, name='locations',),
    path('search/<str:full_id>/', views.search, name='search',),
    path('search/', views.search,),
    path('login_user/', views.login_user, name='login',),
    path('logout_user/', views.logout_user, name='logout',),
    path('api/<str:api_key>/', views.api, name='api'),
    path('api/', views.api),
    path('settings/', views.user_settings, name='user_settings'),
    path('settings/register-device/<str:device_name>/<str:os>/', views.register_device, name='register_device'),
    path('settings/register-printserver/', views.register_printserver, name='register_printserver'),
    path('remote-print/', views.remote_print, name='remote_print',),
    path('i18n/', include('django.conf.urls.i18n')),



]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
