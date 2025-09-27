
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
import requests
import json
from .operations import AnalyticsOperations
from .serializers import (
    DashboardSummarySerializer,
    DepartmentStatsSerializer,
    SalaryDistributionSerializer,
    PerformanceTrendsSerializer,
    AttendanceRatesSerializer
)
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
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
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def export_analytics(request):
    """Export analytics data in specified format"""
    try:
        format_type = request.query_params.get('format', 'json')
        data = AnalyticsOperations.export_analytics_data(format_type)
        
        if format_type == 'csv':
            csv_data = AnalyticsOperations.export_analytics_data('csv')
            response = HttpResponse(csv_data, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="analytics_data.csv"'
            return response
        
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': 'Failed to export analytics data', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
def dashboard_view(request):
    """Render the Chart.js dashboard HTML page - requires token authentication"""
    # Check if user has a valid token in session
    token_key = request.session.get('auth_token')
    
    if not token_key:
        return redirect('analytics-login')
    
    try:
        # Verify the token is still valid
        token = Token.objects.select_related('user').get(key=token_key)
        user = token.user
        
        if not user.is_active:
            request.session.flush()
            messages.error(request, 'User account is disabled.')
            return redirect('analytics-login')
        
        context = {
            'title': 'Employee Analytics Dashboard',
            'api_base_url': '/api/analytics/',
            'user': user,
            'auth_token': token.key,
        }
        return render(request, 'analytics/dashboard.html', context)
        
    except Token.DoesNotExist:
        request.session.flush()
        return redirect('analytics-login')
    except Exception as e:
        return HttpResponse(f'Dashboard Error: {str(e)}', status=500)

@csrf_protect
def analytics_login(request):
    """Login view that calls your existing authentication API"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return render(request, 'analytics/login.html')
        
        try:
            # Call your existing authentication API
            api_url = 'http://127.0.0.1:8000/api/auth/login/'
            response = requests.post(
                api_url,
                json={
                    'username': username,
                    'password': password
                },
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    # Store token in session
                    request.session['auth_token'] = data['token']
                    request.session['user_id'] = data['user_id']
                    request.session['username'] = data['username']
                    
                    messages.success(request, f"Welcome, {data['username']}!")
                    return redirect('/api/analytics/dashboard/')
                else:
                    messages.error(request, data.get('message', 'Login failed'))
            else:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                messages.error(request, error_data.get('message', 'Invalid credentials'))
                
        except requests.RequestException as e:
            messages.error(request, 'Login service unavailable. Please try again.')
        except Exception as e:
            messages.error(request, 'An error occurred during login.')
        
        return render(request, 'analytics/login.html')
    
    # Check if already logged in
    token_key = request.session.get('auth_token')
    if token_key:
        try:
            Token.objects.get(key=token_key)
            return redirect('/api/analytics/dashboard/')
        except Token.DoesNotExist:
            request.session.flush()
    
    return render(request, 'analytics/login.html')

def analytics_logout(request):
    """Logout view that calls your existing logout API"""
    try:
        token_key = request.session.get('auth_token')
        if token_key:
            # Call your existing logout API
            logout_url = 'http://127.0.0.1:8000/api/auth/logout/'
            try:
                requests.post(
                    logout_url,
                    headers={
                        'Authorization': f'Token {token_key}',
                        'Content-Type': 'application/json'
                    },
                    timeout=5
                )
            except requests.RequestException:
                pass  # Continue with session cleanup even if API call fails
        
        # Clear session
        request.session.flush()
        messages.success(request, 'Successfully logged out.')
        return redirect('analytics-login')
        
    except Exception as e:
        messages.error(request, 'Logout failed.')
        return redirect('analytics-login')