from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from .views import product_list

urlpatterns = [
    # Trang chủ
    path('', views.home, name='home'),

    # Đăng nhập và đăng xuất
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Quản lý quyền admin
    path('assign-admin/<int:user_id>/', views.assign_admin, name='assign_admin'),

    #Thông tin cá nhân
    path('profile/',views.profile_view, name='profile_view'),

    # Diễn đàn
    path('forum/', views.forum_home, name='forum_home'),
    path('forum/post/create/', views.create_post, name='create_post'),
    path('forum/post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('forum/post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('forum/post/<int:post_id>/like/', views.toggle_like_post, name='toggle_like_post'),
    path('forum/post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('forum/post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('forum/comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('forum/comment/<int:comment_id>/like/', views.toggle_like_comment, name='toggle_like_comment'),

    

    # Thanh toán PayOS
    path('create_payment/', views.create_payment, name='create_payment'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),

    #Sản phẩm
    path('products/', product_list, name='product_list'),
]

# Phục vụ file media trong môi trường phát triển
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
