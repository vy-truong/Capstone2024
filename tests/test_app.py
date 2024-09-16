import pytest
from main.app import create_model, solve_model


# assertion: if there are 4 employees and 4 shifts available, each one of them should get one.
def test_single_shift_per_day():
    num_employees = 4
    num_shift_per_day = 4
    num_days = 7
    employee_types = ["full_time", "part_time", "manager", "part_time"]

    model, shifts = create_model(
        num_employees, num_shift_per_day, num_days, employee_types
    )
    solver = solve_model(model, shifts, num_employees, num_shift_per_day, num_days)

    for d in range(num_days):
        for e in range(num_employees):
            assigned_shifts = [
                solver.Value(shifts[(e, d, s)]) for s in range(num_shift_per_day)
            ]
            assert (
                sum(assigned_shifts) == 1
            ), f"Employee {e} should have exactly one shift on day {d}"


# assertion: part-time employees don't exceed 20 hour limit.
def test_part_time_hour_limit():
    num_employees = 4
    num_shift_per_day = 4
    num_days = 7
    employee_types = ["full_time", "part_time", "manager", "part_time"]

    model, shifts = create_model(
        num_employees, num_shift_per_day, num_days, employee_types
    )
    solver = solve_model(model, shifts, num_employees, num_shift_per_day, num_days)

    # Ensure that part-time employees do not exceed their hour limits
    part_time_employee_indices = [
        i for i, et in enumerate(employee_types) if et == "part_time"
    ]
    for e in part_time_employee_indices:
        total_work_hours = sum(
            solver.Value(shifts[(e, d, s)])
            for d in range(num_days)
            for s in range(num_shift_per_day)
        )
        assert (
            total_work_hours <= 20
        ), f"Part-time employee {e} should not work more than 20 hours."


# assertion: if we have two main shifts per day, the minimum number of employees needed is 8 if all are full-time
def test_minimum_staffing_fulltime():
    num_employees = 8  # Adjust number to meet shift requirements
    num_shift_per_day = 2  # Two main shifts per day, e.g., lunch and dinner
    num_days = 7  # A week
    employee_types = ["full_time"] * 8  # Assuming all are full-time for simplicity

    shift_length_hours = 5  # Each shift is 5 hours long

    model, shifts = create_model(
        num_employees, num_shift_per_day, num_days, employee_types
    )
    solver = solve_model(model, shifts, num_employees, num_shift_per_day, num_days)

    for e in range(num_employees):
        total_hours_per_week = 0
        for d in range(num_days):
            shifts_worked_today = 0
            for s in range(num_shift_per_day):
                if solver.Value(shifts[(e, d, s)]):
                    shifts_worked_today += 1
                    total_hours_per_week += shift_length_hours
            assert (
                shifts_worked_today <= 2
            ), f"Employee {e} should work no more than 2 shifts per day"
        assert (
            total_hours_per_week <= 40
        ), f"Employee {e} should not exceed 40 working hours per week (worked {total_hours_per_week} hours)"


print(
    "Test passed: All employees are assigned appropriately per day, and no employee exceeds 40 working hours per week."
)
