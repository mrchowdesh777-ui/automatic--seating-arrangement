# ==========================================
# SEATING ALGORITHM - PART 1
# ==========================================
import random
import time
def generate_seating(branch_names, students_by_branch, rooms):
    seed=int(time.time())
    random.seed(seed)

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
#random
    random.shuffle(active)

    if len(active) == 0:
        return allotment

    # Initial Pattern
    # Row1 -> CM EC
    # Row2 -> EE C

    pairA = [0, 1]
    pairB = [2, 3]

    next_branch = 4

    # Room Loop
    for room in rooms:

        room_id = room["room_id"]
        rows = room["num_rows"]
        cols = room["num_cols"]

        for r in range(1, rows + 1):

            if r % 2 == 1:
                current_pair = pairA
            else:
                current_pair = pairB

            for c in range(1, cols + 1):

                if c % 2 == 1:
                    pos = 0
                else:
                    pos = 1

                index = current_pair[pos]

                if index >= len(active):
                    continue

                branch = active[index]
                # ----------------------------------
                # If branch finished, replace it
                # ----------------------------------

                while len(branches[branch]) == 0:

                    if next_branch >= len(active):
                        break

                    current_pair[pos] = next_branch

                    index = current_pair[pos]

                    branch = active[index]

                    next_branch += 1

                # No replacement available
                if len(branches[branch]) == 0:
                    continue

                # ----------------------------------
                # Allocate one student
                # ----------------------------------

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

                # -----------------------------
                # Branch finished?
                # Replace only the current position
                # -----------------------------

                if c % 2 == 1:
                    pos = 0
                else:
                    pos = 1

                while len(branches[branch]) == 0:

                    found = False

                    # Find next branch having students
                    while next_branch < len(active):

                        if len(branches[active[next_branch]]) > 0:

                            current_pair[pos] = next_branch

                            index = next_branch
                            branch = active[index]

                            next_branch += 1
                            found = True
                            break

                        next_branch += 1

                    # No new branches left
                    if not found:

                        found = False

                        # Reuse any branch that still has students
                        for i in range(len(active)):

                            if len(branches[active[i]]) > 0:

                                # Don't use the branch already in the other position
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

    # -----------------------------------
    # Return final seating allotment
    # -----------------------------------

    return allotment
