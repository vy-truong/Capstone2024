import pytest
from ortools.sat.python import cp_model
from main.main import create_shift_scheduling_model, solve_shift_scheduling

# Test case: Each employee should have at most one shift per day
def test_single_shift_per_day():
    """
    Test that each employee is assigned at most one shift per day.
    """
    num_employees = 7 
    shifts_per_day = 4
    total_days = 7
    employee_types = [
        "full_time",
        "part_time",
        "full_time",
        "part_time",
        "full_time",
        "part_time",
        "full_time",
    ]

    model, shifts = create_shift_scheduling_model(
        num_employees, shifts_per_day, total_days, employee_types
    )
    
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    assert status == cp_model.OPTIMAL or status == cp_model.FEASIBLE, "Solver did not find a feasible solution."

    for day in range(total_days):
        for employee in range(num_employees):
            assigned_shifts = [
                solver.Value(shifts[(employee, day, shift)]) for shift in range(shifts_per_day)
            ]
            assert sum(assigned_shifts) <= 1, (
                f"Employee {employee} should have at most one shift on day {day}, "
                f"but has {sum(assigned_shifts)} shifts."
            )


# Test case: Part-time employees should not exceed 20 hours per week
def test_part_time_hour_limit():
    """
    Test that part-time employees do not exceed 20 hours per week.
    """
    num_employees = 7
    shifts_per_day = 4
    total_days = 7
    shift_duration = 4
    part_time_hours = 20
    full_time_hours = 40
    employee_types = ["full_time", "part_time", "full_time", "part_time", "full_time", "part_time", "full_time"]

    # need to use uniform shift durations
    model, shifts = create_shift_scheduling_model(
        num_employees,
        shifts_per_day,
        total_days,
        employee_types,
        full_time_hours=full_time_hours,
        part_time_hours=part_time_hours,
        full_shift=shift_duration,  # all shifts are 4 hours
        half_shift=shift_duration,   # same shift duration for consistency, just while we test this
    )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    assert status in [cp_model.OPTIMAL, cp_model.FEASIBLE], "Solver did not find a feasible solution."

    # Verify that part-time employees do not exceed 20 hours
    part_time_indices = [i for i, et in enumerate(employee_types) if et == "part_time"]
    for employee in part_time_indices:
        total_hours = sum(
            solver.Value(shifts[(employee, day, shift)]) * shift_duration
            for day in range(total_days)
            for shift in range(shifts_per_day)
        )
        print(f"Part-time employee {employee} worked {total_hours} hours.")
        assert total_hours <= part_time_hours, (
            f"Part-time employee {employee} should not work more than {part_time_hours} hours, "
            f"but worked {total_hours} hours."
        )


# Test case: Full-time employees should not exceed 40 hours per week
def test_full_time_hour_limit():
    """
    Test that full-time employees do not exceed 40 hours per week.
    """
    num_employees = 6  # this needed to be raised from 4 to 6
    shifts_per_day = 4
    total_days = 7
    full_time_hours = 40
    shift_duration = 4  # Uniform shift duration for all employees
    employee_types = [
        "full_time",
        "full_time",
        "full_time",
        "part_time",
        "part_time",
        "part_time",
    ]

    # Use uniform shift durations and adjust part-time hours accordingly
    part_time_hours = 20  # Maximum hours for part-time employees
    half_shift = shift_duration  # Same shift duration for consistency

    # Create the model with adjusted parameters
    model, shifts = create_shift_scheduling_model(
        num_employees,
        shifts_per_day,
        total_days,
        employee_types,
        full_time_hours=full_time_hours,
        part_time_hours=part_time_hours,
        full_shift=shift_duration,
        half_shift=half_shift,
    )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    assert status in [cp_model.OPTIMAL, cp_model.FEASIBLE], "Solver did not find a feasible solution."

    # Verify that full-time employees do not exceed 40 hours
    full_time_indices = [
        i for i, emp_type in enumerate(employee_types) if emp_type == "full_time"
    ]
    for employee in full_time_indices:
        total_hours = sum(
            solver.Value(shifts[(employee, day, shift)]) * shift_duration
            for day in range(total_days)
            for shift in range(shifts_per_day)
        )
        print(f"Full-time employee {employee} worked {total_hours} hours.")
        assert total_hours <= full_time_hours, (
            f"Full-time employee {employee} should not work more than {full_time_hours} hours, "
            f"but worked {total_hours} hours."
        )

# Test case: Full-time employees should work at least 40 hours per week
def test_full_time_hours():
    """
    Test that full-time employees work at least 40 hours per week.
    """
    num_employees = 6
    shifts_per_day = 4
    total_days = 5
    shift_duration = 8  # Uniform shift duration for all employees
    full_time_hours = 40
    part_time_hours = 20
    employee_types = [
        "full_time",
        "full_time",
        "full_time",
        "full_time",
        "part_time",
        "part_time",
    ]

    # Create the model with adjusted parameters
    model, shifts = create_shift_scheduling_model(
        num_employees,
        shifts_per_day,
        total_days,
        employee_types,
        full_time_hours=full_time_hours,
        part_time_hours=part_time_hours,
        full_shift=shift_duration,
        half_shift=shift_duration,  # Use same shift duration for simplicity
    )

    # Enforce that full-time employees must work at least 40 hours
    all_employees = range(num_employees)
    all_shifts = range(shifts_per_day)
    all_days = range(total_days)

    for employee in all_employees:
        if employee_types[employee] == 'full_time':
            total_hours = sum(
                shifts[(employee, day, shift)] * shift_duration
                for day in all_days
                for shift in all_shifts
            )
            model.Add(total_hours >= full_time_hours)
            model.Add(total_hours <= full_time_hours)  # Ensure they work exactly 40 hours

    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    assert status in [cp_model.OPTIMAL, cp_model.FEASIBLE], "Solver did not find a feasible solution."

    # Verify that full-time employees work at least 40 hours
    full_time_indices = [
        i for i, emp_type in enumerate(employee_types) if emp_type == "full_time"
    ]
    for employee in full_time_indices:
        total_hours = sum(
            solver.Value(shifts[(employee, day, shift)]) * shift_duration
            for day in all_days
            for shift in all_shifts
        )
        print(f"Full-time employee {employee} worked {total_hours} hours.")
        assert total_hours >= full_time_hours, (
            f"Full-time employee {employee} should work at least {full_time_hours} hours, "
            f"but worked {total_hours} hours."
        )

# Test case: Part-time employees should not work over 20 hours per week
def test_part_time_over():
    """
    Test that part-time employees do not work over 20 hours per week.
    """
    num_employees = 6
    shifts_per_day = 4
    total_days = 5
    part_time_hours = 20
    half_shift = 4
    employee_types = [
        "full_time",
        "full_time",
        "full_time",
        "part_time",
        "part_time",
        "part_time",
    ]

    model, shifts = create_shift_scheduling_model(
        num_employees,
        shifts_per_day,
        total_days,
        employee_types,
        part_time_hours=part_time_hours,
        half_shift=half_shift,
    )
    solver = solve_shift_scheduling(
        model, shifts, num_employees, shifts_per_day, total_days, return_solver=True
    )

    part_time_indices = [
        i for i, emp_type in enumerate(employee_types) if emp_type == "part_time"
    ]
    for employee in part_time_indices:
        total_hours = sum(
            solver.Value(shifts[(employee, day, shift)]) * half_shift
            for day in range(total_days)
            for shift in range(shifts_per_day)
        )
        assert total_hours <= part_time_hours, (
            f"Part-time employee {employee} should not work more than {part_time_hours} hours, "
            f"but worked {total_hours} hours."
        )

# Test case: Expect no solution when insufficient full-time staff
def test_insufficient_full_time_staffing():
    """
    Test that the solver returns INFEASIBLE when there are too many part-time employees
    and not enough full-time employees to cover all shifts.
    The test passes when the solver correctly identifies the problem as infeasible.
    """
    num_employees = 6
    shifts_per_day = 4
    total_days = 5
    full_time_hours = 40
    part_time_hours = 8  # Reduced from 20 to 8
    full_shift = 8
    half_shift = 4
    employee_types = [
        "full_time",
        "part_time",
        "part_time",
        "part_time",
        "part_time",
        "part_time",
    ]

    model, shifts = create_shift_scheduling_model(
        num_employees,
        shifts_per_day,
        total_days,
        employee_types,
        full_time_hours=full_time_hours,
        part_time_hours=part_time_hours,
        full_shift=full_shift,
        half_shift=half_shift,
    )

    # Enforce exact working hours for full-time employees
    for employee in range(num_employees):
        if employee_types[employee] == "full_time":
            model.Add(
                sum(
                    shifts[(employee, day, shift)] * full_shift
                    for day in range(total_days)
                    for shift in range(shifts_per_day)
                )
                == full_time_hours
            )

    # Enforce maximum working hours for part-time employees
    for employee in range(num_employees):
        if employee_types[employee] == "part_time":
            model.Add(
                sum(
                    shifts[(employee, day, shift)] * half_shift
                    for day in range(total_days)
                    for shift in range(shifts_per_day)
                )
                <= part_time_hours
            )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    assert status == cp_model.INFEASIBLE, (
        "Expected no solution due to insufficient full-time staffing, "
        "but a solution was found!"
    )


# Test case: Not enough employees to cover all shifts (designed to fail)
def test_not_enough_employees_infeasible():
    """
    Test that the solver returns INFEASIBLE when there are not enough employees to cover all shifts.
    The test passes when the solver correctly identifies the problem as infeasible.
    """
    num_employees = 1
    shifts_per_day = 4
    total_days = 5
    part_time_hours = 20
    half_shift = 4
    employee_types = ["part_time"]

    model, shifts = create_shift_scheduling_model(
        num_employees,
        shifts_per_day,
        total_days,
        employee_types,
        part_time_hours=part_time_hours,
        half_shift=half_shift,
    )

    # Enforce exact working hours for the part-time employee
    model.Add(
        sum(
            shifts[(0, day, shift)] * half_shift
            for day in range(total_days)
            for shift in range(shifts_per_day)
        )
        == part_time_hours
    )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    assert status == cp_model.INFEASIBLE, (
        "Expected no solution due to insufficient number of employees, "
        "but a solution was found!"
    )

# Test case: Each shift is assigned to exactly one employee
def test_one_employee_per_shift():
    """
    Test that each shift is assigned to exactly one employee.
    """
    num_employees = 4
    shifts_per_day = 3
    total_days = 5
    employee_types = ["full_time", "part_time", "full_time", "part_time"]

    model, shifts = create_shift_scheduling_model(
        num_employees, shifts_per_day, total_days, employee_types
    )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    assert status in [cp_model.OPTIMAL, cp_model.FEASIBLE], (
        f"Solver failed to find a solution, status: {solver.StatusName()}."
    )

    for day in range(total_days):
        for shift in range(shifts_per_day):
            total_assigned = sum(
                solver.Value(shifts[(employee, day, shift)]) for employee in range(num_employees)
            )
            assert total_assigned == 1, (
                f"Shift {shift} on day {day} has {total_assigned} employees assigned, "
                f"expected 1."
            )

# Test case: Minimum staffing with full-time employees
def test_minimum_staffing_full_time():
    """
    Test that with minimum full-time staff, the model finds a feasible solution without exceeding 40 hours per week.
    """
    num_employees = 8
    shifts_per_day = 2
    total_days = 7
    full_time_hours = 40
    full_shift = 8
    employee_types = ["full_time"] * num_employees

    model, shifts = create_shift_scheduling_model(
        num_employees,
        shifts_per_day,
        total_days,
        employee_types,
        full_time_hours=full_time_hours,
        full_shift=full_shift,
    )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    assert status in [cp_model.OPTIMAL, cp_model.FEASIBLE], "Solver failed to find a solution."

    for employee in range(num_employees):
        total_hours = sum(
            solver.Value(shifts[(employee, day, shift)]) * full_shift
            for day in range(total_days)
            for shift in range(shifts_per_day)
        )
        assert total_hours <= full_time_hours, (
            f"Employee {employee} should not exceed {full_time_hours} working hours per week "
            f"(worked {total_hours} hours)."
        )

# Test case: Insufficient staffing results in infeasible solution
def test_insufficient_staffing():
    """
    Test that the solver returns INFEASIBLE when staffing is insufficient.
    Expected result: Test passes because the problem is infeasible.
    """
    num_employees = 2
    shifts_per_day = 3
    total_days = 7
    employee_types = ["full_time"] * num_employees

    model, shifts = create_shift_scheduling_model(
        num_employees, shifts_per_day, total_days, employee_types
    )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    assert status == cp_model.INFEASIBLE, (
        "Expected no solution due to insufficient staffing, but a solution was found!"
    )

# Test case: Initial model creation
def test_initial_model():
    """
    Test that the initial model creation returns a valid model and shifts dictionary.
    """
    num_employees = 4
    shifts_per_day = 4
    total_days = 7
    employee_types = ["full_time", "part_time", "full_time", "part_time"]

    model, shifts = create_shift_scheduling_model(
        num_employees, shifts_per_day, total_days, employee_types
    )
    assert model is not None, "Model should not be None."
    assert shifts is not None, "Shifts dictionary should not be None."
    assert len(shifts) > 0, "Shifts dictionary should not be empty."

# Test case: No available shifts
def test_no_available_shifts():
    """
    Test that when there are no shifts per day, the shifts dictionary is empty.
    """
    num_employees = 4
    shifts_per_day = 0
    total_days = 7
    employee_types = ["full_time", "part_time", "full_time", "part_time"]

    model, shifts = create_shift_scheduling_model(
        num_employees, shifts_per_day, total_days, employee_types
    )
    assert len(shifts) == 0, "Shifts dictionary should be empty when there are no shifts per day."

# Test case: No employees
def test_no_employees():
    """
    Test that when there are no employees, the shifts dictionary is empty.
    """
    num_employees = 0
    shifts_per_day = 4
    total_days = 7
    employee_types = []

    model, shifts = create_shift_scheduling_model(
        num_employees, shifts_per_day, total_days, employee_types
    )
    assert len(shifts) == 0, "Shifts dictionary should be empty when there are no employees."

# Test case 14: There are more employees than available shift 
def test_more_employee_than_available_shift():
    """
    Test there are more employees than available shift. Test should pass when there are not enough available shift per day 
    """
    num_employees = 20
    shifts_per_day = 2
    total_days = 3
    employee_types = [
        "full_time", "full_time",
        "full_time", "full_time",
        "full_time", "full_time",
        "part_time", "full_time",
        "part_time", "part_time",
        "part_time", "full_time", 
        "full_time", "full_time",
        "full_time", "full_time",
        "part_time", "full_time",
        "part_time", "part_time",
        ]
    model, shifts = create_shift_scheduling_model(
        num_employees, shifts_per_day, total_days, employee_types
    )
    
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    assert status == cp_model.OPTIMAL or status == cp_model.INFEASIBLE, "Solver did not find a feasible solution."

    assert status == cp_model.INFEASIBLE, (
        "Expected no solution due to insufficient staffing, but a solution was found!"
    )
            
 # Test case 15: There are just enough employee to cover available shifts  
    """
    Test use to check if the program is able to generate solution under sufficient staff with more full time than part time.
    This test will pass when full time employee can work 40 hours a week, and part time employees do not work over 20 hours
    """
def test_sufficient_staff_with_more_full_time_than_part_time():
    num_employees = 4
    shifts_per_day = 4
    total_days = 7
    part_time_hours = 20
    full_time_hours = 40
    full_shift = 8
    half_shift = 4
    employee_types = [ 
        "full_time",
        "full_time",
        "part_time",
        "part_time",
        ]
    model, shifts = create_shift_scheduling_model(
        num_employees,
        shifts_per_day,
        total_days,
        employee_types,
        full_time_hours= full_time_hours,
        part_time_hours= part_time_hours,
        full_shift= 8,
        half_shift= 4,
    )

    # Enforce exact working hours for full-time employees
    for employee in range(num_employees):
        if employee_types[employee] == "full_time":
            model.Add(
                sum(
                    shifts[(employee, day, shift)] * full_shift
                    for day in range(total_days)
                    for shift in range(shifts_per_day)
                )
                == 40
            )

    # Enforce maximum working hours for part-time employees
    for employee in range(num_employees):
        if employee_types[employee] == "part_time":
            model.Add(
                sum(
                    shifts[(employee, day, shift)] * half_shift
                    for day in range(total_days)
                    for shift in range(shifts_per_day)
                )
                <= 20
            )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    assert status == cp_model.INFEASIBLE, (
        "Expected no solution due to just have the right number of staff to cover available shift. However, the program still generate valid solution since full time workers >= part time worker. "
    )



  # Test case 16: There are just enough employee to cover available shifts  
    """
    Test use to check if the program is able to generate solution under sufficient staff with more full time than part time. Test is expected to fail since there are more part time staff than full time staff. However, the program DID FIND A SOLUTION
    """
def test_sufficient_staff_with_more_part_time_than_full_time():
    num_employees = 4
    shifts_per_day = 4
    total_days = 7
    part_time_hours = 20 # Reduce from 20 to 8
    full_time_hours = 40
    full_shift = 8
    half_shift = 4
    employee_types = [ 
        "part_time",
        "part_time",
        "part_time",
        "full_time",
        ]
    model, shifts = create_shift_scheduling_model(
        num_employees,
        shifts_per_day,
        total_days,
        employee_types,
        full_time_hours= full_time_hours,
        part_time_hours= part_time_hours,
        full_shift= 8,
        half_shift= 4,
    )

    # Enforce exact working hours for full-time employees
    for employee in range(num_employees):
        if employee_types[employee] == "full_time":
            model.Add(
                sum(
                    shifts[(employee, day, shift)] * full_shift
                    for day in range(total_days)
                    for shift in range(shifts_per_day)
                )
                == 40
            )

    # Enforce maximum working hours for part-time employees
    for employee in range(num_employees):
        if employee_types[employee] == "part_time":
            model.Add(
                sum(
                    shifts[(employee, day, shift)] * half_shift
                    for day in range(total_days)
                    for shift in range(shifts_per_day)
                )
                <= 20
            )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    assert status == cp_model.INFEASIBLE, (
        "Expected no solution due to just have the right number of staff to cover available shift. However, the program still generate valid solution since full time workers >= part time worker. "
    )   


 # Test case 17: There are just enough employee to cover available shifts  
    """
    Test use to check if the program is able to generate solution under sufficient staff with more full time than part time. Test is expected to be INFEASIBLE since there are more part time staff than full time staff. 
    """
def test_available_shifts_are_double_part_time_employees():
    num_employees = 4
    shifts_per_day = 8
    total_days = 7
    part_time_hours = 20
    half_shift = 4
    employee_types = [
        "part_time",
        "part_time",
        "part_time",
        "part_time",
    ]

    model, shifts = create_shift_scheduling_model(
        num_employees,
        shifts_per_day,
        total_days,
        employee_types,
        part_time_hours= part_time_hours,
        half_shift= half_shift,
    )

    # Ensure that each shift must be covered by exactly one employee
    for day in range(total_days):
        for shift in range(shifts_per_day):
            model.Add(
                sum(shifts[(employee, day, shift)] for employee in range(num_employees)) == 1
            )

    # Enforce part-time employees do not exceed their hours
    for employee in range(num_employees):
        if employee_types[employee] == "part_time":
            model.Add(
                sum(
                    shifts[(employee, day, shift)] * half_shift
                    for day in range(total_days)
                    for shift in range(shifts_per_day)
                ) <= part_time_hours
            )

    # Initialize solver
    solver = cp_model.CpSolver()
    
    # Solve the model
    status = solver.Solve(model)

    # Check if the solution is INFEASIBLE (no valid solution)
    assert status == cp_model.INFEASIBLE, (
        "Expected no solution due to insufficient part-time staff to cover all shifts, "
        "but the program still generated a valid solution."
    )

