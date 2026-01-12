# apps/employees/views.py
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .operations import EmployeeOperations
from .serializers import (
    EmployeeListSerializer, 
    EmployeeDetailSerializer,
    EmployeeCreateSerializer,
    EmployeeUpdateSerializer
)

# Swagger parameter definitions
search_param = openapi.Parameter('search', openapi.IN_QUERY, description="Search in name, email, employee_id, position", type=openapi.TYPE_STRING)
department_param = openapi.Parameter('department', openapi.IN_QUERY, description="Filter by department ID", type=openapi.TYPE_INTEGER)
min_salary_param = openapi.Parameter('min_salary', openapi.IN_QUERY, description="Minimum salary filter", type=openapi.TYPE_NUMBER)
max_salary_param = openapi.Parameter('max_salary', openapi.IN_QUERY, description="Maximum salary filter", type=openapi.TYPE_NUMBER)
ordering_param = openapi.Parameter('ordering', openapi.IN_QUERY, description="Order by: full_name, -full_name, salary, -salary, hire_date, -hire_date", type=openapi.TYPE_STRING)
page_param = openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER)
page_size_param = openapi.Parameter('page_size', openapi.IN_QUERY, description="Items per page (max 100)", type=openapi.TYPE_INTEGER)

@swagger_auto_schema(
    method='get',
    operation_description='Get paginated list of employees with search and filtering options',
    manual_parameters=[search_param, department_param, min_salary_param, max_salary_param, ordering_param, page_param, page_size_param],
    responses={
        200: openapi.Response('Success', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                'num_pages': openapi.Schema(type=openapi.TYPE_INTEGER),
                'current_page': openapi.Schema(type=openapi.TYPE_INTEGER),
                'has_next': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'has_previous': openapi.Schema(type=openapi.TYPE_BOOLEAN),
            }
        ))
    },
    tags=['Employees']
)
@swagger_auto_schema(
    method='post',
    operation_description='Create a new employee',
    request_body=EmployeeCreateSerializer,
    responses={
        201: openapi.Response('Employee created successfully', EmployeeDetailSerializer),
        400: 'Bad Request - Validation errors'
    },
    tags=['Employees']
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def employee_list_create(request):
    """
    GET: List all employees with pagination, search, and filtering
    POST: Create a new employee
    """
    if request.method == 'GET':
        try:
            data = EmployeeOperations.get_employee_list(request)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': 'Failed to retrieve employees', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    elif request.method == 'POST':
        try:
            result = EmployeeOperations.create_employee(request.data)
            if result['success']:
                return Response(result, status=status.HTTP_201_CREATED)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': 'Failed to create employee', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@swagger_auto_schema(
    method='get',
    operation_description='Get detailed information about a specific employee',
    responses={
        200: EmployeeDetailSerializer,
        404: 'Employee not found'
    },
    tags=['Employees']
)
@swagger_auto_schema(
    method='put',
    operation_description='Update employee information',
    request_body=EmployeeUpdateSerializer,
    responses={
        200: openapi.Response('Employee updated successfully', EmployeeDetailSerializer),
        400: 'Bad Request - Validation errors',
        404: 'Employee not found'
    },
    tags=['Employees']
)
@swagger_auto_schema(
    method='delete',
    operation_description='Delete an employee',
    responses={
        200: 'Employee deleted successfully',
        404: 'Employee not found'
    },
    tags=['Employees']
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def employee_detail(request, pk):
    """
    GET: Retrieve employee details
    PUT/PATCH: Update employee
    DELETE: Delete employee
    """
    if request.method == 'GET':
        try:
            data = EmployeeOperations.get_employee_detail(pk)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': 'Employee not found', 'detail': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
    
    elif request.method == 'PUT':
        try:
            result = EmployeeOperations.update_employee(pk, request.data)
            if result['success']:
                return Response(result, status=status.HTTP_200_OK)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': 'Failed to update employee', 'detail': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
    
    elif request.method == 'DELETE':
        try:
            result = EmployeeOperations.delete_employee(pk)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': 'Failed to delete employee', 'detail': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

@swagger_auto_schema(
    method='get',
    operation_description='Get employee performance history',
    responses={
        200: openapi.Response('Performance history retrieved successfully'),
        404: 'Employee not found'
    },
    tags=['Employees']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def employee_performance(request, pk):
    """Get employee performance history"""
    try:
        data = EmployeeOperations.get_employee_performance(pk)
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': 'Employee not found', 'detail': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )

@swagger_auto_schema(
    method='get',
    operation_description='Get employee attendance history',
    manual_parameters=[
        openapi.Parameter('days', openapi.IN_QUERY, description="Number of days to fetch (default: 30)", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: openapi.Response('Attendance history retrieved successfully'),
        404: 'Employee not found'
    },
    tags=['Employees']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def employee_attendance(request, pk):
    """Get employee attendance history"""
    try:
        days = int(request.query_params.get('days', 30))
        data = EmployeeOperations.get_employee_attendance(pk, days)
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': 'Employee not found', 'detail': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
