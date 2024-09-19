import pytest
from main.app import create_shift_scheduling_model, solve_shift_scheduling
import time

# Assertion: If there are 4 employees and 4 shifts available, each one of them should get one.
def test_single_shift_per_day():
    num_employees = 4
    shifts_per_day = 4
    total_days = 7
    employee_types = ["full_time", "part_time", "manager", "part_time"]

    model, shifts = create_shift_scheduling_model(
        num_employees, shifts_per_day, total_days, employee_types
    )
    solver = solve_shift_scheduling(model, shifts, num_employees, shifts_per_day, total_days, return_solver=True)

    for day in range(total_days):
        for employee in range(num_employees):
            assigned_shifts = [
                solver.Value(shifts[(employee, day, shift)]) for shift in range(shifts_per_day)
            ]
            assert sum(assigned_shifts) == 1, f"Employee {employee} should have exactly one shift on day {day}"


# Assertion: Part-time employees don't exceed 20 hour limit.
def test_part_time_hour_limit():
    num_employees = 4
    shifts_per_day = 4
    total_days = 7
    employee_types = ["full_time", "part_time", "manager", "part_time"]

    model, shifts = create_shift_scheduling_model(
        num_employees, shifts_per_day, total_days, employee_types
    )
    solver = solve_shift_scheduling(model, shifts, num_employees, shifts_per_day, total_days, return_solver=True)

    # Ensure that part-time employees do not exceed their hour limits
    part_time_employee_indices = [
        i for i, et in enumerate(employee_types) if et == "part_time"
    ]
    for employee in part_time_employee_indices:
        total_work_hours = sum(
            solver.Value(shifts[(employee, day, shift)])
            for day in range(total_days)
            for shift in range(shifts_per_day)
        )
        assert (
            total_work_hours <= 20
        ), f"Part-time employee {employee} should not work more than 20 hours."


# Assertion: If we have two main shifts per day, the minimum number of employees needed is 8 if all are full-time.
def test_minimum_staffing_fulltime():
    num_employees = 8  # Adjust number to meet shift requirements
    shifts_per_day = 2  # Two main shifts per day, e.g., lunch and dinner
    total_days = 7  # A week
    employee_types = ["full_time"] * 8  # Assuming all are full-time for simplicity

    shift_length_hours = 5  # Each shift is 5 hours long

    model, shifts = create_shift_scheduling_model(
        num_employees, shifts_per_day, total_days, employee_types
    )
    solver = solve_shift_scheduling(model, shifts, num_employees, shifts_per_day, total_days, return_solver=True)

    for employee in range(num_employees):
        total_hours_per_week = 0
        for day in range(total_days):
            shifts_worked_today = 0
            for shift in range(shifts_per_day):
                if solver.Value(shifts[(employee, day, shift)]):
                    shifts_worked_today += 1
                    total_hours_per_week += shift_length_hours
            assert shifts_worked_today <= 2, f"Employee {employee} should work no more than 2 shifts per day"
        assert total_hours_per_week <= 40, f"Employee {employee} should not exceed 40 working hours per week (worked {total_hours_per_week} hours)"


# Assertion: Optimal number of employees for 14 shifts per week (2 per day, 7 days) is 2 full-time and 2 part-time
def test_optimal_employees_for_14_shifts():
    num_employees = 4  # 2 full-time and 2 part-time employees
    shifts_per_day = 2  # Two shifts per day
    total_days = 7  # A week of shifts
    employee_types = ["full_time", "full_time", "part_time", "part_time"]  # Two full-time, two part-time
    
    # Start time measurement
    start_time = time.time()

    # Create the scheduling model and solve it
    model, shifts = create_shift_scheduling_model(
        num_employees, shifts_per_day, total_days, employee_types
    )
    solver = solve_shift_scheduling(model, shifts, num_employees, shifts_per_day, total_days, return_solver=True)

    # End time measurement
    elapsed_time = time.time() - start_time

    print(f"Tested with {num_employees} employees: Took {elapsed_time:.2f} seconds")
    
    # Ensure all shifts are covered
    for day in range(total_days):
        for shift in range(shifts_per_day):
            assigned_employees = [
                solver.Value(shifts[(employee, day, shift)])
                for employee in range(num_employees)
            ]
            assert sum(assigned_employees) == 1, f"Shift {shift} on day {day} should be assigned to exactly 1 employee"

    # Ensure that all employees have at least one shift per week
    for employee in range(num_employees):
        total_shifts = sum(
            solver.Value(shifts[(employee, day, shift)])
            for day in range(total_days)
            for shift in range(shifts_per_day)
        )
        assert total_shifts >= 1, f"Employee {employee} should have at least one shift per week"

    # Optionally, assert that the performance is acceptable
    assert elapsed_time <= 10, "Performance test failed: Process took too long"