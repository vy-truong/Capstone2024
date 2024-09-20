import pytest
from ortools.sat.python import cp_model
from main.app import create_shift_scheduling_model, solve_shift_scheduling

# Test case: Each employee should have at most one shift per day
def test_single_shift_per_day():
    num_employees = 4
    shifts_per_day = 4
    total_days = 7
    employee_types = ["full_time", "part_time", "full_time", "part_time"]

    model, shifts = create_shift_scheduling_model(
        num_employees, shifts_per_day, total_days, employee_types
    )
    solver = solve_shift_scheduling(model, shifts, num_employees, shifts_per_day, total_days, return_solver=True)

    for day in range(total_days):
        for employee in range(num_employees):
            assigned_shifts = [
                solver.Value(shifts[(employee, day, shift)]) for shift in range(shifts_per_day)
            ]
            assert (
                sum(assigned_shifts) <= 1
            ), f"Employee {employee} should have at most one shift on day {day}"

# Test case: Part-time employees should not exceed 20 hours per week
def test_part_time_hour_limit():
    num_employees = 4
    shifts_per_day = 4
    total_days = 7
    employee_types = ["full_time", "part_time", "full_time", "part_time"]

    model, shifts = create_shift_scheduling_model(
        num_employees, shifts_per_day, total_days, employee_types
    )
    solver = solve_shift_scheduling(model, shifts, num_employees, shifts_per_day, total_days, return_solver=True)

    part_time_employee_indices = [
        i for i, et in enumerate(employee_types) if et == "part_time"
    ]
    for employee in part_time_employee_indices:
        total_work_hours = sum(
            solver.Value(shifts[(employee, day, shift)]) * 4  # Half shift is 4 hours
            for day in range(total_days)
            for shift in range(shifts_per_day)
        )
        assert (
            total_work_hours <= 20
        ), f"Part-time employee {employee} should not work more than 20 hours."

# Test case: Full-time employees should not exceed 40 hours per week
def test_full_time_hour_limit():
    num_employees = 4
    shifts_per_day = 4
    total_days = 7
    employee_types = ["full_time", "part_time", "full_time", "part_time"]

    model, shifts = create_shift_scheduling_model(
        num_employees, shifts_per_day, total_days, employee_types
    )
    solver = solve_shift_scheduling(model, shifts, num_employees, shifts_per_day, total_days, return_solver=True)

    full_time_employee_indices = [
        i for i, et in enumerate(employee_types) if et == "full_time"
    ]
    for employee in full_time_employee_indices:
        total_work_hours = sum(
            solver.Value(shifts[(employee, day, shift)]) * 8  # Full shift is 8 hours
            for day in range(total_days)
            for shift in range(shifts_per_day)
        )
        assert (
            total_work_hours <= 40
        ), f"Full-time employee {employee} should not work more than 40 hours."

# Test case: Full-time workers should work at least 40 hours
def test_full_time_hours():
    num_employees = 6
    shifts_per_day = 4
    total_days = 5
    employee_types = ['full_time', 'full_time', 'full_time', 'full_time', 'part_time', 'part_time']

    model, shifts = create_shift_scheduling_model(num_employees, shifts_per_day, total_days, employee_types)
    solver = solve_shift_scheduling(model, shifts, num_employees, shifts_per_day, total_days, return_solver=True)

    for employee in range(4):  # First four are full-time
        hours_worked = sum(
            solver.Value(shifts[(employee, day, shift)]) * 8
            for day in range(total_days)
            for shift in range(shifts_per_day)
        )
        assert hours_worked >= 40, f"Full-time employee {employee} should work at least 40 hours but worked {hours_worked} hours."

# Test case: Part-time employees should not work over 20 hours
def test_part_time_over():
    num_employees = 6
    shifts_per_day = 4
    total_days = 5
    employee_types = ['full_time', 'full_time', 'full_time', 'part_time', 'part_time', 'part_time']

    model, shifts = create_shift_scheduling_model(num_employees, shifts_per_day, total_days, employee_types)
    solver = solve_shift_scheduling(model, shifts, num_employees, shifts_per_day, total_days, return_solver=True)

    for employee in range(3, 6):  # Employees 3 to 5 are part-time
        hours_worked = sum(
            solver.Value(shifts[(employee, day, shift)]) * 4
            for day in range(total_days)
            for shift in range(shifts_per_day)
        )
        assert hours_worked <= 20, f"Part-time employee {employee} should not work more than 20 hours but worked {hours_worked} hours."

# Test case: Expect no solution when there are too many part-time employees and not enough full-time
def test_more_part_time_than_full_time():
    num_employees = 6
    shifts_per_day = 4
    total_days = 5
    employee_types = ['full_time', 'part_time', 'part_time', 'part_time', 'part_time', 'part_time']

    model, shifts = create_shift_scheduling_model(num_employees, shifts_per_day, total_days, employee_types)

    # Enforce constraints
    for employee in range(num_employees):
        if employee_types[employee] == 'full_time':
            model.Add(
                sum(shifts[(employee, day, shift)] * 8 for day in range(total_days) for shift in range(shifts_per_day)) == 40
            )
        elif employee_types[employee] == 'part_time':
            model.Add(
                sum(shifts[(employee, day, shift)] * 4 for day in range(total_days) for shift in range(shifts_per_day)) <= 20
            )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    assert status == cp_model.INFEASIBLE, "Expected no solution, but a solution was found!"

# Test case: Not enough employees to cover all shifts
def test_not_enough():
    num_employees = 1
    shifts_per_day = 4
    total_days = 5
    employee_types = ['part_time']

    model, shifts = create_shift_scheduling_model(num_employees, shifts_per_day, total_days, employee_types)

    # Enforce constraints
    model.Add(
        sum(shifts[(0, day, shift)] * 4 for day in range(total_days) for shift in range(shifts_per_day)) == 20
    )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    assert status == cp_model.INFEASIBLE, "Expected no solution, but a solution was found!"

# Test case: Each shift is assigned to exactly one employee
def test_one_employee_per_shift():
    num_employees = 4
    shifts_per_day = 3
    total_days = 5
    employee_types = ['full_time', 'part_time', 'full_time', 'part_time']

    model, shifts = create_shift_scheduling_model(num_employees, shifts_per_day, total_days, employee_types)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    assert status in [cp_model.OPTIMAL, cp_model.FEASIBLE], f"Solver failed to find a solution, status: {solver.StatusName()}"

    for day in range(total_days):
        for shift in range(shifts_per_day):
            total_employees_assigned = sum(solver.Value(shifts[(employee, day, shift)]) for employee in range(num_employees))
            assert total_employees_assigned == 1, f"Shift {shift} on day {day} has {total_employees_assigned} employees assigned, expected 1"

# Test case: Minimum staffing with full-time employees
def test_minimum_staffing_fulltime():
    num_employees = 8
    shifts_per_day = 2
    total_days = 7
    employee_types = ["full_time"] * num_employees

    model, shifts = create_shift_scheduling_model(num_employees, shifts_per_day, total_days, employee_types)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    assert status in [cp_model.OPTIMAL, cp_model.FEASIBLE], "Solver failed to find a solution"

    for employee in range(num_employees):
        total_hours_per_week = sum(
            solver.Value(shifts[(employee, day, shift)]) * 8
            for day in range(total_days)
            for shift in range(shifts_per_day)
        )
        assert (
            total_hours_per_week <= 40
        ), f"Employee {employee} should not exceed 40 working hours per week (worked {total_hours_per_week} hours)"

# Test case: Insufficient staffing results in infeasible solution
def test_insufficient_staffing_fulltime():
    num_employees = 2
    shifts_per_day = 3
    total_days = 7
    employee_types = ["full_time"] * num_employees

    model, shifts = create_shift_scheduling_model(num_employees, shifts_per_day, total_days, employee_types)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    assert status == cp_model.INFEASIBLE, "Expected no solution due to insufficient staffing, but a solution was found!"

# Test case: Initial model creation
def test_initial_model():
    num_employees = 4
    shifts_per_day = 4
    total_days = 7
    employee_types = ['full_time', 'part_time', 'full_time', 'part_time']

    model, shifts = create_shift_scheduling_model(num_employees, shifts_per_day, total_days, employee_types)
    assert model is not None and shifts is not None, "Model or shifts dictionary is None"

# Test case: No available shifts
def test_no_available_shifts():
    num_employees = 4
    shifts_per_day = 0
    total_days = 7
    employee_types = ['full_time', 'part_time', 'full_time', 'part_time']

    model, shifts = create_shift_scheduling_model(num_employees, shifts_per_day, total_days, employee_types)
    assert len(shifts) == 0, "Shifts dictionary should be empty when there are no shifts per day"

# Test case: No employees
def test_no_employees():
    num_employees = 0
    shifts_per_day = 4
    total_days = 7
    employee_types = []

    model, shifts = create_shift_scheduling_model(num_employees, shifts_per_day, total_days, employee_types)
    assert len(shifts) == 0, "Shifts dictionary should be empty when there are no employees"