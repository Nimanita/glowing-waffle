# apps/departments/tests.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from unittest.mock import patch, Mock

from .models import Department
from employees.models import Employee
from analytics.models import Performance, Attendance


class DepartmentModelTest(TestCase):
    """Test Department model functionality"""
    
    def test_department_creation(self):
        department = Department.objects.create(
            name="Engineering",
            code="ENG",
            budget=Decimal('1000000.00'),
            location="Building A"
        )
        
        self.assertEqual(department.name, "Engineering")
        self.assertEqual(department.code, "ENG")
        self.assertEqual(department.budget, Decimal('1000000.00'))
        self.assertEqual(department.location, "Building A")
        self.assertIsNotNone(department.created_at)
    
    def test_department_str_representation(self):
        department = Department.objects.create(
            name="Engineering",
            code="ENG",
            budget=Decimal('1000000.00'),
            location="Building A"
        )
        
        self.assertEqual(str(department), "Engineering (ENG)")


class DepartmentAPITest(APITestCase):
    """Test Department API endpoints"""
    
    def setUp(self):
        # Create test user and token
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        
        # Create test departments
        self.department1 = Department.objects.create(
            name="Engineering",
            code="ENG",
            budget=Decimal('1000000.00'),
            location="Building A"
        )
        
        self.department2 = Department.objects.create(
            name="Marketing",
            code="MKT",
            budget=Decimal('500000.00'),
            location="Building B"
        )
        
        self.department3 = Department.objects.create(
            name="Human Resources",
            code="HR",
            budget=Decimal('300000.00'),
            location="Building C"
        )
        
        # Create test employees
        self.employee1 = Employee.objects.create(
            employee_id="EMP001",
            full_name="John Doe",
            email="john.doe@company.com",
            department=self.department1,
            position="Software Engineer",
            salary=Decimal('75000.00'),
            hire_date=timezone.now().date()
        )
        
        self.employee2 = Employee.objects.create(
            employee_id="EMP002",
            full_name="Jane Smith",
            email="jane.smith@company.com",
            department=self.department1,
            position="Senior Developer",
            salary=Decimal('90000.00'),
            hire_date=timezone.now().date()
        )
        
        self.employee3 = Employee.objects.create(
            employee_id="EMP003",
            full_name="Bob Johnson",
            email="bob.johnson@company.com",
            department=self.department2,
            position="Marketing Manager",
            salary=Decimal('65000.00'),
            hire_date=timezone.now().date()
        )
    
    def authenticate(self):
        """Helper method to authenticate requests"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
    
    def test_department_list_unauthenticated(self):
        """Test that unauthenticated requests are rejected"""
        url = reverse('department-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_department_list_authenticated(self):
        """Test department list retrieval for authenticated users"""
        self.authenticate()
        url = reverse('department-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertIn('num_pages', response.data)
        self.assertEqual(len(response.data['results']), 3)
        
        # Check if all departments are present
        department_codes = [dept['code'] for dept in response.data['results']]
        self.assertIn('ENG', department_codes)
        self.assertIn('MKT', department_codes)
        self.assertIn('HR', department_codes)
    
    def test_department_list_search(self):
        """Test department search functionality"""
        self.authenticate()
        url = reverse('department-list-create')
        
        # Search by name
        response = self.client.get(url, {'search': 'Engineering'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Engineering')
        
        # Search by code
        response = self.client.get(url, {'search': 'MKT'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['code'], 'MKT')
        
        # Search by location
        response = self.client.get(url, {'search': 'Building B'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['location'], 'Building B')
        
        # Partial search
        response = self.client.get(url, {'search': 'Human'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Human Resources')
    
    def test_department_list_budget_filter(self):
        """Test filtering departments by budget range"""
        self.authenticate()
        url = reverse('department-list-create')
        
        # Min budget filter
        response = self.client.get(url, {'min_budget': 400000})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Engineering and Marketing
        
        # Max budget filter
        response = self.client.get(url, {'max_budget': 400000})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Only HR
        
        # Budget range filter
        response = self.client.get(url, {'min_budget': 400000, 'max_budget': 600000})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Only Marketing
    
    def test_department_list_location_filter(self):
        """Test filtering departments by location"""
        self.authenticate()
        url = reverse('department-list-create')
        
        response = self.client.get(url, {'location': 'Building A'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['location'], 'Building A')
        
        # Partial location search
        response = self.client.get(url, {'location': 'Building'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)  # All buildings
    
    def test_department_list_ordering(self):
        """Test ordering of department list"""
        self.authenticate()
        url = reverse('department-list-create')
        
        # Order by name ascending (default)
        response = self.client.get(url, {'ordering': 'name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [dept['name'] for dept in response.data['results']]
        self.assertEqual(names, ['Engineering', 'Human Resources', 'Marketing'])
        
        # Order by name descending
        response = self.client.get(url, {'ordering': '-name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [dept['name'] for dept in response.data['results']]
        self.assertEqual(names, ['Marketing', 'Human Resources', 'Engineering'])
        
        # Order by budget ascending
        response = self.client.get(url, {'ordering': 'budget'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        budgets = [float(dept['budget']) for dept in response.data['results']]
        self.assertEqual(budgets, [300000.0, 500000.0, 1000000.0])
        
        # Order by budget descending
        response = self.client.get(url, {'ordering': '-budget'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        budgets = [float(dept['budget']) for dept in response.data['results']]
        self.assertEqual(budgets, [1000000.0, 500000.0, 300000.0])
    
    def test_department_list_pagination(self):
        """Test pagination functionality"""
        self.authenticate()
        url = reverse('department-list-create')
        
        # Test page size limit
        response = self.client.get(url, {'page_size': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(response.data['num_pages'], 2)
        self.assertEqual(response.data['current_page'], 1)
        self.assertTrue(response.data['has_next'])
        self.assertFalse(response.data['has_previous'])
        
        # Test second page
        response = self.client.get(url, {'page_size': 2, 'page': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['current_page'], 2)
        self.assertFalse(response.data['has_next'])
        self.assertTrue(response.data['has_previous'])
        
        # Test maximum page size enforcement
        response = self.client.get(url, {'page_size': 150})  # Over limit
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should be limited to 100, but we only have 3 departments
        self.assertEqual(len(response.data['results']), 3)
    
    def test_department_create_success(self):
        """Test successful department creation"""
        self.authenticate()
        url = reverse('department-list-create')
        
        data = {
            'name': 'Finance',
            'code': 'FIN',
            'budget': '750000.00',
            'location': 'Building D'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['name'], 'Finance')
        self.assertEqual(response.data['data']['code'], 'FIN')
        
        # Verify department was created
        department = Department.objects.get(code='FIN')
        self.assertEqual(department.name, 'Finance')
        self.assertEqual(department.budget, Decimal('750000.00'))
    
    def test_department_create_duplicate_name(self):
        """Test department creation with duplicate name"""
        self.authenticate()
        url = reverse('department-list-create')
        
        data = {
            'name': 'Engineering',  # Already exists
            'code': 'ENG2',
            'budget': '750000.00',
            'location': 'Building D'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('errors', response.data)
    
    def test_department_create_duplicate_code(self):
        """Test department creation with duplicate code"""
        self.authenticate()
        url = reverse('department-list-create')
        
        data = {
            'name': 'Finance',
            'code': 'ENG',  # Already exists
            'budget': '750000.00',
            'location': 'Building D'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('errors', response.data)
    
    def test_department_create_missing_fields(self):
        """Test department creation with missing required fields"""
        self.authenticate()
        url = reverse('department-list-create')
        
        data = {
            'name': 'Finance',
            # Missing code, budget, location
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('errors', response.data)
    
    def test_department_detail_get_success(self):
        """Test successful department detail retrieval"""
        self.authenticate()
        url = reverse('department-detail', kwargs={'pk': self.department1.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Engineering')
        self.assertEqual(response.data['code'], 'ENG')
        self.assertIn('employee_count', response.data)
        self.assertEqual(response.data['employee_count'], 2)  # John and Jane
    
    def test_department_detail_get_not_found(self):
        """Test department detail retrieval for non-existent department"""
        self.authenticate()
        url = reverse('department-detail', kwargs={'pk': 99999})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_department_update_success(self):
        """Test successful department budget update"""
        self.authenticate()
        url = reverse('department-detail', kwargs={'pk': self.department1.id})
        
        data = {
            'budget': '1200000.00'
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify changes
        self.department1.refresh_from_db()
        self.assertEqual(self.department1.budget, Decimal('1200000.00'))
    
    def test_department_update_invalid_fields(self):
        """Test department update with invalid fields"""
        self.authenticate()
        url = reverse('department-detail', kwargs={'pk': self.department1.id})
        
        data = {
            'budget': '1200000.00',
            'name': 'New Engineering',  # Not allowed to update
            'code': 'NEWENG',  # Not allowed to update
            'location': 'New Building'  # Not allowed to update
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('invalid_fields', response.data['errors'])
    
    def test_department_update_invalid_budget(self):
        """Test department update with invalid budget"""
        self.authenticate()
        url = reverse('department-detail', kwargs={'pk': self.department1.id})
        
        data = {
            'budget': '-1000.00'  # Negative budget
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('errors', response.data)
    
    def test_department_update_not_found(self):
        """Test department update for non-existent department"""
        self.authenticate()
        url = reverse('department-detail', kwargs={'pk': 99999})
        
        data = {
            'budget': '1200000.00'
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_department_delete_success(self):
        """Test successful department deletion (no employees)"""
        self.authenticate()
        url = reverse('department-detail', kwargs={'pk': self.department3.id})  # HR has no employees
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        
        # Verify department was deleted
        with self.assertRaises(Department.DoesNotExist):
            Department.objects.get(id=self.department3.id)
    
    def test_department_delete_with_employees(self):
        """Test department deletion with existing employees"""
        self.authenticate()
        url = reverse('department-detail', kwargs={'pk': self.department1.id})  # Engineering has employees
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('Cannot delete department with existing employees', response.data['message'])
        
        # Verify department still exists
        self.assertTrue(Department.objects.filter(id=self.department1.id).exists())
    
    def test_department_delete_not_found(self):
        """Test department deletion for non-existent department"""
        self.authenticate()
        url = reverse('department-detail', kwargs={'pk': 99999})
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_department_employees_success(self):
        """Test successful department employees retrieval"""
        self.authenticate()
        url = reverse('department-employees', kwargs={'pk': self.department1.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('department', response.data)
        self.assertIn('employees', response.data)
        self.assertIn('employee_count', response.data)
        self.assertEqual(response.data['employee_count'], 2)
        self.assertEqual(len(response.data['employees']), 2)
        
        # Check if employees are correct
        employee_names = [emp['full_name'] for emp in response.data['employees']]
        self.assertIn('John Doe', employee_names)
        self.assertIn('Jane Smith', employee_names)
    
    def test_department_employees_empty(self):
        """Test department employees retrieval for department with no employees"""
        self.authenticate()
        url = reverse('department-employees', kwargs={'pk': self.department3.id})  # HR has no employees
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['employee_count'], 0)
        self.assertEqual(len(response.data['employees']), 0)
    
    def test_department_employees_not_found(self):
        """Test department employees retrieval for non-existent department"""
        self.authenticate()
        url = reverse('department-employees', kwargs={'pk': 99999})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    @patch('departments.operations.Performance')
    def test_department_statistics_success(self, mock_performance):
        """Test successful department statistics retrieval"""
        # Mock performance data
        mock_queryset = Mock()
        mock_queryset.filter.return_value.exists.return_value = True
        mock_queryset.filter.return_value.aggregate.return_value = {
            'avg': Decimal('4.2')
        }
        mock_performance.objects = mock_queryset
        
        self.authenticate()
        url = reverse('department-statistics', kwargs={'pk': self.department1.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('department', response.data)
        self.assertIn('employee_count', response.data)
        self.assertIn('average_salary', response.data)
        self.assertIn('salary_range', response.data)
        self.assertIn('positions', response.data)
        self.assertIn('performance_stats', response.data)
        
        # Check calculations
        self.assertEqual(response.data['employee_count'], 2)
        self.assertEqual(float(response.data['average_salary']), 82500.0)  # (75000 + 90000) / 2
        self.assertEqual(float(response.data['salary_range']['min']), 75000.0)
        self.assertEqual(float(response.data['salary_range']['max']), 90000.0)
        
        # Check positions
        positions = response.data['positions']
        self.assertIn('Software Engineer', positions)
        self.assertIn('Senior Developer', positions)
    
    @patch('departments.operations.Performance')
    def test_department_statistics_no_performance(self, mock_performance):
        """Test department statistics without performance data"""
        # Mock no performance data
        mock_queryset = Mock()
        mock_queryset.filter.return_value.exists.return_value = False
        mock_performance.objects = mock_queryset
        
        self.authenticate()
        url = reverse('department-statistics', kwargs={'pk': self.department1.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('department', response.data)
        self.assertIn('employee_count', response.data)
        self.assertIn('average_salary', response.data)
        self.assertNotIn('performance_stats', response.data)  # Should not be present
    
    def test_department_statistics_empty_department(self):
        """Test department statistics for department with no employees"""
        self.authenticate()
        url = reverse('department-statistics', kwargs={'pk': self.department3.id})  # HR has no employees
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['employee_count'], 0)
        self.assertEqual(response.data['average_salary'], 0)
        self.assertEqual(response.data['salary_range']['min'], 0)
        self.assertEqual(response.data['salary_range']['max'], 0)
        self.assertEqual(response.data['positions'], [])
    
    def test_department_statistics_not_found(self):
        """Test department statistics for non-existent department"""
        self.authenticate()
        url = reverse('department-statistics', kwargs={'pk': 99999})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_department_list_server_error(self):
        """Test server error handling in department list"""
        self.authenticate()
        url = reverse('department-list-create')
        
        with patch('departments.operations.DepartmentOperations.get_department_list') as mock_get_list:
            mock_get_list.side_effect = Exception("Database error")
            
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertIn('error', response.data)
    
    def test_department_create_server_error(self):
        """Test server error handling in department creation"""
        self.authenticate()
        url = reverse('department-list-create')
        
        data = {
            'name': 'Finance',
            'code': 'FIN',
            'budget': '750000.00',
            'location': 'Building D'
        }
        
        with patch('departments.operations.DepartmentOperations.create_department') as mock_create:
            mock_create.side_effect = Exception("Database error")
            
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertIn('error', response.data)


class DepartmentOperationsTest(TestCase):
    """Test Department business logic operations"""
    
    def setUp(self):
        self.department = Department.objects.create(
            name="Engineering",
            code="ENG",
            budget=Decimal('1000000.00'),
            location="Building A"
        )
        
        self.employee = Employee.objects.create(
            employee_id="EMP001",
            full_name="John Doe",
            email="john.doe@company.com",
            department=self.department,
            position="Software Engineer",
            salary=Decimal('75000.00'),
            hire_date=timezone.now().date()
        )
    
    def test_get_department_detail_success(self):
        """Test successful department detail retrieval"""
        from .operations import DepartmentOperations
        
        result = DepartmentOperations.get_department_detail(self.department.id)
        
        self.assertEqual(result['name'], 'Engineering')
        self.assertEqual(result['code'], 'ENG')
        self.assertIn('employee_count', result)
    
    def test_get_department_detail_not_found(self):
        """Test department detail retrieval for non-existent department"""
        from .operations import DepartmentOperations
        from django.http import Http404
        
        with self.assertRaises(Http404):
            DepartmentOperations.get_department_detail(99999)
    
    def test_create_department_success(self):
        """Test successful department creation"""
        from .operations import DepartmentOperations
        
        data = {
            'name': 'Finance',
            'code': 'FIN',
            'budget': '750000.00',
            'location': 'Building D'
        }
        
        result = DepartmentOperations.create_department(data)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertEqual(result['data']['name'], 'Finance')
        
        # Verify department was created
        department = Department.objects.get(code='FIN')
        self.assertEqual(department.name, 'Finance')
    
    def test_create_department_validation_error(self):
        """Test department creation with validation errors"""
        from .operations import DepartmentOperations
        
        data = {
            'name': 'Engineering',  # Duplicate
            'code': 'FIN',
            'budget': '750000.00',
            'location': 'Building D'
        }
        
        result = DepartmentOperations.create_department(data)
        
        self.assertFalse(result['success'])
        self.assertIn('errors', result)
    
    def test_update_department_success(self):
        """Test successful department update"""
        from .operations import DepartmentOperations
        
        data = {
            'budget': '1200000.00'
        }
        
        result = DepartmentOperations.update_department(self.department.id, data)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        
        # Verify changes
        self.department.refresh_from_db()
        self.assertEqual(self.department.budget, Decimal('1200000.00'))
    
    def test_update_department_invalid_fields(self):
        """Test department update with invalid fields"""
        from .operations import DepartmentOperations
        
        data = {
            'budget': '1200000.00',
            'name': 'New Engineering',  # Not allowed
            'code': 'NEWENG'  # Not allowed
        }
        
        result = DepartmentOperations.update_department(self.department.id, data)
        
        self.assertFalse(result['success'])
        self.assertIn('errors', result)
        self.assertIn('invalid_fields', result['errors'])
    
    def test_delete_department_success(self):
        """Test successful department deletion"""
        from .operations import DepartmentOperations
        
        # Create department without employees
        empty_dept = Department.objects.create(
            name="Finance",
            code="FIN",
            budget=Decimal('500000.00'),
            location="Building D"
        )
        
        result = DepartmentOperations.delete_department(empty_dept.id)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        
        # Verify department was deleted
        with self.assertRaises(Department.DoesNotExist):
            Department.objects.get(id=empty_dept.id)
    
    def test_delete_department_with_employees(self):
        """Test department deletion with existing employees"""
        from .operations import DepartmentOperations
        
        result = DepartmentOperations.delete_department(self.department.id)
        
        self.assertFalse(result['success'])
        self.assertIn('Cannot delete department with existing employees', result['message'])
        
        # Verify department still exists
        self.assertTrue(Department.objects.filter(id=self.department.id).exists())
    
    def test_get_department_employees(self):
        """Test getting department employees"""
        from .operations import DepartmentOperations
        
        result = DepartmentOperations.get_department_employees(self.department.id)
        
        self.assertIn('department', result)
        self.assertIn('employees', result)
        self.assertIn('employee_count', result)
        self.assertEqual(result['employee_count'], 1)
        self.assertEqual(len(result['employees']), 1)
        self.assertEqual(result['employees'][0]['full_name'], 'John Doe')
    
    @patch('departments.operations.Performance')
    def test_get_department_statistics_with_performance(self, mock_performance):
        """Test getting department statistics with performance data"""
        from .operations import DepartmentOperations
        
        # Mock performance data
        mock_queryset = Mock()
        mock_queryset.filter.return_value.exists.return_value = True
        mock_queryset.filter.return_value.aggregate.return_value = {
            'avg': Decimal('4.5')
        }
        mock_performance.objects = mock_queryset
        
        result = DepartmentOperations.get_department_statistics(self.department.id)
        
        self.assertIn('department', result)
        self.assertIn('employee_count', result)
        self.assertIn('average_salary', result)
        self.assertIn('salary_range', result)
        self.assertIn('positions', result)
        