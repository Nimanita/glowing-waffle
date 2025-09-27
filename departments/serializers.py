# apps/departments/serializers.py
from rest_framework import serializers
from .models import Department

class DepartmentSerializer(serializers.ModelSerializer):
    """Standard department serializer"""
    employee_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = [
            'id', 'name', 'code', 'budget', 
            'location', 'employee_count', 'created_at'
        ]
    
    def get_employee_count(self, obj):
        return obj.employee_set.count()

class DepartmentListSerializer(serializers.ModelSerializer):
    """Minimal department serializer for lists"""
    employee_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'location', 'employee_count']
    
    def get_employee_count(self, obj):
        return obj.employee_set.count()

class DepartmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for department creation"""
    
    class Meta:
        model = Department
        fields = ['name', 'code', 'budget', 'location']
    
    def validate_name(self, value):
        if Department.objects.filter(name=value).exists():
            raise serializers.ValidationError("Department name already exists.")
        return value
    
    def validate_code(self, value):
        if Department.objects.filter(code=value).exists():
            raise serializers.ValidationError("Department code already exists.")
        return value

class DepartmentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for budget-only updates"""
    
    class Meta:
        model = Department
        fields = ['budget']
    
    def validate_budget(self, value):
        if value <= 0:
            raise serializers.ValidationError("Budget must be greater than 0.")
        return value