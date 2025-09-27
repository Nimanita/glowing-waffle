from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.get_auth_token, name='login'),
    path('logout/', views.logout, name='logout'),
    path('verify-token/', views.verify_token, name='verify-token'),
]