# GA_RG_HH: A Hyper-Heuristic Algorithm for University Course Scheduling Problem

## Project Overview
This repository contains the implementation of a hyper-heuristic algorithm integrating genetic and greedy strategies (GA_RG_HH) for solving the University Course Scheduling Problem (UCSP). The algorithm aims to efficiently allocate classroom, teacher, and timeslot resources while satisfying both hard and soft constraints, optimizing scheduling reasonableness and resource utilization.


## Problem Background
The University Course Scheduling Problem (UCSP) is a classic NP-hard optimization problem that requires coordinating multiple resources (classrooms, teachers, timeslots) under various constraints. Manual scheduling, still common in many universities, is time-consuming and often leads to suboptimal resource allocation.

This work proposes a comprehensive UCSP model that incorporates multi-dimensional soft constraints involving:
- Student classes (e.g., balanced weekly course distribution)
- Teachers (e.g., preference for continuous teaching blocks, preferred timeslots)
- Courses (e.g., suitable time slots for specific courses)
- Classrooms (e.g., efficient utilization of space)

The goal is to reduce teacher workload, alleviate student learning burdens, and optimize classroom resource usage.


## Algorithm Description
The proposed GA_RG_HH algorithm combines genetic algorithms (GA) with greedy strategies to balance exploration and exploitation:

- **High-level heuristic**: Genetic algorithms are used to find the optimal combination of operators in the current environment, including operations like tournament selection and two-point crossover.
- **Low-level heuristics**: A set of 10 operators (4 random operators, 5 greedy operators, and 1 invalid operator) is used to change and perturb the current solution in order to find a better solution..
- **Key features**:
  - Dynamic adjustment of operator sequence length to balance exploration/exploitation
  - Pre-check strategy to ensure constraint satisfaction
  - Efficient solution improvement through heuristic operators (e.g., timeslot swapping, classroom type adjustment)


## File Structure
- `GA_RG_HH.py`: Core implementation of the GA_RG_HH algorithm, including genetic operators (selection, crossover, mutation) and heuristic update strategies.
- `time_test.py`: Time performance testing and validation of the scheduling algorithm.
- `obj_time.py`: Implementation of auxiliary heuristic operators (e.g., random adjustment, timeslot swapping) and constraint checking.
- `obj_function.py`: Objective function calculations for soft constraint evaluation, including:
  - Night course penalty
  - Class distribution balance
  - Teacher continuity preference
  - Teacher/course time preferences
  - Same-course daily conflict penalty
  - Classroom utilization efficiency
- `data_gen.py`: Generate detailed test data.
- `data_sta.py`: Statistical test data information.
- `data_loader.py`: Data loading module for processing input files (course tasks, teacher info, classroom data).
- `fig_gtt.py`: Visualization tools for scheduling results (e.g., timetable plots for classes, teachers, and classrooms).


## Dependencies
- Python 3.12
- NumPy
- Matplotlib
- Pandas (for data loading from Excel files)


## Usage
1. Prepare input data files (course tasks, teacher information, classroom data) in Excel format.
2. Configure parameters in the main script (population size, genetic operator probabilities, etc.).
3. Run the main algorithm:
   ```bash
   python GA_RG_HH.py
   ```
4. Check output results, including optimized timetables and objective function values.
5. Use visualization functions in `fig_gtt.py` to plot scheduling results.


## Reference
For detailed algorithm principles and experimental results, please refer to the corresponding research paper:
(The paper is currently under review).

