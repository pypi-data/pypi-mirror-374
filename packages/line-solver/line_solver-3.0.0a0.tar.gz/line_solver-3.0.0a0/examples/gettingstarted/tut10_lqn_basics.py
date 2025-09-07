#!/usr/bin/env python3
"""
Example 10: Basic layered queueing network
This example demonstrates a simple client-server application with two tiers
"""

import sys
import os

# Add the line_solver package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from line_solver.layered import LayeredNetwork, Processor, Task, Entry, Activity
from line_solver.constants import SchedStrategy  
from line_solver.distributions import Exp
from line_solver.solvers import SolverLN, SolverMVA

def main():
    # Create the layered network model
    model = LayeredNetwork('ClientDBSystem')

    # Create processors
    P1 = Processor(model, 'ClientProcessor', 1, SchedStrategy.PS)
    P2 = Processor(model, 'DatabaseProcessor', 1, SchedStrategy.PS)

    # Create tasks
    T1 = Task(model, 'ClientTask', 10, SchedStrategy.REF).on(P1)
    T1.setThinkTime(Exp.fitMean(5.0))  # 5-second think time
    T2 = Task(model, 'DatabaseTask', float('inf'), SchedStrategy.INF).on(P2)

    # Create entries that represent service interfaces
    E1 = Entry(model, 'ClientEntry').on(T1)
    E2 = Entry(model, 'DatabaseEntry').on(T2)

    # Define activities that specify the work performed and synchronous calls
    # Client activity: processes request and calls database
    A1 = Activity(model, 'ClientActivity', Exp.fitMean(1.0)).on(T1)
    A1.boundTo(E1).synchCall(E2, 2.5)  # 2.5 database calls on average

    # Database activity: processes database request  
    A2 = Activity(model, 'DatabaseActivity', Exp.fitMean(0.8)).on(T2)
    A2.boundTo(E2).repliesTo(E2)

    # Solve the layered network using the LN solver with MVA applied to each layer
    solver = SolverLN(model, lambda m: SolverMVA(m))
    avg_table = solver.getAvgTable()
    print(avg_table)

if __name__ == '__main__':
    main()