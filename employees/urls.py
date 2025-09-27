# apps/employees/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('', views.employee_list_create, name='employee-list-create'),            # GET list, POST create
    path('<int:pk>/', views.employee_detail, name='employee-detail'),             # GET/PUT/PATCH/DELETE
    path('<int:pk>/performance/', views.employee_performance, name='employee-performance'),  # GET performance history
    path('<int:pk>/attendance/', views.employee_attendance, name='employee-attendance'),     # GET attendance history
]
