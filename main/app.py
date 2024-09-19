from ortools.sat.python import cp_model

def create_shift_scheduling_model(
    num_employees, shifts_per_day, total_days, employee_types, 
    full_time_hours=40, part_time_hours=20, manager_hours=40
):
    """
    Creates and returns a shift scheduling model based on input parameters.

    Args:
        num_employees (int): The total number of employees.
        shifts_per_day (int): The number of shifts in a single day.
        total_days (int): The total number of days in the scheduling period.
        employee_types (list): A list of employee types (e.g., 'full_time', 'part_time', 'manager').
        full_time_hours (int): Maximum working hours per week for full-time employees.
        part_time_hours (int): Maximum working hours per week for part-time employees.
        manager_hours (int): Maximum working hours per week for managers.

    Returns:
        model (CpModel): The OR-Tools constraint programming model.
        shift_assignments (dict): A dictionary containing the shift assignment variables.
    """
    
    model = cp_model.CpModel()

    # Define the range of employees, shifts, and days
    employee_range = range(num_employees)
    shift_range = range(shifts_per_day)
    day_range = range(total_days)

    # Create shift assignment variables: shift_assignments[e, d, s] = True if employee e works shift s on day d
    shift_assignments = {}
    for employee in employee_range:
        for day in day_range:
            for shift in shift_range:
                shift_assignments[(employee, day, shift)] = model.new_bool_var(
                    f"shift_employee{employee}_day{day}_shift{shift}"
                )

    # Constraint: Each employee can work at most 1 shift per day
    for employee in employee_range:
        for day in day_range:
            model.add_at_most_one(
                shift_assignments[(employee, day, shift)] for shift in shift_range
            )

    # Constraint: Each shift must be assigned to exactly 1 employee
    for day in day_range:
        for shift in shift_range:
            model.add_exactly_one(
                shift_assignments[(employee, day, shift)] for employee in employee_range
            )

    # Constraint: Ensure employees work within their respective hour limits
    for employee in employee_range:
        total_hours_worked = []
        for day in day_range:
            for shift in shift_range:
                total_hours_worked.append(shift_assignments[(employee, day, shift)])

    # Constraint: Ensure employees work within their respective hour limits
    for employee in employee_range:
        total_hours_worked = []
        for day in day_range:
            for shift in shift_range:
                total_hours_worked.append(shift_assignments[(employee, day, shift)])

        # Apply hourly constraints based on employee type
        if employee_types[employee] == 'full_time':
            model.add(sum(total_hours_worked) <= full_time_hours)
        elif employee_types[employee] == 'part_time':
            model.add(sum(total_hours_worked) <= part_time_hours)
        elif employee_types[employee] == 'manager':
            model.add(sum(total_hours_worked) <= manager_hours)

    return model, shift_assignments


def solve_shift_scheduling(model, shift_assignments, num_employees, shifts_per_day, total_days, return_solver=False):
    """
    Solves the shift scheduling model.
    If return_solver is True, return the solver without using a callback (for tests).
    """
    solver = cp_model.CpSolver()

    if return_solver:
        solver.Solve(model)
        return solver

    class SolutionPrinter(cp_model.CpSolverSolutionCallback):
        """Prints the first 5 solutions for shift assignments."""
        
        def __init__(self, shift_assignments, num_employees, shifts_per_day, total_days, limit=5):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self._shift_assignments = shift_assignments
            self._num_employees = num_employees
            self._shifts_per_day = shifts_per_day
            self._total_days = total_days
            self._solution_count = 0
            self._solution_limit = limit

        def on_solution_callback(self):
            self._solution_count += 1
            print(f"\nSolution {self._solution_count}:")
            for day in range(self._total_days):
                print(f"Day {day + 1}")
                for shift in range(self._shifts_per_day):
                    for employee in range(self._num_employees):
                        if self.Value(self._shift_assignments[(employee, day, shift)]):
                            print(f"  Employee {employee} is assigned to Shift {shift}")
            if self._solution_count >= self._solution_limit:
                self.StopSearch()

    solution_printer = SolutionPrinter(shift_assignments, num_employees, shifts_per_day, total_days)
    solver.SolveWithSolutionCallback(model, solution_printer)

    return solver


def main():
    """
    Main function to run the shift scheduling model based on user inputs.
    Prompts the user for the number of employees, shifts per day, days, and employee types.
    """
    
    print("Welcome to the Employee Shift Scheduler!")

    # User input for the number of employees, shifts per day, and days
    num_employees = int(input("Enter the number of employees: "))
    shifts_per_day = int(input("Enter the number of shifts per day: "))
    total_days = int(input("Enter the total number of days to schedule: "))

    # Collect employee types from user input
    print("Please enter the type of each employee using the following codes:")
    print("1: Full-time (up to 40 hours per week)")
    print("2: Part-time (up to 20 hours per week)")
    print("3: Manager (up to 40 hours per week with managerial responsibilities)")
    print()

    # Collect employee types from user input
    employee_types = []
    for i in range(num_employees):
        while True:  # Loop to ensure valid input
            emp_type = input(f"Enter the type of employee {i + 1} (1 for full-time, 2 for part-time, 3 for manager): ").strip()
            if emp_type in ["1", "2", "3"]:
                if emp_type == "1":
                    employee_types.append("full_time")
                elif emp_type == "2":
                    employee_types.append("part_time")
                elif emp_type == "3":
                    employee_types.append("manager")
                break
            else:
                print("Invalid input. Please enter 1, 2, or 3.")

    # Create the shift scheduling model based on user inputs
    model, shift_assignments = create_shift_scheduling_model(
        num_employees, shifts_per_day, total_days, employee_types
    )

    # Solve and print up to 5 possible shift assignments
    solve_shift_scheduling(model, shift_assignments, num_employees, shifts_per_day, total_days)


if __name__ == "__main__":
    main()
