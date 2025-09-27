# apps/analytics/serializers.py
from rest_framework import serializers
from .models import Performance, Attendance
from employees.serializers import EmployeeListSerializer

class PerformanceSerializer(serializers.ModelSerializer):
    """Performance data serializer"""
    employee = EmployeeListSerializer(read_only=True)
    employee_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Performance
        fields = [
            'id', 'employee', 'employee_id', 'review_period',
            'overall_score', 'technical_score', 'communication_score',
            'teamwork_score', 'review_date', 'created_at'
        ]

class AttendanceSerializer(serializers.ModelSerializer):
    """Attendance data serializer"""
    employee = EmployeeListSerializer(read_only=True)
    employee_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'employee', 'employee_id', 'date',
            'check_in_time', 'check_out_time', 'total_hours',
            'status', 'created_at'
        ]

# Chart.js Data Serializers
class DepartmentStatsSerializer(serializers.Serializer):
    """Serializer for department statistics chart data"""
    labels = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField(child=serializers.IntegerField())
    colors = serializers.ListField(child=serializers.CharField())

class PerformanceTrendsSerializer(serializers.Serializer):
    """Serializer for performance trends chart data"""
    labels = serializers.ListField(child=serializers.CharField())
    datasets = serializers.ListField()

class SalaryDistributionSerializer(serializers.Serializer):
    """Serializer for salary distribution chart data"""
    labels = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField(child=serializers.FloatField())
    colors = serializers.ListField(child=serializers.CharField())

class AttendanceRatesSerializer(serializers.Serializer):
    """Serializer for attendance rates chart data"""
    labels = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField(child=serializers.FloatField())
    colors = serializers.ListField(child=serializers.CharField())

class DashboardSummarySerializer(serializers.Serializer):
    """Serializer for dashboard summary data"""
    total_employees = serializers.IntegerField()
    total_departments = serializers.IntegerField()
    average_salary = serializers.FloatField()
    average_performance = serializers.FloatField()
    attendance_rate = serializers.FloatField()
    latest_hires = serializers.ListField()

