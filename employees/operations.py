# apps/employees/operations.py
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.db import DatabaseError, IntegrityError
from rest_framework.response import Response
from rest_framework import status
import traceback
import logging

from .models import Employee
from .serializers import (
    EmployeeListSerializer, 
    EmployeeDetailSerializer,
    EmployeeCreateSerializer,
    EmployeeUpdateSerializer,
    EmployeePerformanceListSerializer,
    EmployeeAttendanceListSerializer
)

logger = logging.getLogger(__name__)


class EmployeeOperations:
    """Business logic operations for Employee management"""
    
    @staticmethod
    def get_employee_list(request):
        """Get paginated list of employees with search and filter"""
        try:
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
                try:
                    queryset = queryset.filter(department_id=int(department_id))
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid department_id: {department_id}. Error: {str(e)}")
                    logger.warning(traceback.format_exc())
            
            # Salary range filter
            min_salary = request.query_params.get('min_salary', None)
            max_salary = request.query_params.get('max_salary', None)
            if min_salary:
                try:
                    queryset = queryset.filter(salary__gte=float(min_salary))
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid min_salary: {min_salary}. Error: {str(e)}")
                    logger.warning(traceback.format_exc())
            if max_salary:
                try:
                    queryset = queryset.filter(salary__lte=float(max_salary))
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid max_salary: {max_salary}. Error: {str(e)}")
                    logger.warning(traceback.format_exc())
            
            # Ordering
            ordering = request.query_params.get('ordering', 'full_name')
            if ordering in ['full_name', '-full_name', 'salary', '-salary', 'hire_date', '-hire_date']:
                queryset = queryset.order_by(ordering)
            
            # Pagination
            try:
                page_size = min(int(request.query_params.get('page_size', 20)), 100)
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid page_size, using default 20. Error: {str(e)}")
                page_size = 20
                
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
            
        except DatabaseError as e:
            logger.error(f"Database error in get_employee_list: {str(e)}")
            logger.error(traceback.format_exc())
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_employee_list: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    @staticmethod
    def get_employee_detail(employee_id):
        """Get detailed employee information"""
        try:
            employee = get_object_or_404(Employee, id=employee_id)
            serializer = EmployeeDetailSerializer(employee)
            return serializer.data
            
        except Employee.DoesNotExist as e:
            logger.error(f"Employee not found with id {employee_id}: {str(e)}")
            logger.error(traceback.format_exc())
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_employee_detail: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    @staticmethod
    def create_employee(data):
        """Create new employee"""
        try:
            serializer = EmployeeCreateSerializer(data=data)
            if serializer.is_valid():
                try:
                    employee = serializer.save()
                    detail_serializer = EmployeeDetailSerializer(employee)
                    return {
                        'success': True,
                        'data': detail_serializer.data,
                        'message': 'Employee created successfully'
                    }
                except IntegrityError as e:
                    logger.error(f"Integrity error creating employee: {str(e)}")
                    logger.error(traceback.format_exc())
                    return {
                        'success': False,
                        'errors': {'database': 'Employee with this employee_id or email may already exist'},
                        'message': 'Employee creation failed'
                    }
                except DatabaseError as e:
                    logger.error(f"Database error creating employee: {str(e)}")
                    logger.error(traceback.format_exc())
                    return {
                        'success': False,
                        'errors': {'database': str(e)},
                        'message': 'Employee creation failed'
                    }
                    
            return {
                'success': False,
                'errors': serializer.errors,
                'message': 'Employee creation failed'
            }
            
        except Exception as e:
            logger.error(f"Unexpected error in create_employee: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'errors': {'unexpected': str(e)},
                'message': 'Employee creation failed due to unexpected error'
            }
    
    @staticmethod
    def update_employee(employee_id, data):
        """Update existing employee"""
        try:
            employee = get_object_or_404(Employee, id=employee_id)
            
            # Validate that only allowed fields are provided
            allowed_fields = {'position', 'department', 'salary'}
            provided_fields = set(data.keys())
            invalid_fields = provided_fields - allowed_fields
            
            if invalid_fields:
                logger.warning(f"Invalid fields provided for employee update: {invalid_fields}")
                return {
                    'success': False,
                    'errors': {
                        'invalid_fields': f"Only position, department, and salary can be updated. Invalid fields: {', '.join(invalid_fields)}"
                    },
                    'message': 'Employee update failed - invalid fields provided'
                }
                
            serializer = EmployeeUpdateSerializer(employee, data=data, partial=True)
            if serializer.is_valid():
                try:
                    updated_employee = serializer.save()
                    detail_serializer = EmployeeDetailSerializer(updated_employee)
                    return {
                        'success': True,
                        'data': detail_serializer.data,
                        'message': 'Employee updated successfully'
                    }
                except DatabaseError as e:
                    logger.error(f"Database error updating employee: {str(e)}")
                    logger.error(traceback.format_exc())
                    return {
                        'success': False,
                        'errors': {'database': str(e)},
                        'message': 'Employee update failed'
                    }
                    
            return {
                'success': False,
                'errors': serializer.errors,
                'message': 'Employee update failed'
            }
            
        except Employee.DoesNotExist as e:
            logger.error(f"Employee not found with id {employee_id}: {str(e)}")
            logger.error(traceback.format_exc())
            raise
        except Exception as e:
            logger.error(f"Unexpected error in update_employee: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'errors': {'unexpected': str(e)},
                'message': 'Employee update failed due to unexpected error'
            }
    
    @staticmethod
    def delete_employee(employee_id):
        """Delete employee"""
        try:
            employee = get_object_or_404(Employee, id=employee_id)
            
            try:
                employee_data = EmployeeDetailSerializer(employee).data
                employee.delete()
                return {
                    'success': True,
                    'data': employee_data,
                    'message': 'Employee deleted successfully'
                }
            except DatabaseError as e:
                logger.error(f"Database error deleting employee: {str(e)}")
                logger.error(traceback.format_exc())
                return {
                    'success': False,
                    'message': 'Failed to delete employee due to database error'
                }
                
        except Employee.DoesNotExist as e:
            logger.error(f"Employee not found with id {employee_id}: {str(e)}")
            logger.error(traceback.format_exc())
            raise
        except Exception as e:
            logger.error(f"Unexpected error in delete_employee: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'message': f'Employee deletion failed: {str(e)}'
            }
    
    @staticmethod
    def get_employee_performance(employee_id):
        """Get employee performance history"""
        try:
            employee = get_object_or_404(Employee.objects.select_related('department'), id=employee_id)
            from analytics.models import Performance
            from analytics.serializers import PerformanceSerializerForEmployeeModel
            
            try:
                performances = Performance.objects.filter(employee=employee).order_by('-review_date')
                serializer = PerformanceSerializerForEmployeeModel(performances, many=True)
                
                return {
                    'employee_id': employee.id,
                    'employee_name': employee.full_name,
                    'department': employee.department.name,
                    'performances': serializer.data,
                    'performance_count': performances.count()
                }
            except Exception as e:
                logger.error(f"Error fetching performance data: {str(e)}")
                logger.error(traceback.format_exc())
                raise
                
        except Employee.DoesNotExist as e:
            logger.error(f"Employee not found with id {employee_id}: {str(e)}")
            logger.error(traceback.format_exc())
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_employee_performance: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    @staticmethod
    def get_employee_attendance(employee_id, days=30):
        """Get employee attendance history"""
        try:
            from datetime import datetime, timedelta
            from django.utils import timezone
            
            employee = get_object_or_404(Employee.objects.select_related('department'), id=employee_id)
            from analytics.models import Attendance
            from analytics.serializers import AttendanceSerializerForEmployeeModel
            
            try:
                end_date = timezone.now().date()
                start_date = end_date - timedelta(days=days)
                
                attendance_records = Attendance.objects.filter(
                    employee=employee,
                    date__range=[start_date, end_date]
                ).order_by('-date')
                
                serializer = AttendanceSerializerForEmployeeModel(attendance_records, many=True)
                
                return {
                    'employee_id': employee.id,
                    'employee_name': employee.full_name,
                    'department': employee.department.name,
                    'attendance_records': serializer.data,
                    'period': f'{start_date} to {end_date}',
                    'total_records': attendance_records.count()
                }
            except Exception as e:
                logger.error(f"Error fetching attendance data: {str(e)}")
                logger.error(traceback.format_exc())
                raise
                
        except Employee.DoesNotExist as e:
            logger.error(f"Employee not found with id {employee_id}: {str(e)}")
            logger.error(traceback.format_exc())
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_employee_attendance: {str(e)}")
            logger.error(traceback.format_exc())
            raise