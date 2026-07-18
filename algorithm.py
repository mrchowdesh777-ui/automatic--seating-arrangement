from collections import deque

def generate_seating(branch_names, students_by_branch, rooms):

    allotment = []

    queues = {}
    for b in branch_names:
        queues[b] = deque(students_by_branch.get(b, []))

    group_a = branch_names[::2]   # 1st,3rd,5th...
    group_b = branch_names[1::2]  # 2nd,4th...

    a = 0
    b = 0

    for room in rooms:

        room_id = room["room_id"]

        for r in range(1, room["num_rows"] + 1):
            for c in range(1, room["num_cols"] + 1):

                if c % 2 == 1:

                    while a < len(group_a) and len(queues[group_a[a]]) == 0:
                        a += 1

                    if a >= len(group_a):
                        continue

                    branch = group_a[a]

                else:

                    while b < len(group_b) and len(queues[group_b[b]]) == 0:
                        b += 1

                    if b >= len(group_b):
                        continue

                    branch = group_b[b]

                student = queues[branch].popleft()

                allotment.append({
                    "room_id": room_id,
                    "num_row": r,
                    "num_col": c,
                    "student_id": student["student_id"],
                    "pin": student["pin_number"],
                    "branch": branch
                })

    return allotment# ==========================================
# SEATING ALGORITHM - VERTICAL FILLING
# ==========================================

def generate_seating(branch_names, students_by_branch, rooms):

    allotment = []

    # Copy all students branch-wise
    branches = {}

    for b in branch_names:
        branches[b] = students_by_branch.get(b, []).copy()

    # Branches having students
    active = []

    for b in branch_names:
        if len(branches[b]) > 0:
            active.append(b)

    if len(active) == 0:
        return allotment

    # Initial Pattern
    pairA = [0, 1]
    pairB = [2, 3]

    next_branch = 4

    # Room Loop
    for room in rooms:

        room_id = room["room_id"]
        rows = room["num_rows"]
        cols = room["num_cols"]

        # COLUMN FIRST (Vertical Seating)
        for c in range(1, cols + 1):

            for r in range(1, rows + 1):

                if r % 2 == 1:
                    current_pair = pairA
                else:
                    current_pair = pairB

                if c % 2 == 1:
                    pos = 0
                else:
                    pos = 1

                index = current_pair[pos]

                if index >= len(active):
                    continue

                branch = active[index]

                # Replace finished branch
                while len(branches[branch]) == 0:

                    if next_branch >= len(active):
                        break

                    current_pair[pos] = next_branch
                    index = current_pair[pos]
                    branch = active[index]
                    next_branch += 1

                if len(branches[branch]) == 0:
                    continue

                # Allocate student
                student = branches[branch].pop(0)

                seat = {
                    "room_id": room_id,
                    "num_row": r,
                    "num_col": c,
                    "pin": student["pin_number"],
                    "student_id": student["student_id"],
                    "branch": branch
                }

                allotment.append(seat)

                # Branch finished?
                if c % 2 == 1:
                    pos = 0
                else:
                    pos = 1

                while len(branches[branch]) == 0:

                    found = False

                    while next_branch < len(active):

                        if len(branches[active[next_branch]]) > 0:

                            current_pair[pos] = next_branch
                            index = next_branch
                            branch = active[index]

                            next_branch += 1
                            found = True
                            break

                        next_branch += 1

                    if not found:

                        found = False

                        for i in range(len(active)):

                            if len(branches[active[i]]) > 0:

                                if current_pair[1 - pos] != i:

                                    current_pair[pos] = i
                                    index = i
                                    branch = active[i]

                                    found = True
                                    break

                        if not found:
                            break

                if len(branches[branch]) == 0:
                    continue

    return allotment