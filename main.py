from ortools.sat.python import cp_model

def main():
    
    drivers = ['Bill', 'Will', 'Jeff', 'John', 'Peter']
    shifts_interval = ['morning', 'afternoon', 'night'] 
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    number_of_truckers = len(drivers) # number of truckers
    num_shifts = len(shifts_interval) # shifts per day
    num_days = 7 # number of days
    
    truckers = range(number_of_truckers)
    all_shifts = range(num_shifts)
    all_days = range(num_days)
    
    # create shift requests array from excel table
    shift_requests = [
        [[0,0,1],[0,1,0],[1,0,0],[0,0,0],[0,1,0],[1,0,0],[0,0,1]], #Bill
        [[0,0,1],[0,1,0],[1,0,0],[1,0,0],[0,1,0],[0,0,0],[0,0,1]], #Will
        [[1,0,0],[1,0,0],[1,0,0],[0,0,1],[1,0,0],[0,1,0],[1,0,0]], #Jeff
        [[0,1,0],[1,0,0],[0,0,0],[0,0,1],[0,1,0],[0,0,0],[0,0,0]], #John
        [[0,0,1],[0,0,0],[1,0,0],[1,0,0],[1,0,0],[0,0,1],[1,0,0]]  #Peter
    ] # 1 = yes, 0 = no
    
    
    

    # Model
    model = cp_model.CpModel()

    # Shift variables
    shifts = {}
    for t in truckers:
        for d in all_days:
            for s in all_shifts:
                shifts[(t, d,
                        s)] = model.NewBoolVar('shift_t%id%is%i' % (t, d, s))

    # Constraints
    # Each shift belongs to exactly one truck driver.
    for d in all_days:
        for s in all_shifts:
            model.AddExactlyOne(shifts[(t, d, s)] for t in truckers)

    # Each driver only works one shift a day.
    for t in truckers:
        for d in all_days:
            model.AddAtMostOne(shifts[(t, d, s)] for s in all_shifts)

    
    min_shifts_per_trucker = (num_shifts * num_days) // number_of_truckers
    if num_shifts * num_days % number_of_truckers == 0:
        max_shifts_per_trucker  = min_shifts_per_trucker
    else:
        max_shifts_per_trucker = min_shifts_per_trucker + 1
    for n in truckers:
        num_shifts_worked = 0
        for d in all_days:
            for s in all_shifts:
                num_shifts_worked += shifts[(n, d, s)]
        model.Add(min_shifts_per_trucker <= num_shifts_worked)
        model.Add(num_shifts_worked <= max_shifts_per_trucker)

    model.Maximize(
        sum(shift_requests[n][d][s] * shifts[(n, d, s)] for n in truckers
            for d in all_days for s in all_shifts))

    # SOLVE
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:
        with open('output.txt', 'w') as f:
            f.write('Output: \n')
            
            for d in all_days:
                f.write(f'\n{days[d]}:\n\n')
                for n in truckers:
                    for s in all_shifts:
                        if solver.Value(shifts[(n, d, s)]) == 1:
                            if shift_requests[n][d][s] == 1:  
                                f.write(f'- "{drivers[n]}" works shift {shifts_interval[s]} [requested].\n')
                            else:
                                f.write(f'- "{drivers[n]}" works shift {shifts_interval[s]} [not requested].\n')
            f.write(f'\nSuccessful shift requests: {solver.ObjectiveValue()}\n')
    else:
            f.write(f'\nNo optimal solution found!\n')
            
    f.close()    
        
    # Statistics
    with open('stats.txt', 'w') as f:
        f.write('\nStats')
        f.write(f'\n  - conflicts: %i' % solver.NumConflicts())
        f.write(f'\n  - branches : %i' % solver.NumBranches())
        f.write(f'\n  - wall time: %f s' % solver.WallTime())
        
        f.close()
        
    print('done.')
   

if __name__ == '__main__':
    main()