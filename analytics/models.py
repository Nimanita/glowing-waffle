# apps/analytics/models.py
from django.db import models
from employees.models import Employee

class Performance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    review_period = models.CharField(max_length=20)
    overall_score = models.DecimalField(max_digits=3, decimal_places=2)
    technical_score = models.DecimalField(max_digits=3, decimal_places=2)
    communication_score = models.DecimalField(max_digits=3, decimal_places=2)
    teamwork_score = models.DecimalField(max_digits=3, decimal_places=2)
    review_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    check_in_time = models.TimeField()
    check_out_time = models.TimeField(null=True, blank=True)
    total_hours = models.DecimalField(max_digits=4, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PRESENT')
    created_at = models.DateTimeField(auto_now_add=True)

