import os
import sys
import logging
import random
from pathlib import Path
from datetime import date, timedelta, datetime, time

from faker import Faker

# ─── Ensure project root is on PYTHONPATH ─────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ─── Django setup ─────────────────────────────────────────────────────
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django

django.setup()

# ─── Model imports ────────────────────────────────────────────────────
from departments.models import Department
from employees.models   import Employee
from analytics.models   import Performance, Attendance

# ─── Logging config ───────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def run():
    logger.info("🔄 Starting Faker data generation…")
    fake = Faker()
    fake.unique.clear()

    # ─── 1. Departments ────────────────────────────────────────────────
    dept_defs = [
        ("IT",        "IT01"),
        ("HR",        "HR01"),
        ("Finance",   "FN01"),
        ("Marketing", "MK01"),
        ("Operations","OP01"),
    ]
    departments = []
    for name, code in dept_defs:
        dept, created = Department.objects.get_or_create(
            name=name,
            code=code,
            defaults={
                "budget":   round(random.uniform(50_000, 200_000), 2),
                "location": fake.city(),
            },
        )
        status = "Created" if created else "Found"
        logger.info(f"✅ {status} Department: {dept.name} ({dept.code})")
        departments.append(dept)

    # ─── 2. Employees per Department ──────────────────────────────────
    employees = []
    for dept in departments:
        for _ in range(4):
            emp = Employee.objects.create(
                employee_id=fake.unique.bothify(text="EMP-####"),
                full_name=fake.name(),
                email=fake.unique.email(),
                department=dept,
                position=fake.job(),
                salary=round(random.uniform(30_000, 120_000), 2),
                hire_date=fake.date_between(start_date="-2y", end_date="today"),
            )
            logger.info(f"   • Created Employee: {emp.employee_id} — {emp.full_name}")
            employees.append(emp)

    # ─── 3. Performance Records ────────────────────────────────────────
    logger.info("🧾 Generating Performance records…")
    review_periods = ["2024-Q3", "2024-Q4"]
    for emp in employees:
        for period in review_periods:
            perf = Performance.objects.create(
                employee=emp,
                review_period=period,
                overall_score=round(random.uniform(1, 5), 2),
                technical_score=round(random.uniform(1, 5), 2),
                communication_score=round(random.uniform(1, 5), 2),
                teamwork_score=round(random.uniform(1, 5), 2),
                review_date=fake.date_between(start_date="-6M", end_date="today"),
            )
            logger.info(f"   • {emp.employee_id} → Performance {period}: {perf.overall_score}")

    
    # ─── 4. Attendance Records ─────────────────────────────────────────
    logger.info("🗓️  Generating Attendance records (last 30 days)…")
    start_day = date.today() - timedelta(days=30)

    for emp in employees:
        for offset in range(31):
            day = start_day + timedelta(days=offset)
            status = random.choices(
                ["PRESENT", "ABSENT", "LATE"], weights=[0.8, 0.1, 0.1]
            )[0]

            if status == "ABSENT":
                # assign a placeholder check_in_time (00:00) rather than None
                check_in = time(hour=0, minute=0)
                check_out = None                 # allowed to be null
                hours = 0.0
            else:
                # normal present/late case
                check_in = time(hour=random.randint(8,10), minute=random.randint(0,59))
                hours = round(random.uniform(6, 9), 2)
                dt_in = datetime.combine(day, check_in)
                dt_out = dt_in + timedelta(hours=hours)
                check_out = dt_out.time()

            Attendance.objects.create(
                employee=emp,
                date=day,
                check_in_time=check_in,      # never null now
                check_out_time=check_out,
                total_hours=hours,
                status=status,
            )

        logger.info(f"   • {emp.employee_id} → Attendance for 31 days")
    logger.info("🎉 All data generated successfully!")

# ─── Execute on import or direct run ─────────────────────────────────
if __name__ == "__main__":
    run()
else:
    run()
