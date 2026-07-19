# ==========================================
# SIMPLE & STABLE SEATING ALGORITHM
# ==========================================

def generate_seating(branch_names, students_by_branch, rooms):

    allotment = []

    # -------------------------------
    # Split branches into Odd & Even
    # -------------------------------
    mid = (len(branch_names) + 1) // 2

    odd_branches = branch_names[:mid]
    even_branches = branch_names[mid:]

    odd_students = []
    even_students = []

    # Collect students
    for b in odd_branches:
        for s in students_by_branch.get(b, []):
            odd_students.append({
                "student_id": s["student_id"],
                "pin": s["pin_number"],
                "branch": b
            })

    for b in even_branches:
        for s in students_by_branch.get(b, []):
            even_students.append({
                "student_id": s["student_id"],
                "pin": s["pin_number"],
                "branch": b
            })

    odd_index = 0
    even_index = 0

    # -------------------------------
    # Room by Room
    # -------------------------------
    for room in rooms:

        room_id = room["room_id"]
        rows = room["num_rows"]
        cols = room["num_cols"]

        # Row-wise
        for r in range(1, rows + 1):

            # Odd columns first
            for c in range(1, cols + 1, 2):

                if odd_index >= len(odd_students):
                    continue

                s = odd_students[odd_index]

                allotment.append({
                    "room_id": room_id,
                    "num_row": r,
                    "num_col": c,
                    "student_id": s["student_id"],
                    "pin": s["pin"],
                    "branch": s["branch"]
                })

                odd_index += 1

            # Even columns
            for c in range(2, cols + 1, 2):

                if even_index >= len(even_students):
                    continue

                s = even_students[even_index]

                allotment.append({
                    "room_id": room_id,
                    "num_row": r,
                    "num_col": c,
                    "student_id": s["student_id"],
                    "pin": s["pin"],
                    "branch": s["branch"]
                })

                even_index += 1

    return allotment
