from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Min, Max
from django.shortcuts import get_object_or_404
from .models import Department
from .serializers import (
    DepartmentSerializer,
    DepartmentListSerializer, 
    DepartmentCreateSerializer,
    DepartmentUpdateSerializer
)

        # Performance statistics
from analytics.models import Performance
from django.db.models import Avg as AvgFunc

class DepartmentOperations:
    """Business logic operations for Department management"""
    
    @staticmethod
    def get_department_list(request):
        """Get paginated list of departments with search"""
        queryset = Department.objects.prefetch_related('employee_set').all()
        
        # Search functionality
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(location__icontains=search)
            )
        
        # Budget range filter
        min_budget = request.query_params.get('min_budget', None)
        max_budget = request.query_params.get('max_budget', None)
        if min_budget:
            queryset = queryset.filter(budget__gte=min_budget)
        if max_budget:
            queryset = queryset.filter(budget__lte=max_budget)
        
        # Location filter
        location = request.query_params.get('location', None)
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        # Ordering
        ordering = request.query_params.get('ordering', 'name')
        if ordering in ['name', '-name', 'budget', '-budget', 'created_at', '-created_at']:
            queryset = queryset.order_by(ordering)
        
        # Pagination
        page_size = min(int(request.query_params.get('page_size', 20)), 100)
        paginator = Paginator(queryset, page_size)
        page_number = request.query_params.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        serializer = DepartmentListSerializer(page_obj, many=True)
        
        return {
            'results': serializer.data,
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
    
    @staticmethod
    def get_department_detail(department_id):
        """Get detailed department information"""
        department = get_object_or_404(Department, id=department_id)
        serializer = DepartmentSerializer(department)
        return serializer.data
    
    @staticmethod
    def create_department(data):
        """Create new department"""
        serializer = DepartmentCreateSerializer(data=data)
        if serializer.is_valid():
            department = serializer.save()
            detail_serializer = DepartmentSerializer(department)
            return {
                'success': True,
                'data': detail_serializer.data,
                'message': 'Department created successfully'
            }
        return {
            'success': False,
            'errors': serializer.errors,
            'message': 'Department creation failed'
        }
    
    @staticmethod
    def update_department(department_id, data):
        """Update existing department"""
        department = get_object_or_404(Department, id=department_id)
        serializer = DepartmentCreateSerializer(department, data=data, partial=True)
        allowed_fields = {'budget'}
        provided_fields = set(data.keys())
        invalid_fields = provided_fields - allowed_fields
            
        if invalid_fields:
                return {
                    'success': False,
                    'errors': {
                        'invalid_fields': f"PUT requests can only update budget. Invalid fields: {', '.join(invalid_fields)}"
                    },
                    'message': 'Department update failed - only budget updates allowed '
                }
            
        serializer = DepartmentUpdateSerializer(department, data=data, partial=False)

        if serializer.is_valid():
            updated_department = serializer.save()
            detail_serializer = DepartmentSerializer(updated_department)
            return {
                'success': True,
                'data': detail_serializer.data,
                'message': 'Department updated successfully'
            }
        return {
            'success': False,
            'errors': serializer.errors,
            'message': 'Department update failed'
        }
    
    @staticmethod
    def delete_department(department_id):
        """Delete department if no employees are assigned"""
        department = get_object_or_404(Department, id=department_id)
        
        # Check if department has employees
        if department.employee_set.exists():
            return {
                'success': False,
                'message': 'Cannot delete department with existing employees'
            }
        
        department_data = DepartmentSerializer(department).data
        department.delete()
        return {
            'success': True,
            'data': department_data,
            'message': 'Department deleted successfully'
        }
    
    @staticmethod
    def get_department_employees(department_id):
        """Get all employees in a department"""
        department = get_object_or_404(Department, id=department_id)
        from employees.serializers import EmployeeListSerializer
        
        employees = department.employee_set.all().order_by('full_name')
        serializer = EmployeeListSerializer(employees, many=True)
        
        return {
            'department': DepartmentSerializer(department).data,
            'employees': serializer.data,
            'employee_count': employees.count()
        }
    
    @staticmethod
    def get_department_statistics(department_id):
        """Get department statistics"""
        department = get_object_or_404(Department, id=department_id)
        employees = department.employee_set.all()
        
        stats = {
            'department': DepartmentSerializer(department).data,
            'employee_count': employees.count(),
            'average_salary': employees.aggregate(avg_salary=Avg('salary'))['avg_salary'] or 0,
            'salary_range': {
                'min': employees.aggregate(min_salary=Min('salary'))['min_salary'] or 0,
                'max': employees.aggregate(max_salary=Max('salary'))['max_salary'] or 0
            },
            'positions': list(employees.values_list('position', flat=True).distinct()),
        }
        
        
        performances = Performance.objects.filter(employee__department=department)
        if performances.exists():
            stats['performance_stats'] = {
                'average_overall': performances.aggregate(avg=AvgFunc('overall_score'))['avg'],
                'average_technical': performances.aggregate(avg=AvgFunc('technical_score'))['avg'],
                'average_communication': performances.aggregate(avg=AvgFunc('communication_score'))['avg'],
                'average_teamwork': performances.aggregate(avg=AvgFunc('teamwork_score'))['avg'],
            }
        
        return stats