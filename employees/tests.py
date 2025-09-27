# apps/employees/tests.py
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

from .models import Employee
from departments.models import Department
from analytics.models import Performance, Attendance


class EmployeeModelTest(TestCase):
    """Test Employee model functionality"""
    
    def setUp(self):
        self.department = Department.objects.create(
            name="Engineering",
            code="ENG",
            budget=Decimal('1000000.00'),
            location="Building A"
        )
    
    def test_employee_creation(self):
        employee = Employee.objects.create(
            employee_id="EMP001",
            full_name="John Doe",
            email="john.doe@company.com",
            department=self.department,
            position="Software Engineer",
            salary=Decimal('75000.00'),
            hire_date=timezone.now().date()
        )
        
        self.assertEqual(employee.employee_id, "EMP001")
        self.assertEqual(employee.full_name, "John Doe")
        self.assertEqual(employee.email, "john.doe@company.com")
        self.assertEqual(employee.department, self.department)
        self.assertEqual(employee.position, "Software Engineer")
        self.assertEqual(employee.salary, Decimal('75000.00'))
        self.assertIsNotNone(employee.hire_date)
        self.assertIsNotNone(employee.created_at)
    
    def test_employee_str_representation(self):
        employee = Employee.objects.create(
            employee_id="EMP001",
            full_name="John Doe",
            email="john.doe@company.com",
            department=self.department,
            position="Software Engineer",
            salary=Decimal('75000.00'),
            hire_date=timezone.now().date()
        )
        
        self.assertEqual(str(employee), "John Doe (EMP001)")


class EmployeeAPITest(APITestCase):
    """Test Employee API endpoints"""
    
    def setUp(self):
        # Create test user and token
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        
        # Create test department
        self.department = Department.objects.create(
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
        
        # Create test employees
        self.employee1 = Employee.objects.create(
            employee_id="EMP001",
            full_name="John Doe",
            email="john.doe@company.com",
            department=self.department,
            position="Software Engineer",
            salary=Decimal('75000.00'),
            hire_date=timezone.now().date()
        )
        
        self.employee2 = Employee.objects.create(
            employee_id="EMP002",
            full_name="Jane Smith",
            email="jane.smith@company.com",
            department=self.department,
            position="Senior Developer",
            salary=Decimal('90000.00'),
            hire_date=timezone.now().date() - timedelta(days=365)
        )
        
        self.employee3 = Employee.objects.create(
            employee_id="EMP003",
            full_name="Bob Johnson",
            email="bob.johnson@company.com",
            department=self.department2,
            position="Marketing Manager",
            salary=Decimal('65000.00'),
            hire_date=timezone.now().date() - timedelta(days=180)
        )
    
    def authenticate(self):
        """Helper method to authenticate requests"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
    
    def test_employee_list_unauthenticated(self):
        """Test that unauthenticated requests are rejected"""
        url = reverse('employee-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_employee_list_authenticated(self):
        """Test employee list retrieval for authenticated users"""
        self.authenticate()
        url = reverse('employee-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertIn('num_pages', response.data)
        self.assertEqual(len(response.data['results']), 3)
        
        # Check if all employees are present
        employee_ids = [emp['employee_id'] for emp in response.data['results']]
        self.assertIn('EMP001', employee_ids)
        self.assertIn('EMP002', employee_ids)
        self.assertIn('EMP003', employee_ids)
    
    def test_employee_list_search(self):
        """Test employee search functionality"""
        self.authenticate()
        url = reverse('employee-list-create')
        
        # Search by name
        response = self.client.get(url, {'search': 'John'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['full_name'], 'John Doe')
        
        # Search by email
        response = self.client.get(url, {'search': 'jane.smith'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['email'], 'jane.smith@company.com')
        
        # Search by employee_id
        response = self.client.get(url, {'search': 'EMP003'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['employee_id'], 'EMP003')
        
        # Search by position
        response = self.client.get(url, {'search': 'Manager'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['position'], 'Marketing Manager')
    
    def test_employee_list_department_filter(self):
        """Test filtering employees by department"""
        self.authenticate()
        url = reverse('employee-list-create')
        
        response = self.client.get(url, {'department': self.department.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # John and Jane
        
        response = self.client.get(url, {'department': self.department2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Bob
    
    def test_employee_list_salary_filter(self):
        """Test filtering employees by salary range"""
        self.authenticate()
        url = reverse('employee-list-create')
        
        # Min salary filter
        response = self.client.get(url, {'min_salary': 80000})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Only Jane
        
        # Max salary filter
        response = self.client.get(url, {'max_salary': 70000})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Only Bob
        
        # Salary range filter
        response = self.client.get(url, {'min_salary': 70000, 'max_salary': 80000})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Only John
    
    def test_employee_list_ordering(self):
        """Test ordering of employee list"""
        self.authenticate()
        url = reverse('employee-list-create')
        
        # Order by name ascending (default)
        response = self.client.get(url, {'ordering': 'full_name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [emp['full_name'] for emp in response.data['results']]
        self.assertEqual(names, ['Bob Johnson', 'Jane Smith', 'John Doe'])
        
        # Order by name descending
        response = self.client.get(url, {'ordering': '-full_name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [emp['full_name'] for emp in response.data['results']]
        self.assertEqual(names, ['John Doe', 'Jane Smith', 'Bob Johnson'])
        
        # Order by salary ascending
        response = self.client.get(url, {'ordering': 'salary'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        salaries = [float(emp['salary']) for emp in response.data['results']]
        self.assertEqual(salaries, [65000.0, 75000.0, 90000.0])
    
    def test_employee_list_pagination(self):
        """Test pagination functionality"""
        self.authenticate()
        url = reverse('employee-list-create')
        
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
    
    def test_employee_create_success(self):
        """Test successful employee creation"""
        self.authenticate()
        url = reverse('employee-list-create')
        
        data = {
            'employee_id': 'EMP004',
            'full_name': 'Alice Brown',
            'email': 'alice.brown@company.com',
            'department': self.department.id,
            'position': 'Data Analyst',
            'salary': '70000.00',
            'hire_date': timezone.now().date().isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['employee_id'], 'EMP004')
        
        # Verify employee was created
        employee = Employee.objects.get(employee_id='EMP004')
        self.assertEqual(employee.full_name, 'Alice Brown')
        self.assertEqual(employee.email, 'alice.brown@company.com')
    
    def test_employee_create_duplicate_employee_id(self):
        """Test employee creation with duplicate employee_id"""
        self.authenticate()
        url = reverse('employee-list-create')
        
        data = {
            'employee_id': 'EMP001',  # Already exists
            'full_name': 'Alice Brown',
            'email': 'alice.brown@company.com',
            'department': self.department.id,
            'position': 'Data Analyst',
            'salary': '70000.00',
            'hire_date': timezone.now().date().isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('errors', response.data)
    
    def test_employee_create_duplicate_email(self):
        """Test employee creation with duplicate email"""
        self.authenticate()
        url = reverse('employee-list-create')
        
        data = {
            'employee_id': 'EMP004',
            'full_name': 'Alice Brown',
            'email': 'john.doe@company.com',  # Already exists
            'department': self.department.id,
            'position': 'Data Analyst',
            'salary': '70000.00',
            'hire_date': timezone.now().date().isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('errors', response.data)
    
    def test_employee_create_missing_fields(self):
        """Test employee creation with missing required fields"""
        self.authenticate()
        url = reverse('employee-list-create')
        
        data = {
            'employee_id': 'EMP004',
            'full_name': 'Alice Brown',
            # Missing email, department, position, salary, hire_date
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('errors', response.data)
    
    def test_employee_detail_get_success(self):
        """Test successful employee detail retrieval"""
        self.authenticate()
        url = reverse('employee-detail', kwargs={'pk': self.employee1.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['employee_id'], 'EMP001')
        self.assertEqual(response.data['full_name'], 'John Doe')
        self.assertIn('department', response.data)
        self.assertEqual(response.data['department']['name'], 'Engineering')
    
    def test_employee_detail_get_not_found(self):
        """Test employee detail retrieval for non-existent employee"""
        self.authenticate()
        url = reverse('employee-detail', kwargs={'pk': 99999})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_employee_update_success(self):
        """Test successful employee update"""
        self.authenticate()
        url = reverse('employee-detail', kwargs={'pk': self.employee1.id})
        
        data = {
            'position': 'Senior Software Engineer',
            'department': self.department2.id,
            'salary': '85000.00'
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify changes
        self.employee1.refresh_from_db()
        self.assertEqual(self.employee1.position, 'Senior Software Engineer')
        self.assertEqual(self.employee1.department.id, self.department2.id)
        self.assertEqual(self.employee1.salary, Decimal('85000.00'))
    
    def test_employee_update_invalid_fields(self):
        """Test employee update with invalid fields"""
        self.authenticate()
        url = reverse('employee-detail', kwargs={'pk': self.employee1.id})
        
        data = {
            'position': 'Senior Software Engineer',
            'full_name': 'New Name',  # Not allowed to update
            'email': 'new@email.com',  # Not allowed to update
            'employee_id': 'NEW001'  # Not allowed to update
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('invalid_fields', response.data['errors'])
    
    def test_employee_update_not_found(self):
        """Test employee update for non-existent employee"""
        self.authenticate()
        url = reverse('employee-detail', kwargs={'pk': 99999})
        
        data = {
            'position': 'Senior Software Engineer',
            'salary': '85000.00'
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_employee_delete_success(self):
        """Test successful employee deletion"""
        self.authenticate()
        url = reverse('employee-detail', kwargs={'pk': self.employee1.id})
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        
        # Verify employee was deleted
        with self.assertRaises(Employee.DoesNotExist):
            Employee.objects.get(id=self.employee1.id)
    
    def test_employee_delete_not_found(self):
        """Test employee deletion for non-existent employee"""
        self.authenticate()
        url = reverse('employee-detail', kwargs={'pk': 99999})
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    @patch('employees.operations.Performance')
    def test_employee_performance_success(self, mock_performance):
        """Test successful employee performance retrieval"""
        # Mock performance data
        mock_queryset = Mock()
        mock_queryset.filter.return_value.order_by.return_value = []
        mock_queryset.filter.return_value.order_by.return_value.count.return_value = 2
        mock_performance.objects = mock_queryset
        
        self.authenticate()
        url = reverse('employee-performance', kwargs={'pk': self.employee1.id})
        
        with patch('analytics.serializers.PerformanceSerializerForEmployeeModel') as mock_serializer:
            mock_serializer.return_value.data = []
            
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('employee_id', response.data)
            self.assertIn('employee_name', response.data)
            self.assertIn('department', response.data)
            self.assertIn('performances', response.data)
            self.assertIn('performance_count', response.data)
    
    def test_employee_performance_not_found(self):
        """Test employee performance retrieval for non-existent employee"""
        self.authenticate()
        url = reverse('employee-performance', kwargs={'pk': 99999})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    @patch('employees.operations.Attendance')
    def test_employee_attendance_success(self, mock_attendance):
        """Test successful employee attendance retrieval"""
        # Mock attendance data
        mock_queryset = Mock()
        mock_queryset.filter.return_value.order_by.return_value = []
        mock_queryset.filter.return_value.order_by.return_value.count.return_value = 10
        mock_attendance.objects = mock_queryset
        
        self.authenticate()
        url = reverse('employee-attendance', kwargs={'pk': self.employee1.id})
        
        with patch('analytics.serializers.AttendanceSerializerForEmployeeModel') as mock_serializer:
            mock_serializer.return_value.data = []
            
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('employee_id', response.data)
            self.assertIn('employee_name', response.data)
            self.assertIn('department', response.data)
            self.assertIn('attendance_records', response.data)
            self.assertIn('period', response.data)
            self.assertIn('total_records', response.data)
    
    @patch('employees.operations.Attendance')
    def test_employee_attendance_custom_days(self, mock_attendance):
        """Test employee attendance retrieval with custom days parameter"""
        # Mock attendance data
        mock_queryset = Mock()
        mock_queryset.filter.return_value.order_by.return_value = []
        mock_queryset.filter.return_value.order_by.return_value.count.return_value = 5
        mock_attendance.objects = mock_queryset
        
        self.authenticate()
        url = reverse('employee-attendance', kwargs={'pk': self.employee1.id})
        
        with patch('analytics.serializers.AttendanceSerializerForEmployeeModel') as mock_serializer:
            mock_serializer.return_value.data = []
            
            response = self.client.get(url, {'days': 15})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('period', response.data)
    
    def test_employee_attendance_not_found(self):
        """Test employee attendance retrieval for non-existent employee"""
        self.authenticate()
        url = reverse('employee-attendance', kwargs={'pk': 99999})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_employee_list_server_error(self):
        """Test server error handling in employee list"""
        self.authenticate()
        url = reverse('employee-list-create')
        
        with patch('employees.operations.EmployeeOperations.get_employee_list') as mock_get_list:
            mock_get_list.side_effect = Exception("Database error")
            
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertIn('error', response.data)
    
    def test_employee_create_server_error(self):
        """Test server error handling in employee creation"""
        self.authenticate()
        url = reverse('employee-list-create')
        
        data = {
            'employee_id': 'EMP004',
            'full_name': 'Alice Brown',
            'email': 'alice.brown@company.com',
            'department': self.department.id,
            'position': 'Data Analyst',
            'salary': '70000.00',
            'hire_date': timezone.now().date().isoformat()
        }
        
        with patch('employees.operations.EmployeeOperations.create_employee') as mock_create:
            mock_create.side_effect = Exception("Database error")
            
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertIn('error', response.data)


class EmployeeOperationsTest(TestCase):
    """Test Employee business logic operations"""
    
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
    
    def test_get_employee_detail_success(self):
        """Test successful employee detail retrieval"""
        from .operations import EmployeeOperations
        
        result = EmployeeOperations.get_employee_detail(self.employee.id)
        
        self.assertEqual(result['employee_id'], 'EMP001')
        self.assertEqual(result['full_name'], 'John Doe')
        self.assertIn('department', result)
    
    def test_get_employee_detail_not_found(self):
        """Test employee detail retrieval for non-existent employee"""
        from .operations import EmployeeOperations
        from django.http import Http404
        
        with self.assertRaises(Http404):
            EmployeeOperations.get_employee_detail(99999)
    
    def test_create_employee_success(self):
        """Test successful employee creation"""
        from .operations import EmployeeOperations
        
        data = {
            'employee_id': 'EMP002',
            'full_name': 'Jane Smith',
            'email': 'jane.smith@company.com',
            'department': self.department.id,
            'position': 'Data Analyst',
            'salary': '70000.00',
            'hire_date': timezone.now().date().isoformat()
        }
        
        result = EmployeeOperations.create_employee(data)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertEqual(result['data']['employee_id'], 'EMP002')
        
        # Verify employee was created
        employee = Employee.objects.get(employee_id='EMP002')
        self.assertEqual(employee.full_name, 'Jane Smith')
    
    def test_create_employee_validation_error(self):
        """Test employee creation with validation errors"""
        from .operations import EmployeeOperations
        
        data = {
            'employee_id': 'EMP001',  # Duplicate
            'full_name': 'Jane Smith',
            'email': 'jane.smith@company.com',
            'department': self.department.id,
            'position': 'Data Analyst',
            'salary': '70000.00',
            'hire_date': timezone.now().date().isoformat()
        }
        
        result = EmployeeOperations.create_employee(data)
        
        self.assertFalse(result['success'])
        self.assertIn('errors', result)
    
    def test_update_employee_success(self):
        """Test successful employee update"""
        from .operations import EmployeeOperations
        
        data = {
            'position': 'Senior Software Engineer',
            'salary': '85000.00'
        }
        
        result = EmployeeOperations.update_employee(self.employee.id, data)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        
        # Verify changes
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.position, 'Senior Software Engineer')
        self.assertEqual(self.employee.salary, Decimal('85000.00'))
    
    def test_update_employee_invalid_fields(self):
        """Test employee update with invalid fields"""
        from .operations import EmployeeOperations
        
        data = {
            'position': 'Senior Software Engineer',
            'full_name': 'New Name',  # Not allowed
            'email': 'new@email.com'  # Not allowed
        }
        
        result = EmployeeOperations.update_employee(self.employee.id, data)
        
        self.assertFalse(result['success'])
        self.assertIn('errors', result)
        self.assertIn('invalid_fields', result['errors'])
    
    def test_delete_employee_success(self):
        """Test successful employee deletion"""
        from .operations import EmployeeOperations
        
        result = EmployeeOperations.delete_employee(self.employee.id)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        
        # Verify employee was deleted
        with self.assertRaises(Employee.DoesNotExist):
            Employee.objects.get(id=self.employee.id)
# Create your tests here.
