
import os
import pandas as pd
import matplotlib.pyplot as plt


def main():
    csv_path = input("Enter path of marks CSV file: ").strip().strip('"')
    output_folder = input("Enter output folder path: ").strip().strip('"')

    if not os.path.isfile(csv_path):
        print("Error: CSV file not found.")
        return

    os.makedirs(output_folder, exist_ok=True)

    try:
        df = pd.read_csv(csv_path)
    except Exception as error:
        print("Could not read CSV:", error)
        return

    required_columns = {"enrollment", "name"}
    if not required_columns.issubset(df.columns):
        print("CSV must contain enrollment and name columns.")
        return

    subject_columns = [
        column for column in df.columns
        if column not in ["enrollment", "name"]
    ]

    if not subject_columns:
        print("No subject columns found.")
        return

    if df.empty:
        print("The CSV contains no student records.")
        return

    # Convert subject marks to numbers.
    # Invalid values and marks outside 0-100 become missing.
    for subject in subject_columns:
        df[subject] = pd.to_numeric(df[subject], errors="coerce")
        df.loc[~df[subject].between(0, 100), subject] = float("nan")

    # Remove rows where every subject mark is missing.
    df = df.dropna(subset=subject_columns, how="all").copy()

    if df.empty:
        print("No valid marks found in the dataset.")
        return

    # Fill missing marks using the average of each subject.
    for subject in subject_columns:
        average = df[subject].mean()
        df[subject] = df[subject].fillna(average)

    # Save cleaned dataset.
    cleaned_path = os.path.join(output_folder, "cleaned_marks.csv")
    df.to_csv(cleaned_path, index=False)

    # Subject-wise summary statistics.
    summary = pd.DataFrame({
        "Subject": subject_columns,
        "Average": [df[s].mean() for s in subject_columns],
        "Median": [df[s].median() for s in subject_columns],
        "Minimum": [df[s].min() for s in subject_columns],
        "Maximum": [df[s].max() for s in subject_columns]
    })

    summary_path = os.path.join(output_folder, "summary.csv")
    summary.to_csv(summary_path, index=False)

    # Calculate each student's average mark.
    df["Average_Marks"] = df[subject_columns].mean(axis=1)

    # Grade distribution across all subject marks.
    all_marks = df[subject_columns].values.flatten()

    grades = pd.cut(
        all_marks,
        bins=[-1, 59, 69, 79, 89, 100],
        labels=["F (<60)", "D (60-69)", "C (70-79)",
                "B (80-89)", "A (90-100)"]
    )

    grade_counts = grades.value_counts().sort_index()

    plt.figure(figsize=(8, 5))
    grade_counts.plot(kind="bar")
    plt.title("Grade Distribution")
    plt.xlabel("Grade")
    plt.ylabel("Number of Marks")
    plt.tight_layout()
    plt.savefig(
        os.path.join(output_folder, "grade_distribution.png")
    )
    plt.close()

    # Subject-wise average comparison.
    plt.figure(figsize=(8, 5))
    plt.bar(summary["Subject"], summary["Average"])
    plt.title("Subject-wise Average Marks")
    plt.xlabel("Subject")
    plt.ylabel("Average Marks")
    plt.ylim(0, 100)
    plt.tight_layout()
    plt.savefig(
        os.path.join(output_folder, "subject_average.png")
    )
    plt.close()

    # Top 10 students by average marks.
    top_students = df.nlargest(10, "Average_Marks").sort_values(
        "Average_Marks"
    )

    plt.figure(figsize=(9, 6))
    plt.barh(
        top_students["name"],
        top_students["Average_Marks"]
    )
    plt.title("Top Performers")
    plt.xlabel("Average Marks")
    plt.ylabel("Student")
    plt.xlim(0, 100)
    plt.tight_layout()
    plt.savefig(
        os.path.join(output_folder, "top_performers.png")
    )
    plt.close()

    print("\nDashboard export completed successfully!")
    print("Cleaned data:", cleaned_path)
    print("Summary:", summary_path)
    print("Charts saved in:", output_folder)


if __name__ == "__main__":
    main()
