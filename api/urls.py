from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'items', views.MenuItemViewSet, basename='menuitem')
router.register(r'bills', views.BillViewSet, basename='bill')

urlpatterns = [
    path('', include(router.urls)),
    path('export/', views.export_csv, name='export_csv'),
]