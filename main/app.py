from ortools.sat.python import cp_model

def create_model(num_employees, num_shift_per_day, num_days, employee_types, full_time_hours=40, part_time_hours=20, manager_hours=40):
    """Creates and returns a shift scheduling model based on input parameters."""
    model = cp_model.CpModel()

    all_employees = range(num_employees)
    all_shifts = range(num_shift_per_day)
    all_days = range(num_days)

    shifts = {}
    # Create shift variables
    for e in all_employees:
        for d in all_days:
            for s in all_shifts:
                shifts[(e, d, s)] = model.new_bool_var(f"shift_n{e}_d{d}_s{s}")

    # Constraints: each employee works at most 1 shift per day
    for e in all_employees:
        for d in all_days:
            model.add_at_most_one(shifts[(e, d, s)] for s in all_shifts)

    # Constraints: each shift must have exactly 1 employee
    for d in all_days:
        for s in all_shifts:
            model.add_exactly_one(shifts[(e, d, s)] for e in all_employees)

    # Add working hour constraints for each employee based on their type
    for e in all_employees:
        total_work_hours = []
        for d in all_days:
            for s in all_shifts:
                total_work_hours.append(shifts[(e, d, s)])
        
        if employee_types[e] == 'full_time':
            model.add(sum(total_work_hours) <= full_time_hours)
        elif employee_types[e] == 'part_time':
            model.add(sum(total_work_hours) <= part_time_hours)
        elif employee_types[e] == 'manager':
            model.add(sum(total_work_hours) <= manager_hours)

    return model, shifts


def solve_model(model, shifts, num_employees, num_shift_per_day, num_days):
    """Solves the scheduling model and returns the solver."""
    solver = cp_model.CpSolver()

    class SolutionPrinter(cp_model.CpSolverSolutionCallback):
        """Print intermediate solutions."""
        def __init__(self, shifts, num_employees, num_shift_per_day, num_days, limit=5):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self._shifts = shifts
            self._num_employees = num_employees
            self._num_shift_per_day = num_shift_per_day
            self._num_days = num_days
            self._solution_count = 0
            self._solution_limit = limit

        def on_solution_callback(self):
            self._solution_count += 1
            print(f"Solution {self._solution_count}")
            for d in range(self._num_days):
                print(f"Day {d}")
                for s in range(self._num_shift_per_day):
                    for e in range(self._num_employees):
                        if self.Value(self._shifts[(e, d, s)]):
                            print(f"  Employee {e} works shift {s} on day {d}")
            if self._solution_count >= self._solution_limit:
                print(f"Stop search after {self._solution_limit} solutions")
                self.StopSearch()

    solution_printer = SolutionPrinter(shifts, num_employees, num_shift_per_day, num_days)
    solver.solve(model, solution_printer)

    return solver


def add_employee(model, shifts, num_employees, employee_type, employee_types, num_shift_per_day, num_days):
    """Adds a new employee to the scheduling model."""
    new_employee_id = num_employees
    employee_types.append(employee_type)  # Add employee type
    num_employees += 1  # Increment employee count

    # Add new employee's shifts to the model
    for d in range(num_days):
        for s in range(num_shift_per_day):
            shifts[(new_employee_id, d, s)] = model.new_bool_var(f"shift_n{new_employee_id}_d{d}_s{s}")

    print(f"New employee {new_employee_id} ({employee_type}) added successfully!")
    return model, shifts, num_employees


if __name__ == "__main__":
    # Example setup
    num_employees = 4
    num_shift_per_day = 4
    num_days = 7
    employee_types = ['full_time', 'part_time', 'manager', 'part_time']

    # Create and solve model
    model, shifts = create_model(num_employees, num_shift_per_day, num_days, employee_types)
    solve_model(model, shifts, num_employees, num_shift_per_day, num_days)
