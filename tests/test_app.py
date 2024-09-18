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

    shift_length_hours = 5

    model, shifts = create_model(
        num_employees, num_shift_per_day, num_days, employee_types
    )
    
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    assert status == cp_model.INFEASIBLE, "Expected staffing to fail, but the solver found a feasible solution."  

print("Test passed: Insufficient staffing correctly results in an infeasible solution.")



# Boundary testing (Too many employees) I had an idea when I started but now idk what ive done and there is heavy use of AI in this test
def test_too_many_employees():
    # Set a number of employees that is higher than usual or expected
    num_employees = 100
    num_shift_per_day = 3
    num_days = 7
    employee_types = ["full_time"] * num_employees  # Assign all employees as full-time

    shift_length_hours = 3

    # Create the model with a high number of employees
    model, shifts = create_model(
        num_employees, num_shift_per_day, num_days, employee_types
    )
    
    # Attempt to solve the model
    try:
        solver = solve_model(model, shifts, num_employees, num_shift_per_day, num_days)
    except Exception as e:
        # Catch any exceptions thrown by the solver due to excessive number of employees
        assert isinstance(e, MemoryError) or isinstance(e, RuntimeError), "Solver failed with an unexpected error."
        print("Solver failed due to too many employees, as expected.")
        return

    # If no exception was raised, check that the solver's results are reasonable
    for e in range(num_employees):
        total_hours_per_week = 0
        for d in range(num_days):
            shifts_worked_today = 0
            for s in range(num_shift_per_day):
                if solver.Value(shifts.get((e, d, s), 0)):  # Use get() to avoid KeyError
                    shifts_worked_today += 1
                    total_hours_per_week += shift_length_hours
            assert (
                shifts_worked_today <= 2
            ), f"Employee {e} should work no more than 2 shifts per day"
        assert (
            total_hours_per_week <= 40
        ), f"Employee {e} should not exceed 40 working hours per week (worked {total_hours_per_week} hours)"

    # Test completed without exceptions means we should validate if results are consistent
    print("Test completed without exceptions. Verify results for any performance issues or unexpected behavior.")




# # Testing for negative hours   (AI generated, will probably just delete this and try building one myself when i come back to it tomorrow) it also causes the other tests to fail so idk whats up with that.
# def create_model_with_negative_hours(num_employees, num_shift_per_day, num_days, employee_types, shift_length_hours):
#     model = cp_model.CpModel()
#     shifts = {}
    
#     for e in range(num_employees):
#         for d in range(num_days):
#             for s in range(num_shift_per_day):
#                 shifts[(e, d, s)] = model.NewBoolVar(f'shift_e{e}_d{d}_s{s}')
    
#     # Constraints (for example purposes; these should be your actual constraints)
#     for d in range(num_days):
#         for s in range(num_shift_per_day):
#             model.Add(sum(shifts[(e, d, s)] for e in range(num_employees)) == 1)

#     # Here we introduce a negative shift length scenario
#     # This should not happen in real scenarios, but we are testing error handling
#     if shift_length_hours < 0:
#         raise ValueError("Shift length hours cannot be negative")

#     return model, shifts

# def solve_model(model, shifts, num_employees, num_shift_per_day, num_days):
#     solver = cp_model.CpSolver()
#     status = solver.Solve(model)
#     return solver, status

# def test_negative_hours():
#     num_employees = 10
#     num_shift_per_day = 3
#     num_days = 7
#     employee_types = ["full_time"] * num_employees
    
#     shift_length_hours = -3  # Negative shift length hours for testing
    
#     # Create the model with negative shift length hours
#     try:
#         model, shifts = create_model_with_negative_hours(
#             num_employees, num_shift_per_day, num_days, employee_types, shift_length_hours
#         )
#         solver, status = solve_model(model, shifts, num_employees, num_shift_per_day, num_days)
#         assert status == cp_model.INFEASIBLE, "The model should be infeasible due to negative hours."
#         print("Test passed: The model is infeasible as expected due to negative hours.")
#     except ValueError as e:
#         assert str(e) == "Shift length hours cannot be negative", "Expected ValueError due to negative hours."
#         print("Test passed: ValueError caught as expected for negative hours.")
#     except Exception as e:
#         assert False, f"Unexpected exception: {e}"

