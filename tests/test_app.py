import pytest
from main.app import create_model, solve_model

# Test to ensure employees are assigned shifts correctly.
def test_single_shift_per_day():
    num_employees = 4
    num_shift_per_day = 4
    num_days = 7
    employee_types = ['full_time', 'part_time', 'manager', 'part_time']

    model, shifts = create_model(num_employees, num_shift_per_day, num_days, employee_types)
    solver = solve_model(model, shifts, num_employees, num_shift_per_day, num_days)

    for d in range(num_days):
        for e in range(num_employees):
            assigned_shifts = [solver.Value(shifts[(e, d, s)]) for s in range(num_shift_per_day)]
            assert sum(assigned_shifts) == 1, f"Employee {e} should have exactly one shift on day {d}"

# Test that ensures part-time employees don't exceed their hour limits
def test_part_time_hour_limit():
    num_employees = 4
    num_shift_per_day = 4
    num_days = 7
    employee_types = ['full_time', 'part_time', 'manager', 'part_time']

    model, shifts = create_model(num_employees, num_shift_per_day, num_days, employee_types)
    solver = solve_model(model, shifts, num_employees, num_shift_per_day, num_days)

    # Ensure that part-time employees do not exceed their hour limits
    part_time_employee_indices = [i for i, et in enumerate(employee_types) if et == 'part_time']
    for e in part_time_employee_indices:
        total_work_hours = sum(solver.Value(shifts[(e, d, s)]) for d in range(num_days) for s in range(num_shift_per_day))
        assert total_work_hours <= 20, f"Part-time employee {e} should not work more than 20 hours."
