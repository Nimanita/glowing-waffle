# apps/departments/views.py
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .operations import DepartmentOperations
from .serializers import (
    DepartmentSerializer,
    DepartmentListSerializer,
    DepartmentCreateSerializer,
    DepartmentUpdateSerializer
)

# Swagger parameter definitions
dept_search_param = openapi.Parameter('search', openapi.IN_QUERY, description="Search in name, code, location", type=openapi.TYPE_STRING)
min_budget_param = openapi.Parameter('min_budget', openapi.IN_QUERY, description="Minimum budget filter", type=openapi.TYPE_NUMBER)
max_budget_param = openapi.Parameter('max_budget', openapi.IN_QUERY, description="Maximum budget filter", type=openapi.TYPE_NUMBER)
location_param = openapi.Parameter('location', openapi.IN_QUERY, description="Filter by location", type=openapi.TYPE_STRING)
dept_ordering_param = openapi.Parameter('ordering', openapi.IN_QUERY, description="Order by: name, -name, budget, -budget, created_at, -created_at", type=openapi.TYPE_STRING)
dept_page_param = openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER)
dept_page_size_param = openapi.Parameter('page_size', openapi.IN_QUERY, description="Items per page (max 100)", type=openapi.TYPE_INTEGER)

@swagger_auto_schema(
    method='get',
    operation_description='Get paginated list of departments with search and filtering options',
    manual_parameters=[dept_search_param, min_budget_param, max_budget_param, location_param, dept_ordering_param, dept_page_param, dept_page_size_param],
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
    tags=['Departments']
)
@swagger_auto_schema(
    method='post',
    operation_description='Create a new department',
    request_body=DepartmentCreateSerializer,
    responses={
        201: openapi.Response('Department created successfully', DepartmentSerializer),
        400: 'Bad Request - Validation errors'
    },
    tags=['Departments']
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def department_list_create(request):
    """
    GET: List all departments with pagination, search, and filtering
    POST: Create a new department
    """
    if request.method == 'GET':
        try:
            data = DepartmentOperations.get_department_list(request)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': 'Failed to retrieve departments', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    elif request.method == 'POST':
        try:
            result = DepartmentOperations.create_department(request.data)
            if result['success']:
                return Response(result, status=status.HTTP_201_CREATED)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': 'Failed to create department', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@swagger_auto_schema(
    method='get',
    operation_description='Get detailed information about a specific department',
    responses={
        200: DepartmentSerializer,
        404: 'Department not found'
    },
    tags=['Departments']
)
@swagger_auto_schema(
    method='put',
    operation_description='Update department information',
    request_body=DepartmentUpdateSerializer,
    responses={
        200: openapi.Response('Department updated successfully', DepartmentSerializer),
        400: 'Bad Request - Validation errors',
        404: 'Department not found'
    },
    tags=['Departments']
)
@swagger_auto_schema(
    method='delete',
    operation_description='Delete a department (only if no employees are assigned)',
    responses={
        200: 'Department deleted successfully',
        400: 'Cannot delete department with existing employees',
        404: 'Department not found'
    },
    tags=['Departments']
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def department_detail(request, pk):
    """
    GET: Retrieve department details
    PUT/PATCH: Update department
    DELETE: Delete department
    """
    if request.method == 'GET':
        try:
            data = DepartmentOperations.get_department_detail(pk)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': 'Department not found', 'detail': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
    
    elif request.method == 'PUT':
        try:
            result = DepartmentOperations.update_department(pk, request.data)
            if result['success']:
                return Response(result, status=status.HTTP_200_OK)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': 'Failed to update department', 'detail': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
    
    elif request.method == 'DELETE':
        try:
            result = DepartmentOperations.delete_department(pk)
            if result['success']:
                return Response(result, status=status.HTTP_200_OK)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': 'Failed to delete department', 'detail': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

@swagger_auto_schema(
    method='get',
    operation_description='Get all employees in a department',
    responses={
        200: openapi.Response('Department employees retrieved successfully'),
        404: 'Department not found'
    },
    tags=['Departments']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def department_employees(request, pk):
    """Get all employees in a department"""
    try:
        data = DepartmentOperations.get_department_employees(pk)
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': 'Department not found', 'detail': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )

@swagger_auto_schema(
    method='get',
    operation_description='Get department statistics including salary and performance data',
    responses={
        200: openapi.Response('Department statistics retrieved successfully'),
        404: 'Department not found'
    },
    tags=['Departments']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def department_statistics(request, pk):
    """Get department statistics"""
    try:
        data = DepartmentOperations.get_department_statistics(pk)
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': 'Department not found', 'detail': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )