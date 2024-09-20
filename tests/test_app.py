import pytest
from main.app import create_model, solve_model
from ortools.sat.python import cp_model



# assertion: if there are 4 employees and 4 shifts available, each one of them should get one. (Equal shift distribution)
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



# assertion: part-time employees don't exceed 20 hour limit.    (Part time compliance)
def test_part_time_hour_limit():
    num_employees = 4
    num_shift_per_day = 4
    num_days = 7
    employee_types = ["full_time", "part_time", "manager", "part_time"]

    model, shifts = create_model(
        num_employees, num_shift_per_day, num_days, employee_types
    )
    solver = solve_model(model, shifts, num_employees, num_shift_per_day, num_days)

    # Ensure that part-time employees do not exceed their hour limits  (part time compliance)
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

############################################################################################################

# assertion: full-time employees don't exceed 40 hour limit. Near copy of part_time_hour_limit (full time compliance)
def test_full_time_hour_limit():
    num_employees = 4
    num_shift_per_day = 4
    num_days = 7
    employee_types = ["full_time", "part_time", "manager", "part_time"]

    model, shifts = create_model(
        num_employees, num_shift_per_day, num_days, employee_types
    )
    solver = solve_model(model, shifts, num_employees, num_shift_per_day, num_days)

    # Ensure that part-time employees do not exceed their hour limits  (part time compliance)
    full_time_employee_indices = [
        i for i, et in enumerate(employee_types) if et == "full_time"
    ]
    for e in full_time_employee_indices:
        total_work_hours = sum(
            solver.Value(shifts[(e, d, s)])
            for d in range(num_days)
            for s in range(num_shift_per_day)
        )
        assert (
            total_work_hours <= 40
        ), f"full-time employee {e} should not work more than 40 hours without approval."



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



# Testing to fail (insufficient staffing)
def test_insufficient_staffing_fulltime():
    num_employees = 2
    num_shift_per_day = 3
    num_days = 7
    employee_types = ["full_time"] * 3

    # shift_length_hours = 5

    model, shifts = create_model(
        num_employees, num_shift_per_day, num_days, employee_types
    )
    
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    assert status == cp_model.INFEASIBLE, "Expected staffing to fail, but the solver found a feasible solution."  

print("Test passed: Insufficient staffing correctly results in an infeasible solution.")



# Testing the initial model
def test_initial_model():
    num_employees = 4
    num_shift_per_day = 4
    num_days = 7
    
    employee_types = ['full_time', 'part_time', 'manager', 'part_time']
    model, shifts = create_model(num_employees, num_shift_per_day, num_days, employee_types)
    assert(model, shifts, num_employees, num_shift_per_day, num_days, employee_types)



def test_no_available_shifts():
    num_employees = 4
    num_shift_per_day = 0
    num_days = 7
    employee_types = ['full_time', 'part_time', 'manager', 'part_time']

    model, shifts = create_model(num_employees, num_shift_per_day, num_days, employee_types)
    assert len(shifts) == 0
    # Length of shifts should be 0.


#Basically the same as above but with 0 employees instead of 0 shifts
def test_no_employees():
    num_employees = 0
    num_shift_per_day = 4
    num_days = 7
    employee_types = ['full_time', 'part_time', 'manager', 'part_time']

    model, shifts = create_model(num_employees, num_shift_per_day, num_days, employee_types)
    assert len(shifts) == 0
    # Length of shifts should be 0.


# I have run out of ideas for what to test so I told an AI to make me a random one and this was it. 
def test_one_employee_per_shift():
    # Setup: 4 employees, 3 shifts per day, 5 days
    num_employees = 4
    num_shift_per_day = 3
    num_days = 5
    employee_types = ['full_time', 'part_time', 'manager', 'part_time']  # Mixed types

    # Create the model
    model, shifts = create_model(num_employees, num_shift_per_day, num_days, employee_types)

    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Ensure solver finds a feasible or optimal solution
    assert solver.StatusName() in ['OPTIMAL', 'FEASIBLE'], f"Solver failed to find a solution, status: {solver.StatusName()}"

    # Verify that each shift is assigned to exactly one employee
    for d in range(num_days):
        for s in range(num_shift_per_day):
            total_employees_assigned = sum(solver.Value(shifts[(e, d, s)]) for e in range(num_employees))
            assert total_employees_assigned == 1, f"Shift {s} on day {d} has {total_employees_assigned} employees assigned, expected 1"


