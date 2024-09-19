import pytest
from ortools.sat.python import cp_model

# Giả sử đây là hàm em dùng để tạo mô hình xếp ca
from main.app import create_shift_scheduling_model, solve_shift_scheduling

# test case 1: check to make sure full time worker work at least 40 hours 
def test_full_time_hours():
    num_employees = 6
    shifts_per_day = 4 
    total_days = 5 
    employee_types = ['full_time','full_time','full_time','part_time','part_time', 'part_time']


    # create model to organize these shit and store them or watever 
    model, shifts = create_shift_scheduling_model(num_employees, shifts_per_day, total_days, employee_types
    )

    # solver to do result 
    solver = solve_shift_scheduling(model, shifts, num_employees, shifts_per_day, total_days,  return_solver=True)


    #check full time 
    for e in range(3):  # Kiểm tra 3 nhân viên full-time đầu tiên
        hours_worked = sum(solver.Value(shifts[(e, d, s)]) * 8 for d in range(total_days) for s in range(shifts_per_day))
        assert hours_worked >= 40, f"Nhân viên {e} full-time không làm đủ 40 giờ!"





