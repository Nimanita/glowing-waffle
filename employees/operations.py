# apps/employees/operations.py
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from .models import Employee
from .serializers import (
    EmployeeListSerializer, 
    EmployeeDetailSerializer,
    EmployeeCreateSerializer,
    EmployeeUpdateSerializer,
    EmployeePerformanceListSerializer,
    EmployeeAttendanceListSerializer
)

class EmployeeOperations:
    """Business logic operations for Employee management"""
    
    @staticmethod
    def get_employee_list(request):
        """Get paginated list of employees with search and filter"""
        queryset = Employee.objects.select_related('department').all()
        
        # Search functionality
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) |
                Q(email__icontains=search) |
                Q(employee_id__icontains=search) |
                Q(position__icontains=search)
            )
        
        # Department filter
        department_id = request.query_params.get('department', None)
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        
        # Salary range filter
        min_salary = request.query_params.get('min_salary', None)
        max_salary = request.query_params.get('max_salary', None)
        if min_salary:
            queryset = queryset.filter(salary__gte=min_salary)
        if max_salary:
            queryset = queryset.filter(salary__lte=max_salary)
        
        # Ordering
        ordering = request.query_params.get('ordering', 'full_name')
        if ordering in ['full_name', '-full_name', 'salary', '-salary', 'hire_date', '-hire_date']:
            queryset = queryset.order_by(ordering)
        
        # Pagination
        page_size = min(int(request.query_params.get('page_size', 20)), 100)
        paginator = Paginator(queryset, page_size)
        page_number = request.query_params.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        serializer = EmployeeListSerializer(page_obj, many=True)
        
        return {
            'results': serializer.data,
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
    
    @staticmethod
    def get_employee_detail(employee_id):
        """Get detailed employee information"""
        employee = get_object_or_404(Employee, id=employee_id)
        serializer = EmployeeDetailSerializer(employee)
        return serializer.data
    
    @staticmethod
    def create_employee(data):
        """Create new employee"""
        serializer = EmployeeCreateSerializer(data=data)
        if serializer.is_valid():
            employee = serializer.save()
            detail_serializer = EmployeeDetailSerializer(employee)
            return {
                'success': True,
                'data': detail_serializer.data,
                'message': 'Employee created successfully'
            }
        return {
            'success': False,
            'errors': serializer.errors,
            'message': 'Employee creation failed'
        }
    
    @staticmethod
    def update_employee(employee_id, data):
        """Update existing employee"""
        employee = get_object_or_404(Employee, id=employee_id)
        # Validate that only allowed fields are provided
        allowed_fields = {'position', 'department', 'salary'}
        provided_fields = set(data.keys())
        invalid_fields = provided_fields - allowed_fields
        
        if invalid_fields:
            return {
                'success': False,
                'errors': {
                    'invalid_fields': f"Only position, department, and salary can be updated. Invalid fields: {', '.join(invalid_fields)}"
                },
                'message': 'Employee update failed - invalid fields provided'
            }
            
        serializer = EmployeeUpdateSerializer(employee, data=data, partial=True)
        if serializer.is_valid():
            updated_employee = serializer.save()
            detail_serializer = EmployeeDetailSerializer(updated_employee)
            return {
                'success': True,
                'data': detail_serializer.data,
                'message': 'Employee updated successfully'
            }
        return {
            'success': False,
            'errors': serializer.errors,
            'message': 'Employee update failed'
        }
    
    @staticmethod
    def delete_employee(employee_id):
        """Delete employee"""
        employee = get_object_or_404(Employee, id=employee_id)
        employee_data = EmployeeDetailSerializer(employee).data
        employee.delete()
        return {
            'success': True,
            'data': employee_data,
            'message': 'Employee deleted successfully'
        }
    
    @staticmethod
    def get_employee_performance(employee_id):
        """Get employee performance history"""
        employee = get_object_or_404(Employee.objects.select_related('department'), id=employee_id)
        from analytics.models import Performance
        from analytics.serializers import PerformanceSerializer
        
        performances = Performance.objects.filter(employee=employee).order_by('-review_date')
        serializer = PerformanceSerializer(performances, many=True)
        
        return {
            'employee_id': employee.id,
            'employee_name': employee.full_name,
            'department': employee.department.name,
            'performances': serializer.data,
            'performance_count': performances.count()
        }
    
    @staticmethod
    def get_employee_attendance(employee_id, days=30):
        """Get employee attendance history"""
        from datetime import datetime, timedelta
        from django.utils import timezone
        employee = get_object_or_404(Employee.objects.select_related('department'), id=employee_id)
        from analytics.models import Attendance
        from analytics.serializers import AttendanceSerializer
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        attendance_records = Attendance.objects.filter(
            employee=employee,
            date__range=[start_date, end_date]
        ).order_by('-date')
        
        serializer = AttendanceSerializer(attendance_records, many=True)
        
        return {
            'employee_id': employee.id,
            'employee_name': employee.full_name,
            'department': employee.department.name,
            'attendance_records': serializer.data,
            'period': f'{start_date} to {end_date}',
            'total_records': attendance_records.count()
        }