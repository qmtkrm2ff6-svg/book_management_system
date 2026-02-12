from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from books.views import BookViewSet, RegisterView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from books.views import book_list_page # 导入刚才写的函数
from books.views import book_list_page, borrow_book_web,return_book_web,index_portal
from django.contrib.auth import views as auth_views  # 必须加上这一行
from books.views import my_borrow_history # 记得导入
from books.views import register_view



# 1. 初始化路由器
router = DefaultRouter()
# 这里的注册会自动生成 /api/books/ 和 /api/books/{pk}/ 路径
router.register(r'books', BookViewSet, basename='book')

# 2. 配置 Swagger
schema_view = get_schema_view(
   openapi.Info(
      title="图书管理系统 API", 
      default_version='v1',
      description="包含图书 CRUD、借还逻辑及用户注册登录功能",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # 核心 API 路径
    path('api/', include(router.urls)), 
    
    # 身份认证相关
    path('api/register/', RegisterView.as_view(), name='auth_register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Swagger 文档路径
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    
    # DRF 浏览器端登录（可选，主要用于调试）
    path('api-auth/', include('rest_framework.urls')),
    path('', index_portal, name='index'),
    path('web/books/', book_list_page, name='book-list-web'),
    path('web/books/<int:pk>/borrow/', borrow_book_web, name='borrow-book-web'),
    path('web/books/<int:pk>/return/', return_book_web, name='return-book-web'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('web/history/', my_borrow_history, name='borrow-history'),
    path('web/register/', register_view, name='register'),





]