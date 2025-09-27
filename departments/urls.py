# apps/departments/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('', views.department_list_create, name='department-list-create'),           # GET list, POST create
    path('<int:pk>/', views.department_detail, name='department-detail'),           # GET/PUT/PATCH/DELETE
    path('<int:pk>/employees/', views.department_employees, name='department-employees'),  # GET employees in dept
    path('<int:pk>/statistics/', views.department_statistics, name='department-statistics'),  # GET dept stats
]
