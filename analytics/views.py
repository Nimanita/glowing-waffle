
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import json
from .operations import AnalyticsOperations
from .serializers import (
    DashboardSummarySerializer,
    DepartmentStatsSerializer,
    SalaryDistributionSerializer,
    PerformanceTrendsSerializer,
    AttendanceRatesSerializer
)

@swagger_auto_schema(
    method='get',
    operation_description='Get dashboard summary statistics including total employees, departments, average salary, performance, and attendance rate',
    responses={
        200: DashboardSummarySerializer,
        500: 'Internal Server Error'
    },
    tags=['Analytics']
)
@api_view(['GET'])
#@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def dashboard_summary(request):
    """Get dashboard summary statistics"""
    try:
        data = AnalyticsOperations.get_dashboard_summary()
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': 'Failed to retrieve dashboard summary', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@swagger_auto_schema(
    method='get',
    operation_description='Get employee count by department for pie chart visualization',
    responses={
        200: DepartmentStatsSerializer,
        500: 'Internal Server Error'
    },
    tags=['Analytics']
)
@api_view(['GET'])
#@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def department_stats(request):
    """Get department statistics for Chart.js pie chart"""
    try:
        data = AnalyticsOperations.get_department_stats()
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': 'Failed to retrieve department statistics', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@swagger_auto_schema(
    method='get',
    operation_description='Get average salary by department for bar chart visualization',
    responses={
        200: SalaryDistributionSerializer,
        500: 'Internal Server Error'
    },
    tags=['Analytics']
)
@api_view(['GET'])
#@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def salary_distribution(request):
    """Get salary distribution by department for Chart.js bar chart"""
    try:
        data = AnalyticsOperations.get_salary_distribution()
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': 'Failed to retrieve salary distribution', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@swagger_auto_schema(
    method='get',
    operation_description='Get performance trends over time for line chart visualization',
    responses={
        200: PerformanceTrendsSerializer,
        500: 'Internal Server Error'
    },
    tags=['Analytics']
)
@api_view(['GET'])
#@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def performance_trends(request):
    """Get performance trends over time for Chart.js line chart"""
    try:
        data = AnalyticsOperations.get_performance_trends()
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': 'Failed to retrieve performance trends', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@swagger_auto_schema(
    method='get',
    operation_description='Get monthly attendance rates for doughnut chart visualization',
    responses={
        200: AttendanceRatesSerializer,
        500: 'Internal Server Error'
    },
    tags=['Analytics']
)
@api_view(['GET'])
#@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def attendance_rates(request):
    """Get attendance rates by month for Chart.js doughnut chart"""
    try:
        data = AnalyticsOperations.get_attendance_rates()
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': 'Failed to retrieve attendance rates', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@swagger_auto_schema(
    method='get',
    operation_description='Get hire date timeline for line chart visualization',
    responses={
        200: openapi.Response('Hire date timeline data'),
        500: 'Internal Server Error'
    },
    tags=['Analytics']
)
@api_view(['GET'])
#@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def hire_timeline(request):
    """Get hire date timeline for Chart.js line chart"""
    try:
        data = AnalyticsOperations.get_hire_date_timeline()
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': 'Failed to retrieve hire timeline', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@swagger_auto_schema(
    method='get',
    operation_description='Export analytics data in JSON or CSV format',
    manual_parameters=[
        openapi.Parameter('format', openapi.IN_QUERY, description="Export format: json or csv", type=openapi.TYPE_STRING, enum=['json', 'csv'])
    ],
    responses={
        200: 'Analytics data exported successfully',
        500: 'Internal Server Error'
    },
    tags=['Analytics']
)
@api_view(['GET'])
#@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def export_analytics(request):
    """Export analytics data in specified format"""
    try:
        format_type = request.query_params.get('format', 'json')
        data = AnalyticsOperations.export_analytics_data(format_type)
        
        if format_type == 'csv':
            response = HttpResponse(data, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="analytics_data.csv"'
            return response
        
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': 'Failed to export analytics data', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Dashboard HTML View (Non-API)
def dashboard_view(request):
    """Render the Chart.js dashboard HTML page"""
    try:
        # Pre-fetch data for initial render (optional)
        context = {
            'title': 'Employee Analytics Dashboard',
            'api_base_url': '/api/analytics/',
        }
        return render(request, 'analytics/dashboard.html', context)
    except Exception as e:
        return HttpResponse(f'Dashboard Error: {str(e)}', status=500)