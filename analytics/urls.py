from django.urls import path
from . import views


urlpatterns = [
    path('summary/', views.dashboard_summary, name='dashboard-summary'),
    path('departments/', views.department_stats, name='department-stats'),
    path('salary-distribution/', views.salary_distribution, name='salary-distribution'),
    path('performance-trends/', views.performance_trends, name='performance-trends'),
    path('attendance-rates/', views.attendance_rates, name='attendance-rates'),
    path('hire-timeline/', views.hire_timeline, name='hire-timeline'),
    path('export/', views.export_analytics, name='export-analytics'),
    path('dashboard/', views.dashboard_view, name='dashboard-view'),  # HTML view
]

