

def analyze_students(n, k, m, records):
    semesters = {}
    subject_toppers = {}

    for record in records:
        enrollment, name, semester, cpi, marks = record
        average = sum(marks) / m

        student = {
            "enrollment": enrollment,
            "name": name,
            "cpi": cpi,
            "average": average,
            "marks": marks
        }

        if semester not in semesters:
            semesters[semester] = []

        semesters[semester].append(student)

        for i in range(m):
            subject = f"S{i + 1}"
            mark = marks[i]

            if subject not in subject_toppers:
                subject_toppers[subject] = {
                    "mark": mark,
                    "enrollments": [enrollment]
                }
            elif mark > subject_toppers[subject]["mark"]:
                subject_toppers[subject] = {
                    "mark": mark,
                    "enrollments": [enrollment]
                }
            elif mark == subject_toppers[subject]["mark"]:
                subject_toppers[subject]["enrollments"].append(
                    enrollment
                )

    for semester in sorted(semesters):
        students = semesters[semester]

        students.sort(
            key=lambda s: (
                -s["cpi"],
                -s["average"],
                s["enrollment"]
            )
        )

        top_students = students[:k]
        enrollments = [
            student["enrollment"] for student in top_students
        ]

        print(f"Semester {semester}: {' '.join(enrollments)}")

    for i in range(m):
        subject = f"S{i + 1}"
        toppers = sorted(subject_toppers[subject]["enrollments"])
        print(f"{subject}: {' '.join(toppers)}")


def main():
    USE_SAMPLE = True

    if USE_SAMPLE:
        n, k, m = 5, 2, 3

        records = [
            ("2201", "Asha", 5, 8.90, [90, 82, 75]),
            ("2202", "Bharat", 5, 8.90, [88, 95, 70]),
            ("2203", "Chaitra", 3, 9.10, [91, 88, 92]),
            ("2204", "Dev", 5, 7.80, [76, 80, 85]),
            ("2205", "Esha", 3, 9.10, [91, 90, 88])
        ]
    else:
        n, k, m = map(int, input().split())
        records = []

        for _ in range(n):
            data = input().split()

            enrollment = data[0]
            name = data[1]
            semester = int(data[2])
            cpi = float(data[3])
            marks = list(map(int, data[4:4 + m]))

            records.append(
                (enrollment, name, semester, cpi, marks)
            )

    analyze_students(n, k, m, records)


if __name__ == "__main__":
    main()
