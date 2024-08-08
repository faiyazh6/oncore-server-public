import random
import numpy as np
import math
import pulp


def convert_minutes_to_hhmm(minutes):
    hours = minutes // 60
    remaining_minutes = minutes % 60
    return f"{hours:02}:{remaining_minutes:02}"


def generate_example_data():
    # Define the number of chairs, max patients per nurse, and operating hours

    scale = 1

    num_chairs = int(20 * scale)
    M = 4  # Example nursing capacity (max number of patients a nurse can monitor at once)
    num_patients = int(50 * scale)
    num_nurses = int(10 * scale)
    open_time = 480
    close_time = 1080
    break_start_time = 600  # Breaks can start at 10:00 (600 minutes from midnight)
    break_end_time = 840  # Breaks can end at 2:00 (840 minutes from midnight)
    break_duration = 30  # Break duration in minutes

    # Generate patient list
    patients = []
    appointment_durations = {
        '1_hour': int(20 * scale),  # 20 patients with 1-hour appointments
        '2_hours': int(15 * scale),  # 15 patients with 2-hour appointments
        '3-5_hours': int(10 * scale),  # 10 patients with 3-5 hour appointments
        '6-8_hours': int(4 * scale),  # 4 patients with 6-8 hour appointments
        '9+_hours': int(1 * scale)  # 1 patient with 9+ hour appointments
    }

    appointment_times = {
        '1_hour': 60,
        '2_hours': 120,
        '3-5_hours': random.choice([180, 240, 300]),
        '6-8_hours': random.choice([360, 420, 480]),
        '9+_hours': random.choice([540, 600])
    }

    patient_id = 0
    for duration_type, count in appointment_durations.items():
        for _ in range(count):
            duration = appointment_times[duration_type]
            max_start_time = close_time - duration

            # Ensure start time is in 10-minute intervals
            start_time = random.randint(open_time // 10, max_start_time // 10) * 10

            acuity = random.randint(1, 3)
            patients.append({
                'patientId': patient_id,
                'readyTime': start_time,
                'length': duration,
                'dueTime': close_time,
                'acuity': acuity
            })
            patient_id += 1

    # Generate nursing schedule
    nurses = []
    center_open_hours = (close_time - open_time) // 60

    for i in range(num_nurses):
        shift_length = random.randint(8, center_open_hours)  # Shift length between 8 hours and the remaining open hours
        latest_start_hour = center_open_hours - shift_length
        start_hour = random.randint(0, latest_start_hour)
        shift_start = open_time + start_hour * 60
        shift_end = shift_start + shift_length * 60

        nurses.append({
            'nurseId': i,
            'startTime': shift_start,
            'endTime': shift_end
        })

    print(f"Number of Nurses: {num_nurses}")
    print(f"Number of Chairs: {num_chairs}")
    print(f"Maximum Patient Capacity per Nurse: {M}")
    print(f"Operating Hours: {convert_minutes_to_hhmm(open_time)} - {convert_minutes_to_hhmm(close_time)}")
    print("Patients:")
    for patient in patients:
        print(
            f"Patient ID: {patient['patientId']}, Ready Time: {convert_minutes_to_hhmm(patient['readyTime'])}, Due Time: {convert_minutes_to_hhmm(patient['dueTime'])}, Duration: {patient['length']} minutes, Acuity: {patient['acuity']}")

    print("Nurses:")
    for nurse in nurses:
        print(
            f"Nurse ID: {nurse['nurseId']}, Shift Start: {convert_minutes_to_hhmm(nurse['startTime'])}, Shift End: {convert_minutes_to_hhmm(nurse['endTime'])}")

    return num_nurses, num_chairs, M, open_time, close_time, patients, nurses, break_start_time, break_end_time, break_duration


def generate_realistic_data():
    # Define the number of chairs, max patients per nurse, and operating hours
    num_chairs = 36
    M = 4  # Example nursing capacity (max number of patients a nurse can monitor at once)

    num_nurses = 12
    open_time = 480
    close_time = 1080
    break_start_time = 690  # Breaks can start at 11:30 (690 minutes from midnight)
    break_end_time = 750  # Breaks can end at 12:30 (750 minutes from midnight)
    break_duration = 30  # Break duration in minutes

    # Generate patient list
    patients = []
    appointment_durations = {
        '1_hour': int(20 * 2),  # 20 patients with 1-hour appointments
        '2_hours': int(15 * 2),  # 15 patients with 2-hour appointments
        '3-5_hours': int(10 * 2),  # 10 patients with 3-5 hour appointments
        '6-8_hours': int(4 * 2),  # 4 patients with 6-8 hour appointments
        '9+_hours': int(1 * 2)  # 1 patient with 9+ hour appointments
    }

    num_patients = sum(appointment_durations.values())

    appointment_times = {
        '1_hour': 60,
        '2_hours': 120,
        '3-5_hours': random.choice([180, 240, 300]),
        '6-8_hours': random.choice([360, 420, 480]),
        '9+_hours': random.choice([540, 600])
    }

    patient_id = 0
    for duration_type, count in appointment_durations.items():
        for _ in range(count):
            duration = appointment_times[duration_type]
            max_start_time = close_time - duration

            # Ensure start time is in 10-minute intervals
            start_time = random.randint(open_time // 10, max_start_time // 10) * 10

            acuity = random.randint(1, 3)
            patients.append({
                'patientId': patient_id,
                'readyTime': start_time,
                'length': duration,
                'dueTime': close_time,
                'acuity': acuity
            })
            patient_id += 1

    # Generate nursing schedule
    nurses = []
    center_open_hours = (close_time - open_time) // 60

    for i in range(num_nurses):
        shift_length = random.randint(8, center_open_hours)  # Shift length between 8 hours and the remaining open hours
        latest_start_hour = center_open_hours - shift_length
        start_hour = random.randint(0, latest_start_hour)
        shift_start = open_time + start_hour * 60
        shift_end = shift_start + shift_length * 60

        nurses.append({
            'nurseId': i,
            'startTime': shift_start,
            'endTime': shift_end
        })

    print(f"Number of Patients: {num_patients}")
    print(f"Number of Nurses: {num_nurses}")
    print(f"Number of Chairs: {num_chairs}")
    print(f"Maximum Patient Capacity per Nurse: {M}")
    print(f"Operating Hours: {convert_minutes_to_hhmm(open_time)} - {convert_minutes_to_hhmm(close_time)}")
    print("Patients:")
    for patient in patients:
        print(
            f"Patient ID: {patient['patientId']}, Ready Time: {convert_minutes_to_hhmm(patient['readyTime'])}, Due Time: {convert_minutes_to_hhmm(patient['dueTime'])}, Duration: {patient['length']} minutes, Acuity: {patient['acuity']}")

    print("Nurses:")
    for nurse in nurses:
        print(
            f"Nurse ID: {nurse['nurseId']}, Shift Start: {convert_minutes_to_hhmm(nurse['startTime'])}, Shift End: {convert_minutes_to_hhmm(nurse['endTime'])}")

    print("------------------------")

    return num_nurses, num_chairs, M, open_time, close_time, patients, nurses, break_start_time, break_end_time, break_duration


import pandas as pd
import random
import string

def generate_random_mrn():
    return ''.join(random.choices(string.digits, k=10))

def generate_random_name():
    first_names = ['John', 'Emma', 'James', 'Olivia', 'William', 'Ava', 'Noah', 'Sophia', 'Liam', 'Isabella']
    last_names = ['Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor']
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def generate_patient_excel(patients, file_path):
    # Generate random MRN and Patient Name
    for patient in patients:
        patient['patientMRN'] = generate_random_mrn()
        patient['patientName'] = generate_random_name()

    # Create a DataFrame
    df = pd.DataFrame(patients)

    df["readyTime"] = np.array([convert_minutes_to_hhmm(x) for x in df["readyTime"]])
    df["dueTime"] = np.array([convert_minutes_to_hhmm(x) for x in df["dueTime"]])


    # Rename columns to match the desired format
    df = df.rename(columns={
        'patientId': 'Patient ID',
        'patientMRN': 'Patient MRN',
        'patientName': 'Patient Name',
        'readyTime': 'Scheduled Tx Start Time',
        'length': 'Scheduled Tx Length (min)',
        'dueTime': 'Patient Due Time',
        'acuity': 'Acuity'
    })

    # Save the DataFrame to an Excel file
    df.to_csv(file_path, index=False)

def calculate_roi_metrics(allocation, patients, nurses, open_time, close_time, break_start_time, break_end_time,
                          break_duration):
    num_nurses = len(nurses)
    overtime_per_nurse = []
    patient_wait_times = []
    nurses_with_lunch_break = 0
    nurses_without_overtime = 0

    nurse_shifts = {nurse['nurseId']: [open_time, close_time] for nurse in nurses}

    for n in nurse_shifts.keys():
        nurse_shifts[n][0] = min((alloc[1] for alloc in allocation if alloc[4] == n), default=close_time)
        nurse_shifts[n][1] = max((alloc[2] for alloc in allocation if alloc[4] == n), default=open_time)

    # Calculate nurse overtime
    for n in nurses:
        nurse_id = n['nurseId']
        shift_end = nurse_shifts[nurse_id][1]
        overtime = max(0, shift_end - close_time)
        overtime_per_nurse.append(overtime)

        if overtime == 0:
            nurses_without_overtime += 1

    avg_overtime_per_nurse = np.mean(overtime_per_nurse) if overtime_per_nurse else 0

    # Calculate patient wait time
    for p in patients:
        for a in allocation:
            if a[0] == p['patientId']:
                wait_time = a[1] - p['readyTime']
                patient_wait_times.append(wait_time)
                break

    avg_patient_wait_time = np.mean(patient_wait_times) if patient_wait_times else 0

    # Calculate number of nurses with lunch break
    for n in range(num_nurses):
        nurse_id = nurses[n]['nurseId']
        has_lunch_break = False
        for t in range(break_start_time, break_end_time - break_duration + 1, 10):
            interval_has_start = any(t <= alloc[1] < t + break_duration for alloc in allocation if alloc[4] == nurse_id)
            # interval_has_end = any(t <= alloc[2] < t + break_duration for alloc in allocation if alloc[4] == nurse_id)
            if not interval_has_start:
                has_lunch_break = True
                break
            """
            if not interval_has_start and not interval_has_end:
                has_lunch_break = True
                break
            """
        if has_lunch_break:
            nurses_with_lunch_break += 1

    avg_nurses_with_lunch_break = nurses_with_lunch_break / num_nurses if num_nurses > 0 else 0

    # Calculate on-time closes
    ontime_closes = 1 if all(alloc[2] <= close_time for alloc in allocation) else 0

    metrics = {
        'avgOvertimePerNurse': avg_overtime_per_nurse,
        'avgPatientWaitTime': avg_patient_wait_time,
        'avgNursesWithLunchBreak': avg_nurses_with_lunch_break,
        'avgNursesWithoutOvertime': nurses_without_overtime / num_nurses if num_nurses > 0 else 0,
        'NumberOfOntimeCloses': ontime_closes
    }

    return metrics


def generate_naive_allocation(patients, nurses, num_chairs, open_time, close_time):
    patients_sorted = sorted(patients, key=lambda p: p['readyTime'])
    allocation = []
    chair_end_times = [open_time] * num_chairs
    nurse_index = 0
    num_nurses = len(nurses)

    for patient in patients_sorted:
        patient_id = patient['patientId']
        ready_time = patient['readyTime']
        duration = patient['length']

        # Find the chair with the earliest available end time
        earliest_chair_id = chair_end_times.index(min(chair_end_times))
        start_time = max(ready_time, chair_end_times[earliest_chair_id])
        end_time = start_time + duration

        # Assign the patient to this chair
        chair_end_times[earliest_chair_id] = end_time

        # Assign the next nurse in a round-robin fashion
        nurse_id = nurses[nurse_index]['nurseId']
        nurse_index = (nurse_index + 1) % num_nurses

        allocation.append((patient_id, start_time, end_time, earliest_chair_id, nurse_id))

    return allocation

def audit_allocation(allocation, patients, num_stations, num_nurses, open_time, close_time, M, break_start_time, break_end_time, break_duration):
    time_slots = range(open_time, close_time, 10)

    # Initialize tracking structures
    nurse_capacities = {nurse_id: 0 for nurse_id in range(num_nurses)}
    nurse_end_times = {nurse_id: [] for nurse_id in range(num_nurses)}
    chair_assignments = {chair_id: [] for chair_id in range(num_stations)}

    print("Audit Check:")

    # Constraint 1: Each patient has exactly one setup timeslot
    for p in patients:
        assigned_times = [alloc for alloc in allocation if alloc[0] == p['patientId']]
        if len(assigned_times) == 1:
            print("✔ Constraint 1: Each patient has exactly one setup timeslot for Patient", p['patientId'])
        else:
            print("✘ Constraint 1: Error in setup timeslot for Patient", p['patientId'])

    # Constraint 2: No appointment starts before its ready time
    ready_time_check = True
    for p in patients:
        for alloc in allocation:
            if alloc[0] == p['patientId'] and alloc[1] < p['readyTime']:
                print("✘ Constraint 2: Patient", p['patientId'], "starts before ready time.")
                ready_time_check = False
    if ready_time_check:
        print("✔ Constraint 2: No appointment starts before its ready time")

    # Objective 3: Each appointment must be completed before its due time and the end of the work-shift
    due_time_check = True
    for p in patients:
        for alloc in allocation:
            if alloc[0] == p['patientId'] and alloc[2] > min(p['dueTime'], close_time):
                print("✘ Objective 3: Patient", p['patientId'], "is not completed before due time.")
                due_time_check = False
    if due_time_check:
        print("✔ Objective 3: Each appointment must be completed before its due time and the end of the work-shift")

    # Constraint 4: The number of appointments running at every moment cannot exceed the number of stations
    station_check = True
    for t in time_slots:
        running_appointments = sum(1 for alloc in allocation if alloc[1] <= t < alloc[2])
        if running_appointments > num_stations:
            print("✘ Constraint 4: More appointments running than stations at time", t)
            station_check = False
    if station_check:
        print(
            "✔ Constraint 4: The number of appointments running at every moment does not exceed the number of stations")

    # Objective 5: The nursing capacity usage at every moment cannot exceed the instantaneous nursing capacity
    nursing_capacity_check = True
    for t in time_slots:
        monitoring_nursing_capacity = sum(1 for alloc in allocation if alloc[1] <= t <= alloc[2])
        if monitoring_nursing_capacity > M * num_nurses:
            print("✘ Objective 5: Nursing capacity exceeded at time", t)
            nursing_capacity_check = False
    if nursing_capacity_check:
        print(
            "✔ Objective 5: The nursing capacity usage at every moment does not exceed the instantaneous nursing capacity")


def h(y, break_time_start, break_time_end, num_nurses):
    break_time_mid = (break_time_start + break_time_end) / 2
    if break_time_start <= y < break_time_mid:
        break_nurses = math.ceil(float(num_nurses) / 2)
        return num_nurses - break_nurses
    elif break_time_mid <= y < break_time_end:
        break_nurses = math.floor(float(num_nurses) / 2)
        return num_nurses - break_nurses
    else:
        return num_nurses


def schedule_patients_all_constraints(patients, num_stations, num_nurses, open_time, close_time, M, break_start_time, break_end_time, break_duration):
    # Define the problem
    prob = pulp.LpProblem("InfusionCenterScheduling", pulp.LpMinimize)

    time_slots = range(open_time, close_time, 10)

    # Variables: x[p,t] = 1 if appointment p starts at timeslot t
    x = pulp.LpVariable.dicts("StartTimeslot", [(p['patientId'], t) for p in patients for t in time_slots],
                              cat='Binary')

    # Decision Variable

    # Define the last ending time of all patient's infusions
    # max_end_time = pulp.LpVariable("max_end_time", lowBound=open_time)

    # Add constraints to ensure max_end_time is the last ending time of all patients
    """
    for p in patients:
        for t in time_slots:
            prob += max_end_time >= (t + p['length']) * x[p['patientId'], t]
    """

    # Objective: Minimize total weighted deferring time and makespan
    # Differing Time: the difference between the ready time and the actual starting time
    # Makespan: the last ending time of the patients - but we will make the sum of all ending times
    deferring_time_weight = 1
    makespan_weight = 1
    overtime_weight = 10

    prob += (
            deferring_time_weight * pulp.lpSum(
        [((t - p['readyTime']) * x[p['patientId'], t]) for p in patients for t in time_slots]
    ) +
            makespan_weight * pulp.lpSum(
        [((t + p['length']) * x[p['patientId'], t]) for p in patients for t in time_slots]
    ) +
            overtime_weight * pulp.lpSum(
        [((max(0, (t + p['length'] - close_time))) * x[p['patientId'], t]) for p in patients for t in
         time_slots]
    )
    )

    # Constraints
    for p in patients:
        # Each appointment has exactly one setup timeslot
        prob += pulp.lpSum([x[p['patientId'], t] for t in time_slots]) == 1

        # No appointment starts before its ready time
        prob += pulp.lpSum([x[p['patientId'], t] for t in range(open_time, p['readyTime'], 10)]) == 0

        # This is something we should just check as a metric of how good the algorithm is doing...
        # Each appointment must be completed before its due time and the end of the work-shift
        prob += pulp.lpSum([(t + p['length']) * x[p['patientId'], t] for t in time_slots]) <= min(
            p['dueTime'], close_time)

    for t in time_slots:
        # Note: these are straight from the paper - so they must be correct
        # The number of appointments running at any moment cannot exceed the number of stations
        prob += pulp.lpSum([x[p['patientId'], t_prime] for p in patients for t_prime in
                            range(max(open_time, t - p['length']), t + 1, 10)]) <= num_stations

        # The nursing capacity usage at every moment cannot exceed the instantaneous nursing capacity
        # setting up a patient takes M capacity and monitoring takes 1, each nurse has capacity of M total
        """
        prob += (pulp.lpSum([x[p['patientId'], t_prime] for p in patients for t_prime in
                             range(max(open_time, t - p['length']), t + 1, 10)])
                 ) * (1 / M) + (pulp.lpSum([x[p['patientId'], t] for p in patients])) * (1 - (1 / M)) <= h(t, break_start_time, break_end_time, num_nurses)
        """

        # This says that setting up a patient and monitoring takes capacity of 1 and each nurse on duty has capacity of M total
        prob += pulp.lpSum([x[p['patientId'], t_prime] for p in patients for t_prime in
                            range(max(open_time, t - p['length']), t + 1, 10)]) <= h(t, break_start_time,
                                                                                       break_end_time, num_nurses) * M

    # Solve the problem
    prob.solve(pulp.PULP_CBC_CMD(timeLimit=60))

    # Extract the solution and assign patients to stations and nurses
    allocation = []
    chair_assignments = [0] * num_stations  # Tracks end time of the current assignment for each chair

    # Initialize nurse assignments and capacities
    nurse_breaks = {nurse_id: (0, 0) for nurse_id in range(num_nurses)}

    break_time_mid = (break_start_time + break_end_time) / 2

    # Assign breaks to nurses
    for nurse_id in range(num_nurses // 2):
        nurse_breaks[nurse_id] = (break_start_time, break_time_mid)

    for nurse_id in range(num_nurses // 2, num_nurses):
        nurse_breaks[nurse_id] = (break_time_mid, break_end_time)

    def is_nurse_on_break(nurse_id, time):
        return nurse_breaks[nurse_id][0] <= time < nurse_breaks[nurse_id][1]

    def nurse_already_setup(nurse_id, t):
        for p in setup_assignments[nurse_id]:
            if x[p['patientId'], t].varValue == 1:
                return True

        return False

    # Assign \(\left\lfloor \frac{P}{N} \right\rfloor\) setups to each nurse
    setup_count_per_nurse = len(patients) // num_nurses

    setup_assignments = {nurse_id: [] for nurse_id in range(num_nurses)}
    patient_nurse_setups = {p["id"]: 0 for p in patients}
    unassigned_setups = []

    for t in time_slots:
        for p in sorted(patients, key=lambda k: k['patientId']):
            if x[p['patientId'], t].varValue == 1:
                assigned = False
                for nurse_id in range(num_nurses):
                    if len(setup_assignments[nurse_id]) < setup_count_per_nurse and not is_nurse_on_break(nurse_id, t):
                        setup_assignments[nurse_id].append(p)
                        patient_nurse_setups[p["id"]] = nurse_id
                        assigned = True
                        break
                if not assigned:
                    unassigned_setups.append(p)

    for t in time_slots:
        for p in sorted(unassigned_setups, key=lambda k: k['patientId']):
            if x[p['patientId'], t].varValue == 1:
                for nurse_id in range(num_nurses):
                    if not is_nurse_on_break(nurse_id, t) and not nurse_already_setup(nurse_id, t):
                        setup_assignments[nurse_id].append(p)
                        patient_nurse_setups[p["id"]] = nurse_id
                        break

    for t in time_slots:
        for p in sorted(patients, key=lambda k: k['patientId']):
            if x[p['patientId'], t].varValue == 1:
                # Assign to the first available chair
                for chair_id in range(num_stations):
                    if chair_assignments[chair_id] <= t:
                        chair_assignments[chair_id] = t + p['length']
                        break  # stops going through the chairs

                allocation.append((p['patientId'], t, t + p['length'], chair_id, patient_nurse_setups[p["id"]]))

    return allocation


def schedule_patients_no_set_lunch(patients, num_stations, num_nurses, open_time, close_time, M, break_start_time, break_end_time, break_duration):
    # Define the problem
    prob = pulp.LpProblem("InfusionCenterScheduling", pulp.LpMinimize)

    time_slots = range(open_time, close_time, 10)

    # Variables: x[p,t] = 1 if appointment p starts at timeslot t
    x = pulp.LpVariable.dicts("StartTimeslot", [(p['patientId'], t) for p in patients for t in time_slots],
                              cat='Binary')

    # Decision Variable
    # Objective: Minimize total weighted deferring time and makespan
    # Differing Time: the difference between the ready time and the actual starting time
    # Makespan: the last ending time of the patients - but we will make the sum of all ending times
    deferring_time_weight = 1
    makespan_weight = 1

    prob += (
            deferring_time_weight * pulp.lpSum(
        [((t - p['readyTime']) * x[p['patientId'], t]) for p in patients for t in time_slots]
    ) +
            makespan_weight * pulp.lpSum(
        [((t + p['length']) * x[p['patientId'], t]) for p in patients for t in time_slots]
    )
    )

    # Constraints
    for p in patients:
        # Each appointment has exactly one setup timeslot
        prob += pulp.lpSum([x[p['patientId'], t] for t in time_slots]) == 1

        # No appointment starts before its ready time
        prob += pulp.lpSum([x[p['patientId'], t] for t in range(open_time, p['readyTime'], 10)]) == 0

        # This is something we should just check as a metric of how good the algorithm is doing...
        # Each appointment must be completed before its due time and the end of the work-shift
        prob += pulp.lpSum([(t + p['length']) * x[p['patientId'], t] for t in time_slots]) <= min(
            p['dueTime'], close_time)

    for t in time_slots:
        # Note: these are straight from the paper - so they must be correct
        # The number of appointments running at any moment cannot exceed the number of stations
        prob += pulp.lpSum([x[p['patientId'], t_prime] for p in patients for t_prime in
                            range(max(open_time, t - p['length']), t + 1, 10)]) <= num_stations

        # The nursing capacity usage at every moment cannot exceed the instantaneous nursing capacity
        # setting/finishing up a patient takes M capacity and monitoring takes 1, each nurse has capacity of M total

        prob += (
                pulp.lpSum([x[p['patientId'], t_prime] for p in patients for t_prime in
                            range(max(open_time, t - p['length']), t + 1, 10)]) * (1 / M) +
                pulp.lpSum([x[p['patientId'], t] for p in patients]) * (1 - (1 / M)) +
                pulp.lpSum([x[p['patientId'], t - p['length']] for p in patients if t - p['length'] in time_slots]) * (
                        1 - (1 / M))
                <= num_nurses)

    # Solve the problem
    prob.solve(pulp.PULP_CBC_CMD(timeLimit=60))

    if prob.status == pulp.LpStatusOptimal:

        # Extract the solution and assign patients to stations and nurses
        allocation = []
        chair_assignments = [0] * num_stations  # Tracks end time of the current assignment for each chair
        nurse_capacities = {nurse_id: 0 for nurse_id in
                            range(num_nurses)}  # Tracks current capacity usage for each nurse
        nurse_end_times = {nurse_id: [] for nurse_id in
                           range(num_nurses)}  # Tracks end times of patients assigned to each nurse
        nurse_index = 0

        for t in time_slots:
            for p in sorted(patients, key=lambda k: k['patientId']):
                if x[p['patientId'], t].varValue == 1:
                    # Assign to the first available chair
                    for chair_id in range(num_stations):
                        if chair_assignments[chair_id] <= t:
                            chair_assignments[chair_id] = t + p['length']
                            break  # stops going through the chairs

                    # Assign to the first available nurse with capacity
                    for nurse_id in range(nurse_index, num_nurses):
                        if nurse_capacities[nurse_id] < M:
                            nurse_capacities[nurse_id] += 1
                            nurse_end_times[nurse_id].append(t + p['length'])
                            break

                    nurse_index = (nurse_index + 1) % num_nurses

                    allocation.append((p['patientId'], t, t + p['length'], chair_id, nurse_id))

            # Update nurse capacities after assignment
            for nurse_id in range(num_nurses):
                for end_time in nurse_end_times[nurse_id]:
                    if t >= end_time:
                        nurse_capacities[nurse_id] -= 1
                # Remove processed end times
                nurse_end_times[nurse_id] = [et for et in nurse_end_times[nurse_id] if et > t]

        return allocation
    else:
        return None


def schedule_patients_no_constraint(patients, num_stations, num_nurses, open_time, close_time, M, break_start_time, break_end_time, break_duration):
    # Define the problem
    prob = pulp.LpProblem("InfusionCenterScheduling", pulp.LpMinimize)

    time_slots = range(open_time, close_time, 10)

    # Variables: x[p,t] = 1 if appointment p starts at timeslot t
    x = pulp.LpVariable.dicts("StartTimeslot", [(p['patientId'], t) for p in patients for t in time_slots],
                              cat='Binary')

    # Decision Variable

    # Objective: Minimize total weighted deferring time and makespan
    # Differing Time: the difference between the ready time and the actual starting time
    # Makespan: the last ending time of the patients - but we will make the sum of all ending times
    deferring_time_weight = 1
    makespan_weight = 1
    overtime_weight = 10

    prob += (
            deferring_time_weight * pulp.lpSum(
        [((t - p['readyTime']) * x[p['patientId'], t]) for p in patients for t in time_slots]
    ) +
            makespan_weight * pulp.lpSum(
        [((t + p['length']) * x[p['patientId'], t]) for p in patients for t in time_slots]
    ) +
            overtime_weight * pulp.lpSum(
        [((max(0, (t + p['length'] - close_time))) * x[p['patientId'], t]) for p in patients for t in
         time_slots]
    )
    )

    # Constraints
    for p in patients:
        # Each appointment has exactly one setup timeslot
        prob += pulp.lpSum([x[p['patientId'], t] for t in time_slots]) == 1

        # No appointment starts before its ready time
        prob += pulp.lpSum([x[p['patientId'], t] for t in range(open_time, p['readyTime'], 10)]) == 0

        """
        # This is something we should just check as a metric of how good the algorithm is doing...
        # Each appointment must be completed before its due time and the end of the work-shift
        prob += pulp.lpSum([(t + p['length']) * x[p['patientId'], t] for t in time_slots]) <= min(
            p['dueTime'], close_time)

        """

    for t in time_slots:
        # Note: these are straight from the paper - so they must be correct
        # The number of appointments running at any moment cannot exceed the number of stations
        prob += pulp.lpSum([x[p['patientId'], t_prime] for p in patients for t_prime in
                            range(max(open_time, t - p['length']), t + 1, 10)]) <= num_stations

        # The nursing capacity usage at every moment cannot exceed the instantaneous nursing capacity
        # setting/finishing up a patient takes M capacity and monitoring takes 1, each nurse has capacity of M total

        prob += (
                pulp.lpSum([x[p['patientId'], t_prime] for p in patients for t_prime in
                            range(max(open_time, t - p['length']), t + 1, 10)]) * (1 / M) +
                pulp.lpSum([x[p['patientId'], t] for p in patients]) * (1 - (1 / M)) +
                pulp.lpSum([x[p['patientId'], t - p['length']] for p in patients if t - p['length'] in time_slots]) * (
                        1 - (1 / M))
                <= num_nurses)

    # Solve the problem
    prob.solve(pulp.PULP_CBC_CMD(timeLimit=60))

    if prob.status == pulp.LpStatusOptimal:

        # Extract the solution and assign patients to stations and nurses
        allocation = []
        chair_assignments = [0] * num_stations  # Tracks end time of the current assignment for each chair
        nurse_capacities = {nurse_id: 0 for nurse_id in
                            range(num_nurses)}  # Tracks current capacity usage for each nurse
        nurse_end_times = {nurse_id: [] for nurse_id in
                           range(num_nurses)}  # Tracks end times of patients assigned to each nurse
        nurse_index = 0

        for t in time_slots:
            for p in sorted(patients, key=lambda k: k['patientId']):
                if x[p['patientId'], t].varValue == 1:
                    # Assign to the first available chair
                    for chair_id in range(num_stations):
                        if chair_assignments[chair_id] <= t:
                            chair_assignments[chair_id] = t + p['length']
                            break  # stops going through the chairs

                    # Assign to the first available nurse with capacity
                    for nurse_id in range(nurse_index, num_nurses):
                        if nurse_capacities[nurse_id] < M:
                            nurse_capacities[nurse_id] += 1
                            nurse_end_times[nurse_id].append(t + p['length'])
                            break

                    nurse_index = (nurse_index + 1) % num_nurses

                    allocation.append((p['patientId'], t, t + p['length'], chair_id, nurse_id))

            # Update nurse capacities after assignment
            for nurse_id in range(num_nurses):
                for end_time in nurse_end_times[nurse_id]:
                    if t >= end_time:
                        nurse_capacities[nurse_id] -= 1
                # Remove processed end times
                nurse_end_times[nurse_id] = [et for et in nurse_end_times[nurse_id] if et > t]

        return allocation
    else:
        return None