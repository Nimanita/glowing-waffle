#!/usr/bin/env bash
# exit on error
set -o errexit

echo "============================================"
echo "Building Django Application..."
echo "============================================"

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "Setting up admin user..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('mamata', 'admin@example.com', 'Mamata@12345')
    print('Superuser created: mamata / Mamata@12345')
EOF

# Generate sample data if database is empty
echo "Checking for sample data..."
python manage.py shell <<EOF
from employees.models import Employee
if Employee.objects.count() == 0:
    print('Generating sample data...')
    exec(open('utils/data_generator.py').read())
    print('Sample data generated!')
else:
    print('Data already exists, skipping generation.')
EOF

echo "============================================"
echo "Build complete!"
echo "============================================"