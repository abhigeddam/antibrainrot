from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'), # Dashboard as home for logged in
    path('register/', views.register, name='register'),
    path('connect-telegram/', views.connect_telegram, name='connect_telegram'),
    path('api/check-connection/', views.check_connection_status, name='check_connection_status'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]
