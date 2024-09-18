from ortools.sat.python import cp_model


def get_number_of_employees(num_employees):
    return num_employees


def main() -> None:
    
    # i set number of employee
    num_employees = 6 
    num_shift_per_day = 4 #there will be 4 role titles: 1 manager, 1 host, 1 busser, 1 servers
    num_days = 7 
    full_time_hour_per_week = 40
    part_time_hour_per_week = 20
    manager_hour_per_week = 40 # i include this to test. But i think we should let the user decide 

    # full time or part time for **each employee**
    employee_types = ['full_time', 'part_time', 'manager', 'part_time', 'full_time', 'part_time']

    all_employees = range(num_employees)
    all_shifts = range(num_shift_per_day)
    all_days = range(num_days)

    # create model 
    
    model = cp_model.CpModel()

    # create an array to store SHIFT OF EMPLOYEE that will display the (e, d, s) ONE PER SHIFT. 
    # we will use this array shifts from now for other rule 
    shifts = {}
    for e in all_employees:
        for d in all_days:
            for s in all_shifts:
                shifts[(e, d, s)] = model.new_bool_var(f"shift_n{e}_d{d}_s{s}")

    # make sure each employee is assigned to maximum 1 shift a day
    for e in all_employees:
        for d in all_days:
            model.add_at_most_one(shifts[(e, d, s)] for s in all_shifts)

    # make sure each shift is assigned to 1 employee a day
    for d in all_days:
        for s in all_shifts:
            model.add_exactly_one(shifts[(e, d, s)] for e in all_employees)

    # add constraint for working hour. again this is for testing purpose. we will create an input field for manager to assign 
    for e in all_employees:
        # this line will store the employee total working hours in a week
        total_work_hours = []
        for d in all_days:
            for s in all_shifts:
                total_work_hours.append(shifts[(e, d, s)])
        
    
        # full-time employees work up to 40 hours per week
        # remember the employee_types i create at line 13 yall? we will use it to compare 
        if employee_types[e] == 'full_time':
            model.add(sum(total_work_hours) <= full_time_hour_per_week)
        # part-time employees work up to 20 hours per week
        elif employee_types[e] == 'part_time':
            model.add(sum(total_work_hours) <= part_time_hour_per_week)
        # manager works up to 40 hours per week
        elif employee_types[e] == 'manager':
            model.add(sum(total_work_hours) <= manager_hour_per_week)

    # modify shift requirements to ensure that the number of shifts per employee is reasonable
    min_shifts_per_employee = (num_shift_per_day * num_days) // num_employees #around 4 shifts a week
    max_shifts_per_employee = min_shifts_per_employee + 2  # allow some flexibility maximum 6 shifts

    #check 
    for e in all_employees:
        shifts_worked = []
        for d in all_days:
            for s in all_shifts:
                shifts_worked.append(shifts[(e, d, s)])
        model.add(sum(shifts_worked) >= min_shifts_per_employee)
        model.add(sum(shifts_worked) <= max_shifts_per_employee)

    #ADD NEW EMPLOYEE INTO THE MODEL        
    def add_employee(employee_type):
        nonlocal num_employees, employee_types, shifts
        new_employee_id = num_employees
        employee_types.append(employee_type)  # add employee type (should be part time or full time)
        num_employees += 1  # Increment employee count

        # add new employee's shifts to the model
        for d in all_days:
            for s in all_shifts:
                shifts[(new_employee_id, d, s)] = model.new_bool_var(f"shift_n{new_employee_id}_d{d}_s{s}")
        
        print(f"New employee {new_employee_id} ({employee_type}) added successfully!")

    # # Example: Add a new full-time employee
    add_employee('full_time')

    # create the solver and solve.
    solver = cp_model.CpSolver()
    solver.parameters.linearization_level = 0
    solver.parameters.enumerate_all_solutions = True

    # create the solution printer
    class EmployeesPartialSolutionPrinter(cp_model.CpSolverSolutionCallback):
        """Print intermediate solutions."""

        # some construction etc 
        #Solution callback. This class implements a callback that will be called at each new solution found during search.
        def __init__(self, shifts, num_employees, num_days, num_shift_per_day, limit):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self._shifts = shifts
            self._num_employees = num_employees
            self._num_days = num_days
            self._num_shift_per_day = num_shift_per_day
            self._solution_count = 0
            self._solution_limit = limit

        def on_solution_callback(self): #the callback solution will be assigned in on_solution_callback

            #it will print Solution and num if found
            self._solution_count += 1
            print(f"Solution {self._solution_count}")

            #create a loop for it to print all day in a week 
            for d in range(self._num_days):
                print(f"Day {d}")
                for e in range(self._num_employees):
                    is_working = False
                    for s in range(self._num_shift_per_day):
                        if self.Value(self._shifts[(e, d, s)]):
                            is_working = True
                            print(f"  Employee {e} works shift {s}")
                    if not is_working:
                        print(f"  Employee {e} does not work")
            if self._solution_count >= self._solution_limit:
                print(f"Stop search after {self._solution_limit} solutions")
                self.StopSearch()

        def solutionCount(self):
            return self._solution_count
     
    # Display the first five solutions.
    solution_limit = 5
    solution_printer = EmployeesPartialSolutionPrinter(
        shifts, num_employees, num_days, num_shift_per_day, solution_limit
    )

    # Use SolveWithSolutionCallback to pass the callback
    solver.SolveWithSolutionCallback(model, solution_printer)




    # Statistics.
    print("\nStatistics")
    print(f"  - Conflicts      : {solver.NumConflicts()}")
    print(f"  - Branches       : {solver.NumBranches()}")
    print(f"  - Wall time      : {solver.WallTime()} s")
    print(f"  - Solutions found: {solution_printer.solutionCount()}")

if __name__ == "__main__":
    main()
