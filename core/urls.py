from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('qr/', views.qr_base64, name='qr_base64'),
    path('auth/login', views.login_view, name='login'),
    path('auth/logout', views.logout_view, name='logout'),
    path('auth/me', views.me, name='me'),
]