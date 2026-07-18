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

    return allotment