# apps/employees/serializers.py
from rest_framework import serializers
from .models import Employee
from departments.serializers import DepartmentSerializer

class EmployeeListSerializer(serializers.ModelSerializer):
    """Serializer for employee list view with minimal fields"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'full_name', 'email', 
            'department_name', 'position', 'salary', 'hire_date'
        ]

class EmployeeDetailSerializer(serializers.ModelSerializer):
    """Serializer for employee detail view with all fields"""
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'full_name', 'email',
            'department', 'department_id', 'position', 
            'salary', 'hire_date', 'created_at'
        ]

class EmployeeCreateSerializer(serializers.ModelSerializer):
    """Serializer for employee creation"""
    
    class Meta:
        model = Employee
        fields = [
            'employee_id', 'full_name', 'email',
            'department', 'position', 'salary', 'hire_date'
        ]
    
    def validate_employee_id(self, value):
        if Employee.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError("Employee ID already exists.")
        return value
    
    def validate_email(self, value):
        if Employee.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

class EmployeeUpdateSerializer(serializers.ModelSerializer):
    """Serializer for employee updates"""
    
    class Meta:
        model = Employee
        fields = [
           'department', 
            'position', 'salary'
        ]
    
    def validate_email(self, value):
        instance = self.instance
        if Employee.objects.filter(email=value).exclude(id=instance.id).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

class EmployeePerformanceListSerializer(serializers.Serializer):
    """Minimal serializer for performance data in employee context"""
    id = serializers.IntegerField()
    review_date = serializers.DateField()
    overall_score = serializers.DecimalField(max_digits=3, decimal_places=2)
    technical_score = serializers.DecimalField(max_digits=3, decimal_places=2)
    communication_score = serializers.DecimalField(max_digits=3, decimal_places=2)
    teamwork_score = serializers.DecimalField(max_digits=3, decimal_places=2)
    review_period = serializers.CharField()

class EmployeeAttendanceListSerializer(serializers.Serializer):
    """Minimal serializer for attendance data in employee context"""
    id = serializers.IntegerField()
    date = serializers.DateField()
    check_in_time = serializers.TimeField()
    check_out_time = serializers.TimeField()
    status = serializers.CharField()
    total_hours = serializers.DecimalField(max_digits=4, decimal_places=2)