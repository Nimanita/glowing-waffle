# apps/analytics/operations.py
from django.db.models import Count, Avg, Sum , Min, Max , Q
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Performance, Attendance
from employees.models import Employee
from departments.models import Department

class AnalyticsOperations:
    """Business logic operations for Analytics and Chart.js data"""
    
    @staticmethod
    def get_dashboard_summary():
        """Get dashboard summary statistics"""
        total_employees = Employee.objects.count()
        total_departments = Department.objects.count()
        
        # Average salary
        avg_salary = Employee.objects.aggregate(avg=Avg('salary'))['avg'] or 0
        
        # Average performance
        avg_performance = Performance.objects.aggregate(avg=Avg('overall_score'))['avg'] or 0
        
        # Attendance rate (last 30 days)
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        total_possible_days = Attendance.objects.filter(date__gte=thirty_days_ago).count()
        present_days = Attendance.objects.filter(
            date__gte=thirty_days_ago, 
            status='PRESENT'
        ).count()
        attendance_rate = (present_days / total_possible_days * 100) if total_possible_days > 0 else 0
        
        # Latest hires (last 5)
        from employees.serializers import EmployeeListSerializer
        latest_hires = Employee.objects.order_by('-hire_date')[:5]
        latest_hires_data = EmployeeListSerializer(latest_hires, many=True).data
        
        return {
            'total_employees': total_employees,
            'total_departments': total_departments,
            'average_salary': round(float(avg_salary), 2),
            'average_performance': round(float(avg_performance), 2),
            'attendance_rate': round(attendance_rate, 2),
            'latest_hires': latest_hires_data
        }
    
    @staticmethod
    def get_department_stats():
        """Get department statistics for pie chart"""
        departments = Department.objects.annotate(
            employee_count=Count('employee')
        ).order_by('-employee_count')
        
        colors = [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
            '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
        ]
        
        return {
            'labels': [dept.name for dept in departments],
            'data': [dept.employee_count for dept in departments],
            'colors': colors[:len(departments)]
        }
    
    @staticmethod
    def get_salary_distribution():
        """Get salary distribution by department for bar chart"""
        departments = Department.objects.annotate(
            avg_salary=Avg('employee__salary')
        ).filter(avg_salary__isnull=False).order_by('-avg_salary')
        
        colors = [
            '#36A2EB', '#4BC0C0', '#FF6384', '#FFCE56',
            '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
        ]
        
        return {
            'labels': [dept.name for dept in departments],
            'data': [round(float(dept.avg_salary), 2) for dept in departments],
            'colors': colors[:len(departments)]
        }
    
    @staticmethod
    def get_performance_trends():
        """Get performance trends over time for line chart"""
        # Get last 6 periods
        periods = Performance.objects.values('review_period').distinct().order_by('review_period')
        
        period_data = []
        for period in periods:
            avg_score = Performance.objects.filter(
                review_period=period['review_period']
            ).aggregate(avg=Avg('overall_score'))['avg']
            period_data.append({
                'period': period['review_period'],
                'score': round(float(avg_score), 2) if avg_score else 0
            })
        
        return {
            'labels': [item['period'] for item in period_data],
            'datasets': [{
                'label': 'Average Performance Score',
                'data': [item['score'] for item in period_data],
                'borderColor': '#36A2EB',
                'backgroundColor': 'rgba(54, 162, 235, 0.1)',
                'tension': 0.4
            }]
        }
    
    @staticmethod
    def get_attendance_rates():
        """Get attendance rates by month for doughnut chart"""
        # Get last 6 months attendance
        six_months_ago = timezone.now().date() - timedelta(days=180)
        
        monthly_data = Attendance.objects.filter(
            date__gte=six_months_ago
        ).extra({
            'month': "DATE_FORMAT(date, '%%Y-%%m')"
        }).values('month').annotate(
            total=Count('id'),
            present=Count('id', filter=Q(status='PRESENT'))
        ).order_by('month')
        
        labels = []
        data = []
        for month_data in monthly_data:
            rate = (month_data['present'] / month_data['total'] * 100) if month_data['total'] > 0 else 0
            labels.append(month_data['month'])
            data.append(round(rate, 2))
        
        colors = ['#4BC0C0', '#36A2EB', '#FF6384', '#FFCE56', '#9966FF', '#FF9F40']
        
        return {
            'labels': labels,
            'data': data,
            'colors': colors[:len(data)]
        }
    
    @staticmethod
    def get_hire_date_timeline():
        """Get hire date timeline for line chart"""
        # Group employees by hire date (monthly)
        hire_data = Employee.objects.extra({
            'month': "DATE_FORMAT(hire_date, '%%Y-%%m')"
        }).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        return {
            'labels': [item['month'] for item in hire_data],
            'datasets': [{
                'label': 'New Hires',
                'data': [item['count'] for item in hire_data],
                'borderColor': '#FF6384',
                'backgroundColor': 'rgba(255, 99, 132, 0.1)',
                'tension': 0.4
            }]
        }
    
    @staticmethod
    def get_performance_by_department():
        """Get performance scores by department"""
        dept_performance = Department.objects.annotate(
            avg_performance=Avg('employee__performance__overall_score')
        ).filter(avg_performance__isnull=False)
        
        return {
            'labels': [dept.name for dept in dept_performance],
            'data': [round(float(dept.avg_performance), 2) for dept in dept_performance],
            'colors': ['#36A2EB', '#4BC0C0', '#FF6384', '#FFCE56', '#9966FF']
        }
    
    @staticmethod
    def export_analytics_data(format_type='json'):
        """Export analytics data in specified format"""
        data = {
            'summary': AnalyticsOperations.get_dashboard_summary(),
            'department_stats': AnalyticsOperations.get_department_stats(),
            'salary_distribution': AnalyticsOperations.get_salary_distribution(),
            'performance_trends': AnalyticsOperations.get_performance_trends(),
            'attendance_rates': AnalyticsOperations.get_attendance_rates(),
            'hire_timeline': AnalyticsOperations.get_hire_date_timeline(),
            'generated_at': timezone.now().isoformat()
        }
        
        if format_type == 'csv':
            # Convert to CSV format for specific charts
            import csv
            import io
            output = io.StringIO()
            
            # Export department stats as CSV
            writer = csv.writer(output)
            writer.writerow(['Department', 'Employee Count'])
            dept_stats = data['department_stats']
            for label, count in zip(dept_stats['labels'], dept_stats['data']):
                writer.writerow([label, count])
            
            return output.getvalue()
        
        return data