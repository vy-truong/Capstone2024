"""
Employee Shift Scheduler using OR-Tools CP-SAT Solver.

This script allows users to schedule shifts for employees over a number of days.
Employees can be full-time or part-time, with different maximum working hours.
The script ensures that shifts are assigned according to constraints and displays possible schedules.
"""

# Import the required OR-Tools module for CP-SAT solver
from ortools.sat.python import cp_model

def create_shift_scheduling_model(
    num_employees,
    shifts_per_day,
    total_days,
    employee_types, 
    full_time_hours=40,
    part_time_hours=20,
    full_shift=8,
    half_shift=4,
):
    """
    Creates a constraint programming model for shift scheduling.

    Args:
        num_employees (int): Number of employees to schedule.
        shifts_per_day (int): Number of shifts available each day.
        total_days (int): Total number of days to schedule.
        employee_types (list of str): List indicating the type of each employee ('full_time' or 'part_time').
        full_time_hours (int, optional): Maximum hours per week for full-time employees. Defaults to 40.
        part_time_hours (int, optional): Maximum hours per week for part-time employees. Defaults to 20.
        full_shift (int, optional): Hours per shift for full-time employees. Defaults to 8.
        half_shift (int, optional): Hours per shift for part-time employees. Defaults to 4.

    Returns:
        model (cp_model.CpModel): The CP-SAT model with all constraints added.
        shifts (dict): Dictionary of shift variables indexed by (employee, day, shift).
    """

    model = cp_model.CpModel()

    # Define ranges for employees, shifts, and days
    all_employees = range(num_employees)
    all_shifts = range(shifts_per_day)
    all_days = range(total_days)

    # Create the shift variables we need to pass to the model, constraints to follow
    shifts = {}
    for employee in all_employees:
        for day in all_days:
            for shift in all_shifts:
                # Create a boolean variable for each possible assignment
                shifts[(employee, day, shift)] = model.NewBoolVar(f"shift_e{employee}_d{day}_s{shift}")

    # Constraint: Each employee works at most one shift per day
    for employee in all_employees:
        for day in all_days:
            # For each employee and day, add the constraint
            model.AddAtMostOne(shifts[(employee, day, shift)] for shift in all_shifts)

    # Constraint: Each shift is assigned exactly one employee
    for day in all_days:
        for shift in all_shifts:
            # For each day and shift, ensure exactly one employee is assigned
            model.AddExactlyOne(shifts[(employee, day, shift)] for employee in all_employees)

    # Constraint: Enforce maximum working hours based on employee type
    for employee in all_employees:
        if employee_types[employee] == 'part_time':
            # Part-time employees have a maximum number of hours per week
            total_hours = sum(
                shifts[(employee, day, shift)] * half_shift  # Part-time shift hours
                for day in all_days
                for shift in all_shifts
            )
            model.Add(total_hours <= part_time_hours)
        elif employee_types[employee] == 'full_time':
            # Full-time employees have a maximum number of hours per week
            total_hours = sum(
                shifts[(employee, day, shift)] * full_shift  # Full-time shift hours
                for day in all_days
                for shift in all_shifts
            )
            model.Add(total_hours <= full_time_hours)
        else:
            # Handle unexpected employee type
            raise ValueError(f"Unknown employee type: {employee_types[employee]}")

    # Constraint: Ensure every full-time employee works at least one shift over the scheduling period
    for employee in all_employees:
        if employee_types[employee] == 'full_time':
            total_shifts_worked = sum(
                shifts[(employee, day, shift)]
                for day in all_days
                for shift in all_shifts
            )
            model.Add(total_shifts_worked >= 1)

    return model, shifts

def solve_shift_scheduling(model, shifts, num_employees, shifts_per_day, total_days, return_solver=False):
    """
    Solves the shift scheduling model prints solutions.

    Args:
        model (cp_model.CpModel): The shift scheduling model to solve.
        shifts (dict): Dictionary of shift variables.
        num_employees (int): Number of employees.
        shifts_per_day (int): Number of shifts per day.
        total_days (int): Total number of days to schedule.
        return_solver (bool, optional): True if feasible. Defaults to False.
    """

    solver = cp_model.CpSolver()

    if return_solver:
        # Solve the model and return the solver
        status = solver.Solve(model)
        return solver
    else:
        # Define a solution printer to display solutions
        class SolutionPrinter(cp_model.CpSolverSolutionCallback):

            """Here is where we limit how many results we want"""
            def __init__(self, shifts, num_employees, shifts_per_day, total_days, limit=3):
                cp_model.CpSolverSolutionCallback.__init__(self)
                self._shifts = shifts
                self._num_employees = num_employees
                self._shifts_per_day = shifts_per_day
                self._total_days = total_days
                self._solution_count = 0
                self._solution_limit = limit

            def on_solution_callback(self):
                """For each possible solution, do..."""
                self._solution_count += 1
                print(f"\nSolution {self._solution_count}:")
                for day in range(self._total_days):
                    print(f"Day {day + 1}")
                    for shift in range(self._shifts_per_day):
                        for employee in range(self._num_employees):
                            if self.Value(self._shifts[(employee, day, shift)]):
                                print(f"  Employee {employee} is assigned to Shift {shift}")
                    print()
                if self._solution_count >= self._solution_limit:
                    self.StopSearch()

        # Create an instance of the solution printer
        solution_printer = SolutionPrinter(shifts, num_employees, shifts_per_day, total_days)

        # Solve the model with the solution printer callback
        status = solver.SolveWithSolutionCallback(model, solution_printer)

        # Check if a solution was found
        if status == cp_model.INFEASIBLE:
            print("No solution found.")

def main():
    """
    Main function to run the shift scheduling model based on user inputs.
    Prompts the user for inputs, creates the model, and solves it.
    """

    print("Welcome to the Employee Shift Scheduler!")

    # User input
    num_employees = int(input("Enter the number of employees: "))
    shifts_per_day = int(input("Enter the number of shifts per day: "))
    total_days = int(input("Enter the total number of days to schedule: "))

    print("\nPlease enter the type of each employee using the following codes:")
    print("1: Full-time (up to 40 hours per week)")
    print("2: Part-time (up to 20 hours per week)\n")

    # Initialize the list of employee types
    employee_types = []
    for i in range(num_employees):
        while True:
            emp_type = input(f"Enter the type of employee {i + 1} (1 for full-time, 2 for part-time): ").strip()
            if emp_type == "1":
                employee_types.append("full_time")
                break
            elif emp_type == "2":
                employee_types.append("part_time")
                break
            else:
                print("Invalid input. Please enter 1 or 2.")

    # Create the shift scheduling model based on user inputs
    model, shifts = create_shift_scheduling_model(
        num_employees, shifts_per_day, total_days, employee_types
    )

    # Solve and print up to 3 possible shift assignments
    solve_shift_scheduling(model, shifts, num_employees, shifts_per_day, total_days)

if __name__ == "__main__":
    main()
