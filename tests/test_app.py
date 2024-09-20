import pytest
from ortools.sat.python import cp_model

# Giả sử đây là hàm em dùng để tạo mô hình xếp ca
from main.app import create_shift_scheduling_model, solve_shift_scheduling

# test case 1: check to make sure full time worker work at least 40 hours 
def test_full_time_hours():
    num_employees = 6
    shifts_per_day = 4 
    total_days = 5 
    employee_types = ['full_time','full_time','full_time','full_time','part_time', 'part_time']


    # create model to organize these shit and store them or watever 
    model, shifts = create_shift_scheduling_model(num_employees, shifts_per_day, total_days, employee_types
    )

    # solver to do result 
    solver = solve_shift_scheduling(model, shifts, num_employees, shifts_per_day, total_days,  return_solver=True)

    #check full time 
    for e in range(3): 
        hours_worked = sum(solver.Value(shifts[(e, d, s)]) * 8 for d in range(total_days) for s in range(shifts_per_day))
        assert hours_worked == 40, f"{hours_worked} full time work less than 40 {e}"
        

def test_part_time_over():
    num_employees = 6
    shifts_per_day = 4
    total_days = 5
    employee_types = ['full_time','full_time','full_time','part_time','part_time', 'part_time']

    model, shifts = create_shift_scheduling_model(num_employees, shifts_per_day, total_days, employee_types)
    solver = solve_shift_scheduling(model, shifts, num_employees, shifts_per_day, total_days, return_solver=True)
    for e in range(3, 5):  
        hours_worked = sum(solver.Value(shifts[(e, d, s)]) * 4 for d in range(total_days) for s in range(shifts_per_day))
        assert hours_worked <= 20, f"part time over 20 hours {e}"


# Expectation: When there are more part-time workers than full-time workers, and the system cannot find a valid schedule (e.g., full-time workers can't cover enough shifts to meet 40 hours), the solver should return no solution.
# def test_more_part_time_than_full_time():
#     # Setup: 6 employees, 5 part-time and 1 full-time (expected no solution)
#     num_employees = 3
#     shifts_per_day = 7
#     total_days = 7
#     employee_types = ['part_time', 'part_time', 'part_time']

#     # Create the scheduling model
#     model, shifts = create_shift_scheduling_model(num_employees, shifts_per_day, total_days, employee_types)

#     # Solve the scheduling problem
#     solver = cp_model.CpSolver()
#     status = solver.Solve(model)

#     # Since there are too many part-time employees, and not enough full-time, expect no solution
#     assert status == cp_model.INFEASIBLE, "Expected no solution, but a solution was found!"


# Expectation: When there are more part-time workers than full-time workers, and the system cannot find a valid schedule (e.g., full-time workers can't cover enough shifts to meet 40 hours), the solver should return no solution.


def test_more_part_time_than_full_time():
    # Setup: 6 employees, 5 part-time and 1 full-time (expected no solution)
    num_employees = 6
    shifts_per_day = 4
    total_days = 5
    full_shift = 8
    half_shift = 4
    employee_types = ['full_time', 'part_time', 'part_time', 'part_time', 'part_time', 'part_time']

    # Create the scheduling model
    model, shifts = create_shift_scheduling_model(num_employees, shifts_per_day, total_days, employee_types)

    # Enforce full-time must work at least 40 hours
    for e in range(num_employees):
        if employee_types[e] == 'full_time':
            model.Add(sum(shifts[(e, d, s)] * full_shift for d in range(total_days) for s in range(shifts_per_day)) == 40)

    # Enforce part-time cannot work more than 20 hours
    for e in range(num_employees):
        if employee_types[e] == 'part_time':
            model.Add(sum(shifts[(e, d, s)] * half_shift for d in range(total_days) for s in range(shifts_per_day)) <= 20)

    # Solve the scheduling problem
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Since there are too many part-time employees and not enough full-time, expect no solution
    assert status == cp_model.INFEASIBLE, "Expected no solution, but a solution was found!"


def test_not_enough():
    # Setup: 1 part-time employee (expected no solution)
    num_employees = 1
    shifts_per_day = 4
    total_days = 5
    full_shift = 8
    half_shift = 4
    employee_types = ['part_time']

    # Create the scheduling model
    model, shifts = create_shift_scheduling_model(num_employees, shifts_per_day, total_days, employee_types)

    # Ensure the part-time employee works exactly 20 hours (since half_shift = 4, this is 5 shifts)
    for e in range(num_employees):
        if employee_types[e] == 'part_time':
            model.Add(sum(shifts[(e, d, s)] * half_shift for e in range(num_employees) for d in range(total_days) for s in range(shifts_per_day)) == 20)

    # Solve the scheduling problem
    solver = solve_shift_scheduling(model, shifts, num_employees, shifts_per_day, total_days, return_solver=True)
    status = solver.Solve(model)

    # Expect no solution because 1 part-time worker can't cover all shifts
    assert status == cp_model.INFEASIBLE, "Expected no solution, but a solution was found!"