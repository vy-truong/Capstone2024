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
    model = cp_model.CpModel()

    all_employees = range(num_employees)
    all_shifts = range(shifts_per_day)
    all_days = range(total_days)

    # Create shift variables
    shifts = {} 
    for e in all_employees:
        for d in all_days:
            for s in all_shifts:
                shifts[(e, d, s)] = model.NewBoolVar(f"shift_n{e}_d{d}_s{s}")

    # Constraints: each employee works at most 1 shift per day
    for e in all_employees:
        for d in all_days:
            model.AddAtMostOne(shifts[(e, d, s)] for s in all_shifts)

    # Constraints: each shift must have exactly 1 employee
    for d in all_days:
        for s in all_shifts:
            model.AddExactlyOne(shifts[(e, d, s)] for e in all_employees)
    

    # For part-time employees, ensure they work at most half-shifts
    for e in all_employees:
        if employee_types[e] == 'part_time':
            model.Add(sum(shifts[(e, d, s)] * full_shift for d in all_days for s in all_shifts) <= part_time_hours)

    # Track total hours worked per employee
    hours_worked = {}
    for e in all_employees:
        if employee_types[e] == 'full_time':
            # Full-time employees: Create a variable to track hours worked
            hours_worked[e] = model.NewIntVar(0, full_shift * total_days * shifts_per_day, f"hours_worked_{e}")
            # Sum up the total hours worked for full-time employees
            total_hours = sum(shifts[(e, d, s)] * full_shift for d in all_days for s in all_shifts)
            model.Add(hours_worked[e] == total_hours)
        elif employee_types[e] == 'part_time':
            # Part-time employees: Create a variable to track hours worked
            hours_worked[e] = model.NewIntVar(0, half_shift * total_days * shifts_per_day, f"hours_worked_{e}")

            # Sum up the total hours worked for part-time employees
            total_hours = sum(shifts[(e, d, s)] * half_shift for d in all_days for s in all_shifts)
            model.Add(hours_worked[e] == total_hours)


    # Calculate total hours worked and apply type-based constraints
    for e in all_employees:
        # Full-time and part-time constraints based on employee types
        if employee_types[e] == 'full_time':
            total_hours = sum(
            shifts[(e, d, s)] * full_shift for d in all_days for s in all_shifts
        )
        elif employee_types[e] == 'part_time':
            total_hours = sum(
            shifts[(e, d, s)] * half_shift for d in all_days for s in all_shifts
        )

    # Ensure every employee works at least one shift PER WEEK
    for e in all_employees:
        model.Add(sum(shifts[(e, d, s)] for d in all_days for s in all_shifts) >= 1)

    return model, shifts


def solve_shift_scheduling(model, shifts, num_employees, shifts_per_day, total_days, return_solver=False):
    """
    Solves the shift scheduling model.
    If return_solver is True, return the solver without using a callback (for tests).
    """
    solver = cp_model.CpSolver()

    if return_solver:
        solver.Solve(model)
        return solver
    else:
        print("No solution")


    class SolutionPrinter(cp_model.CpSolverSolutionCallback):
        """Prints the first 3 solutions for shift assignments."""
        
        def __init__(self, shifts, num_employees, shifts_per_day, total_days, limit=3):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self._shifts = shifts
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
                        if self.Value(self._shifts[(employee, day, shift)]):
                            print(f"  Employee {employee} is assigned to Shift {shift}")
            if self._solution_count >= self._solution_limit:
                self.StopSearch()

    solution_printer = SolutionPrinter(shifts, num_employees, shifts_per_day, total_days)
    solver.SolveWithSolutionCallback(model, solution_printer)


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
    print()

    employee_types = []
    for i in range(num_employees):
        while True:
            emp_type = input(f"Enter the type of employee {i + 1} (1 for full-time, 2 for part-time): ").strip()
            if emp_type in ["1", "2"]:
                if emp_type == "1":
                    employee_types.append("full_time")
                elif emp_type == "2":
                    employee_types.append("part_time")
                break
            else:
                print("Invalid input. Please enter 1 or 2")

    # Create the shift scheduling model based on user inputs
    model, shifts = create_shift_scheduling_model(
        num_employees, shifts_per_day, total_days, employee_types
    )

    # Solve and print up to 5 possible shift assignments
    solve_shift_scheduling(model, shifts, num_employees, shifts_per_day, total_days)


if __name__ == "__main__":
    main()