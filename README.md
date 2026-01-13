# glowing-waffle


A comprehensive Django REST API system for managing employee data with synthetic data generation, PostgreSQL storage, REST APIs, and Chart.js data visualization. Built to demonstrate modern web development architecture and coding efficiency.

## 📋 Table of Contents

- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [System Architecture](#-system-architecture)
- [Database Design](#-database-design)
- [Installation & Setup](#-installation--setup)
- [API Documentation](#-api-documentation)
- [Usage Examples](#-usage-examples)
- [Data Generation](#-data-generation)
- [Analytics & Visualization](#-analytics--visualization)
- [Authentication](#-authentication)
- [Rate Limiting](#-rate-limiting)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Features

### Core Functionality
- **Employee Management**: Complete CRUD operations for employee records
- **Department Management**: Department creation, updates, and analytics
- **Performance Tracking**: Employee performance reviews and scoring
- **Attendance Monitoring**: Daily attendance tracking with multiple statuses
- **Analytics Dashboard**: Real-time data visualization with Chart.js

### Technical Features
- **RESTful APIs**: Comprehensive REST API with Django REST Framework
- **Authentication**: Token-based authentication system
- **Rate Limiting**: Multi-level throttling for API security
- **Data Export**: JSON and CSV export functionality
- **Swagger Documentation**: Interactive API documentation
- **PostgreSQL Integration**: Production-ready database setup
- **Synthetic Data Generation**: Automated test data creation with Faker

## 🛠 Technology Stack

### Backend
- **Django 4.2.24**: Web framework
- **Django REST Framework**: API development
- **PostgreSQL**: Primary database
- **Python 3.8+**: Programming language

### Documentation & Testing
- **drf-yasg**: Swagger/OpenAPI documentation
- **Faker**: Synthetic data generation
- **Django Test Framework**: Unit and integration testing

### Frontend Integration
- **Chart.js**: Data visualization
- **HTML5/CSS3/JavaScript**: Dashboard interface

## 📁 Project Structure

```
employee_management_system/
├── manage.py
├── requirements.txt
├── README.md
├── LICENSE
│
├── config/                     # Django project configuration
│   ├── __init__.py
│   ├── settings.py            # Main settings with throttle configuration
│   ├── urls.py                # URL routing
│   ├── wsgi.py
│   └── asgi.py
│
├── employees/                  # Employee management app
│   ├── __init__.py
│   ├── models.py              # Employee model
│   ├── serializers.py         # API serializers
│   ├── views.py               # API views
│   ├── operations.py          # Business logic
│   ├── urls.py                # App URLs
│   ├── admin.py               # Admin interface
│   ├── apps.py
│   ├── tests.py
│   └── migrations/
│
├── departments/               # Department management app
│   ├── __init__.py
│   ├── models.py             # Department model
│   ├── serializers.py        # API serializers
│   ├── views.py              # API views
│   ├── operations.py         # Business logic
│   ├── urls.py               # App URLs
│   ├── admin.py
│   ├── apps.py
│   ├── tests.py
│   └── migrations/
│
├── analytics/                # Analytics and reporting app
│   ├── __init__.py
│   ├── models.py             # Performance & Attendance models
│   ├── serializers.py        # Chart.js data serializers
│   ├── views.py              # Analytics API views
│   ├── operations.py         # Analytics business logic
│   ├── urls.py               # Analytics URLs
│   ├── admin.py
│   ├── apps.py
│   ├── tests.py
│   └── migrations/
│
├── authentication/           # Custom authentication app
│   ├── __init__.py
│   ├── views.py              # Auth endpoints
│   ├── serializers.py        # Auth serializers
│   ├── urls.py               # Auth URLs
│   ├── admin.py
│   ├── apps.py
│   └── tests.py
│
└── utils/                    # Utility functions
    ├── __init__.py
    └── data_generator.py     # Faker data generation script
```

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                           │
├─────────────────────────────────────────────────────────────┤
│  Web Dashboard  │  Mobile App  │  Third-party Applications  │
│   (Chart.js)    │              │                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      API LAYER                             │
├─────────────────────────────────────────────────────────────┤
│         Django REST Framework + Authentication             │
│    ┌─────────────┬─────────────┬─────────────┬───────────┐   │
│    │ Employees   │ Departments │ Analytics   │   Auth    │   │
│    │    API      │     API     │     API     │    API    │   │
│    └─────────────┴─────────────┴─────────────┴───────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                     │
├─────────────────────────────────────────────────────────────┤
│    ┌─────────────┬─────────────┬─────────────┬───────────┐   │
│    │  Employee   │ Department  │ Analytics   │   Data    │   │
│    │ Operations  │ Operations  │ Operations  │Generator  │   │
│    └─────────────┴─────────────┴─────────────┴───────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     DATA LAYER                             │
├─────────────────────────────────────────────────────────────┤
│                    PostgreSQL Database                     │
│  ┌───────────┬─────────────┬─────────────┬─────────────┐    │
│  │Employee   │ Department  │ Performance │ Attendance  │    │
│  │   Table   │    Table    │    Table    │   Table     │    │
│  └───────────┴─────────────┴─────────────┴─────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Database Design

### Entity Relationship Diagram

```
┌─────────────────────┐       ┌─────────────────────┐
│    Department       │       │      Employee       │
├─────────────────────┤       ├─────────────────────┤
│ id (PK)             │◄──────┤ id (PK)             │
│ name                │  1:N  │ employee_id         │
│ code                │       │ full_name           │
│ budget              │       │ email               │
│ location            │       │ department_id (FK)  │
│ created_at          │       │ position            │
└─────────────────────┘       │ salary              │
                              │ hire_date           │
                              │ created_at          │
                              └─────────────────────┘
                                       │
                               ┌───────┴───────┐
                               │ 1:N           │ 1:N
                               ▼               ▼
                ┌─────────────────────┐       ┌─────────────────────┐
                │    Performance      │       │    Attendance       │
                ├─────────────────────┤       ├─────────────────────┤
                │ id (PK)             │       │ id (PK)             │
                │ employee_id (FK)    │       │ employee_id (FK)    │
                │ review_period       │       │ date                │
                │ overall_score       │       │ check_in_time       │
                │ technical_score     │       │ check_out_time      │
                │ communication_score │       │ total_hours         │
                │ teamwork_score      │       │ status              │
                │ review_date         │       │ created_at          │
                │ created_at          │       └─────────────────────┘
                └─────────────────────┘
```

### Model Specifications

#### 1. Department Model
```python
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### 2. Employee Model
```python
class Employee(models.Model):
    employee_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    position = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    hire_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
```

#### 3. Performance Model
```python
class Performance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    review_period = models.CharField(max_length=20)  # "2024-Q1"
    overall_score = models.DecimalField(max_digits=3, decimal_places=2)
    technical_score = models.DecimalField(max_digits=3, decimal_places=2)
    communication_score = models.DecimalField(max_digits=3, decimal_places=2)
    teamwork_score = models.DecimalField(max_digits=3, decimal_places=2)
    review_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
```

#### 4. Attendance Model
```python
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
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
```

## 🔧 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip (Python package installer)
- git

### 1. Clone the Repository
```bash
git clone https://github.com/Nimanita/glowing-waffle.git
cd glowing-waffle
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv env

# Activate virtual environment
# On Windows:
env\Scripts\activate
# On macOS/Linux:
source env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. PostgreSQL Database Setup

#### Install PostgreSQL
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# macOS (with Homebrew)
brew install postgresql
brew services start postgresql

# Windows
# Download and install from: https://www.postgresql.org/download/windows/
```

#### Create Database and User
```bash
# Access PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE employee_management;
CREATE USER emp_user WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE employee_management TO emp_user;
ALTER USER emp_user CREATEDB;
\q
```

### 5. Environment Configuration

Create a `.env` file in the config folder:

```bash
# Database Configuration
DB_NAME=employee_management
DB_USER=emp_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Django Configuration
SECRET_KEY=your-super-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1


```

### 6. Database Migration
```bash
# Create and apply migrations

python3 manage.py migrate

# Create superuser
python3 manage.py createsuperuser
```

### 7. Generate Sample Data
```bash
run the script:
python3 utils/data_generator.py
```

### 8. Create Directories and Static Files
```bash
# Create required directories
mkdir -p logs static media templates

# Collect static files (if needed)
python3 manage.py collectstatic --noinput
```

### 9. Run the Development Server
```bash
python3 manage.py runserver
```

### 10. Verify Installation

Visit the following URLs to verify everything is working:

- **API Root**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/
- **API Documentation**: http://localhost:8000/swagger/
- **ReDoc Documentation**: http://localhost:8000/redoc/

## 📚 API Documentation

### Base URL
```
Development: http://localhost:8000/api/
Production: https://yourapi.com/api/
```

### Authentication
All API endpoints require authentication except for the login endpoint.

```bash
# Get authentication token
POST /api/auth/login/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}

# Response
{
    "token": "your-auth-token-here",
    "user_id": 1,
    "username": "your_username"
}

# Use token in subsequent requests
## Authorization: Token your-auth-token-here
```

### Core API Endpoints

#### Employee Management
```bash
# List employees (with pagination, search, filtering)
GET /api/employees/
GET /api/employees/?search=john&department=1&min_salary=50000&page=1

# Create employee
POST /api/employees/
{
    "employee_id": "EMP001",
    "full_name": "John Doe",
    "email": "john@example.com",
    "department": 1,
    "position": "Software Developer",
    "salary": "75000.00",
    "hire_date": "2024-01-15"
}

# Get employee details
GET /api/employees/1/

# Update employee
PUT /api/employees/1/
{
    "position": "Senior Software Developer",
    "salary": "85000.00",
    "department": 1
}

# Delete employee
DELETE /api/employees/1/

# Get employee performance
GET /api/employees/1/performance/

# Get employee attendance
GET /api/employees/1/attendance/?days=30
```

#### Department Management
```bash
# List departments
GET /api/departments/
GET /api/departments/?search=IT&min_budget=100000

# Create department
POST /api/departments/
{
    "name": "Information Technology",
    "code": "IT",
    "budget": "500000.00",
    "location": "Building A, Floor 3"
}

# Get department details
GET /api/departments/1/

# Update department (budget only)
PUT /api/departments/1/
{
    "budget": "600000.00"
}

# Delete department
DELETE /api/departments/1/

# Get department employees
GET /api/departments/1/employees/

# Get department statistics
GET /api/departments/1/statistics/
```

#### Analytics & Dashboard
```bash
# Dashboard summary
GET /api/analytics/summary/

# Department statistics (for pie chart)
GET /api/analytics/department-stats/

# Salary distribution (for bar chart)
GET /api/analytics/salary-distribution/

# Performance trends (for line chart)
GET /api/analytics/performance-trends/

# Attendance rates (for doughnut chart)
GET /api/analytics/attendance-rates/

# Hire date timeline (for line chart)
GET /api/analytics/hire-timeline/

# Export analytics data
GET /api/analytics/export/?format=json
GET /api/analytics/export/?format=csv
```

### Response Format Examples

#### Employee List Response
```json
{
    "results": [
        {
            "id": 1,
            "employee_id": "EMP001",
            "full_name": "John Doe",
            "email": "john.doe@company.com",
            "department_name": "Information Technology",
            "position": "Software Developer",
            "salary": "75000.00",
            "hire_date": "2024-01-15"
        }
    ],
    "count": 25,
    "num_pages": 2,
    "current_page": 1,
    "has_next": true,
    "has_previous": false
}
```

#### Analytics Summary Response
```json
{
    "total_employees": 25,
    "total_departments": 5,
    "average_salary": 72500.50,
    "average_performance": 4.2,
    "attendance_rate": 94.5,
    "latest_hires": [...]
}
```

## 🔐 Authentication

The system uses Django REST Framework's Token Authentication:

### Login Process
1. Send credentials to `/api/auth/login/`
2. Receive authentication token
3. Include token in `Authorization` header: `Token your-token-here`
4. Token remains valid until explicitly revoked

### Security Features
- Password validation and hashing
- Token-based stateless authentication
- Rate limiting on authentication endpoints
- CSRF protection for web forms

## 🚦 Rate Limiting

The API implements comprehensive rate limiting:

### Rate Limits by User Type
- **Anonymous Users**: 100 requests/hour
- **Authenticated Users**: 1000 requests/hour

### Endpoint-Specific Limits
- **Login Attempts**: 5/minute
- **Registration**: 3/minute
- **Password Reset**: 3/minute
- **Analytics APIs**: 200/hour
- **Data Export**: 10/hour

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## 📈 Analytics & Visualization

### Dashboard Features
The system provides a comprehensive analytics dashboard with Chart.js integration:

1. **Department Distribution** - Pie Chart
   - Employee count by department
   - Interactive hover effects
   - Custom color schemes

2. **Salary Analysis** - Bar Chart
   - Average salary by department
   - Comparative visualization
   - Responsive design

3. **Performance Trends** - Line Chart
   - Performance scores over time
   - Multi-period comparison
   - Trend analysis

4. **Attendance Overview** - Doughnut Chart
   - Monthly attendance rates
   - Status breakdown
   - Real-time updates

5. **Hiring Timeline** - Line Chart
   - New hires over time
   - Seasonal patterns
   - Growth tracking

### VISUAL APIS

## Analytics Dashboard Interface (Chart.js frontend)
- GET /api/analytics/dashboard/
- POST /api/analytics/login
  
<img width="1834" height="910" alt="Screenshot from 2025-09-27 17-00-56" src="https://github.com/user-attachments/assets/1eaa3123-44fa-458c-abb1-4d2d6efde97b" />
&nbsp;&nbsp;&nbsp;&nbsp;
<img width="1843" height="929" alt="Screenshot from 2025-09-27 17-01-04" src="https://github.com/user-attachments/assets/251f42de-8633-4b76-96d6-8bd70d90f7f4" />



## 📊 Data Generation

The system includes a comprehensive data generation script using Faker library:

### Running Data Generator
```bash
# Method 1: Django shell
python manage.py shell
>>> exec(open('utils/data_generator.py').read())

# Method 2: Create management command
python manage.py generate_sample_data --employees=50 --departments=8
```

### Generated Data Structure
- **5 Departments**: IT, HR, Finance, Marketing, Operations
- **25 Employees**: 4-5 per department with realistic data
- **50+ Performance Records**: 2 reviews per employee
- **750+ Attendance Records**: Last 30 days for each employee

### Sample Data Features
- Realistic names and email addresses
- Appropriate salary ranges by position
- Logical hire dates and performance scores
- Varied attendance patterns with realistic absences

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test employees
python manage.py test department

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```



## 🚀 Deployment

### Environment Setup
```bash
# Production environment variables
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECRET_KEY=your-production-secret-key

# Database (production)
DB_NAME=employee_management_prod
DB_USER=prod_user
DB_PASSWORD=secure-production-password
DB_HOST=your-db-host
DB_PORT=5432
```



## 📝 Usage Examples

### Complete Workflow Example

```bash
# 1. Authenticate
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "yourpassword"}'

# Response: {"token": "abc123...", "user_id": 1, "username": "admin"}

# 2. Create Department
curl -X POST http://localhost:8000/api/departments/ \
  -H "Authorization: Token abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Data Science",
    "code": "DS",
    "budget": "800000.00",
    "location": "Building B, Floor 2"
  }'

# 3. Create Employee
curl -X POST http://localhost:8000/api/employees/ \
  -H "Authorization: Token abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "EMP100",
    "full_name": "Alice Johnson",
    "email": "alice.johnson@company.com",
    "department": 1,
    "position": "Data Scientist",
    "salary": "95000.00",
    "hire_date": "2024-03-01"
  }'

# 4. Get Analytics Data
curl -X GET http://localhost:8000/api/analytics/summary/ \
  -H "Authorization: Token abc123..."

# 5. Export Data
curl -X GET "http://localhost:8000/api/analytics/export/?format=csv" \
  -H "Authorization: Token abc123..." \
  -o analytics_export.csv
```


```




## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Employee Management System

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 📞 Support

If you need help or have questions:

1. **Documentation**: Check this README and the API documentation at `/swagger/`
2. **Issues**: Report bugs or request features on GitHub Issues
3. **Discussions**: Join community discussions on GitHub Discussions
4. **Email**: Contact the maintainers at support@yourcompany.com


---

**Built with ❤️ using Django, PostgreSQL, and modern web technologies.**

For more information, visit our [documentation](https://your-docs-site.com) or [GitHub repository](https://github.com/yourusername/employee_management_system).
