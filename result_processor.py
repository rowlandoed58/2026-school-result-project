"""
Student Result Processor
-------------------------
Reads exam scores from results.csv, analyzes them, prints a full
report to the screen, and saves the same report to report.txt.

No classes, no pandas — just functions, dictionaries, and loops.
"""

import csv

CSV_FILE = "results.csv"
REPORT_FILE = "report.txt"


def load_data(filename):
    """
    Reads the CSV file into a list of dictionaries, one per student.
    Any score that is missing or not a valid number is skipped
    instead of crashing the program.
    Returns (students, subjects).
    """
    students = []
    subjects = []

    with open(filename, newline="") as f:
        reader = csv.DictReader(f)
        subjects = [col for col in reader.fieldnames if col != "name"]

        for row in reader:
            student = {"name": row["name"]}
            for subject in subjects:
                raw_value = row.get(subject, "")
                try:
                    student[subject] = float(raw_value)
                except (ValueError, TypeError):
                    continue
            students.append(student)

    return students, subjects


def get_grade(average):
    """Converts a numeric average into a letter grade."""
    if average >= 70:
        return "A"
    elif average >= 60:
        return "B"
    elif average >= 50:
        return "C"
    elif average >= 45:
        return "D"
    else:
        return "F"


def student_average(student, subjects):
    """Average of a single student's scores across the subjects they have."""
    scores = [student[s] for s in subjects if s in student]
    if not scores:
        return 0.0
    return sum(scores) / len(scores)


def compute_student_results(students, subjects):
    """Builds one dict per student with their name, average, and grade."""
    results = []
    for student in students:
        avg = student_average(student, subjects)
        grade = get_grade(avg)
        results.append({"name": student["name"], "average": avg, "grade": grade})
    return results


def compute_subject_averages(students, subjects):
    """Returns a dict {subject: class_average} across all students."""
    subject_averages = {}
    for subject in subjects:
        scores = [student[subject] for student in students if subject in student]
        subject_averages[subject] = sum(scores) / len(scores) if scores else 0.0
    return subject_averages


def find_top_student(student_results):
    """Returns the student dict with the highest average."""
    return max(student_results, key=lambda s: s["average"])


def count_pass_fail(student_results, pass_mark=50):
    """Counts how many students passed vs failed."""
    passed = sum(1 for s in student_results if s["average"] >= pass_mark)
    failed = len(student_results) - passed
    return passed, failed


def rank_students(student_results):
    """Highest to lowest average."""
    return sorted(student_results, key=lambda s: s["average"], reverse=True)


def rank_subjects_hardest_to_easiest(subject_averages):
    """Lowest class average first (hardest), highest last (easiest)."""
    return sorted(subject_averages.items(), key=lambda item: item[1])


def subject_summary(students, subjects, subject_name):
    """
    Returns class average, highest score, and lowest score for the
    requested subject, or None if the subject doesn't exist.
    """
    match = next((s for s in subjects if s.lower() == subject_name.lower()), None)
    if match is None:
        return None

    scored_students = [(st["name"], st[match]) for st in students if match in st]
    if not scored_students:
        return None

    avg = sum(score for _, score in scored_students) / len(scored_students)
    highest_student, highest_score = max(scored_students, key=lambda x: x[1])
    lowest_student, lowest_score = min(scored_students, key=lambda x: x[1])

    return {
        "subject": match,
        "average": avg,
        "highest_score": highest_score,
        "highest_student": highest_student,
        "lowest_score": lowest_score,
        "lowest_student": lowest_student,
    }


def build_report(students, subjects, student_results, subject_averages,
                  top_student, passed, failed, ranked_students,
                  ranked_subjects):
    """Assembles the full report as one big string."""
    lines = []
    add = lines.append

    add("=" * 55)
    add("STUDENT RESULT PROCESSOR — REPORT")
    add("=" * 55)
    add("")

    add("1) PER-STUDENT AVERAGE & GRADE")
    add("-" * 55)
    for s in student_results:
        add(f"   {s['name']:<20} avg={s['average']:.2f}  grade={s['grade']}")
    add("")

    add("2) CLASS AVERAGE PER SUBJECT")
    add("-" * 55)
    for subject in subjects:
        add(f"   {subject:<15} class avg = {subject_averages[subject]:.2f}")
    add("")

    add("3) TOP STUDENT (highest overall average)")
    add("-" * 55)
    add(f"   {top_student['name']}  ({top_student['average']:.2f})")
    add("")

    add("4) PASS / FAIL COUNT (pass = overall avg >= 50)")
    add("-" * 55)
    add(f"   Passed: {passed}    Failed: {failed}")
    add("")

    add("5) STUDENT LEADERBOARD (highest to lowest average)")
    add("-" * 55)
    for i, s in enumerate(ranked_students, start=1):
        add(f"   {i}. {s['name']:<20} {s['average']:.2f}  ({s['grade']})")
    add("")

    add("6) SUBJECTS RANKED HARDEST TO EASIEST (lowest avg = hardest)")
    add("-" * 55)
    for i, (subject, avg) in enumerate(ranked_subjects, start=1):
        tag = ""
        if i == 1:
            tag = "  <- hardest"
        elif i == len(ranked_subjects):
            tag = "  <- easiest"
        add(f"   {i}. {subject:<15} {avg:.2f}{tag}")
    add("")

    all_scores = [score for student in students for score in student.values() if isinstance(score, float)]
    overall_avg = sum(all_scores) / len(all_scores) if all_scores else 0.0
    add("7) OVERALL CLASS AVERAGE (all scores): " + f"{overall_avg:.2f}")
    add("")

    return "\n".join(lines)


def main():
    students, subjects = load_data(CSV_FILE)

    student_results = compute_student_results(students, subjects)
    subject_averages = compute_subject_averages(students, subjects)
    top_student = find_top_student(student_results)
    passed, failed = count_pass_fail(student_results)
    ranked_students = rank_students(student_results)
    ranked_subjects = rank_subjects_hardest_to_easiest(subject_averages)

    report_text = build_report(
        students, subjects, student_results, subject_averages,
        top_student, passed, failed, ranked_students, ranked_subjects
    )

    print(report_text)

    with open(REPORT_FILE, "w") as f:
        f.write(report_text)

    print("-" * 55)
    subject_name = input(f"Enter a subject name to look up {subjects}: ").strip()
    summary = subject_summary(students, subjects, subject_name)

    lookup_lines = []
    if summary is None:
        msg = f"\nNo such subject: '{subject_name}'. Try one of {subjects}."
        print(msg)
        lookup_lines.append(msg)
    else:
        lookup_lines.append("")
        lookup_lines.append(f"SUBJECT LOOKUP: {summary['subject']}")
        lookup_lines.append("-" * 55)
        lookup_lines.append(f"   Class average : {summary['average']:.2f}")
        lookup_lines.append(
            f"   Highest score : {summary['highest_score']:.2f} "
            f"({summary['highest_student']})"
        )
        lookup_lines.append(
            f"   Lowest score  : {summary['lowest_score']:.2f} "
            f"({summary['lowest_student']})"
        )
        for line in lookup_lines:
            print(line)

    with open(REPORT_FILE, "a") as f:
        f.write("\n".join(lookup_lines))
        f.write("\n")


if __name__ == "__main__":
    main()
