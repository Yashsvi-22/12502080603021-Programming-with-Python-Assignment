
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv
import os


DATA_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "assignment_data.json"
)


class AssignmentTracker:

    def __init__(self, root):
        self.root = root
        self.root.title("Student Assignment Tracker")
        self.root.geometry("970x500")
        self.root.minsize(750, 450)

        self.students = {}
        self.submissions = []

        self.load_data()
        self.create_widgets()
        self.refresh_table()

   
    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as file:
                    data = json.load(file)

                self.students = data.get("students", {})
                self.submissions = data.get("submissions", [])

            except (json.JSONDecodeError, OSError):
                messagebox.showwarning(
                    "Warning",
                    "Saved data could not be loaded. Starting with empty data."
                )
                self.students = {}
                self.submissions = []

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as file:
                json.dump(
                    {
                        "students": self.students,
                        "submissions": self.submissions
                    },
                    file,
                    indent=4
                )
        except OSError as error:
            messagebox.showerror(
                "Save Error",
                f"Could not save data:\n{error}"
            )

    def create_widgets(self):

        title = ttk.Label(
            self.root,
            text="Student Assignment Tracker",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=12)

        student_frame = ttk.LabelFrame(
            self.root,
            text="Student Details",
            padding=10
        )
        student_frame.pack(fill="x", padx=8, pady=5)

        ttk.Label(student_frame, text="Enrollment No:").grid(
            row=0, column=0, padx=5, pady=5
        )

        self.enrollment_entry = ttk.Entry(student_frame, width=18)
        self.enrollment_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(student_frame, text="Student Name:").grid(
            row=0, column=2, padx=5, pady=5
        )

        self.name_entry = ttk.Entry(student_frame, width=20)
        self.name_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(
            student_frame,
            text="Add Student",
            command=self.add_student
        ).grid(row=0, column=4, padx=8, pady=5)

        submission_frame = ttk.LabelFrame(
            self.root,
            text="Submission Details",
            padding=10
        )
        submission_frame.pack(fill="x", padx=8, pady=5)

        ttk.Label(submission_frame, text="Assignment:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )

        self.assignment_entry = ttk.Entry(
            submission_frame, width=18
        )
        self.assignment_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(submission_frame, text="Status:").grid(
            row=0, column=2, padx=5, pady=5, sticky="w"
        )

        self.status_combo = ttk.Combobox(
            submission_frame,
            values=["Pending", "Completed"],
            state="readonly",
            width=16
        )
        self.status_combo.set("Pending")
        self.status_combo.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(submission_frame, text="Marks:").grid(
            row=1, column=0, padx=5, pady=5, sticky="w"
        )

        self.marks_entry = ttk.Entry(submission_frame, width=18)
        self.marks_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(submission_frame, text="Total Marks:").grid(
            row=1, column=2, padx=5, pady=5, sticky="w"
        )

        self.total_entry = ttk.Entry(submission_frame, width=16)
        self.total_entry.grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(submission_frame, text="Remarks:").grid(
            row=2, column=0, padx=5, pady=5, sticky="w"
        )

        self.remarks_entry = ttk.Entry(
            submission_frame, width=45
        )
        self.remarks_entry.grid(
            row=2, column=1, columnspan=3,
            padx=5, pady=5, sticky="ew"
        )

        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=8, pady=5)

        ttk.Button(
            button_frame,
            text="Add Submission",
            command=self.add_submission
        ).pack(side="left", padx=4, pady=4)

        ttk.Button(
            button_frame,
            text="Update Selected Marks",
            command=self.update_marks
        ).pack(side="left", padx=4, pady=4)

        ttk.Button(
            button_frame,
            text="Delete Selected Submission",
            command=self.delete_selected_submission
        ).pack(side="left", padx=4, pady=4)

        ttk.Button(
            button_frame,
            text="Delete Selected Student",
            command=self.delete_selected_student
        ).pack(side="left", padx=4, pady=4)

        ttk.Button(
            button_frame,
            text="Clear Form",
            command=self.clear_form
        ).pack(side="left", padx=4, pady=4)

        ttk.Button(
            button_frame,
            text="Export CSV",
            command=self.export_csv
        ).pack(side="left", padx=4, pady=4)

        filter_frame = ttk.Frame(self.root)
        filter_frame.pack(fill="x", padx=8, pady=4)

        ttk.Label(
            filter_frame,
            text="Filter Submissions:"
        ).pack(side="left", padx=5)

        self.filter_combo = ttk.Combobox(
            filter_frame,
            values=["All", "Pending", "Completed"],
            state="readonly",
            width=15
        )
        self.filter_combo.set("All")
        self.filter_combo.pack(side="left", padx=5)
        self.filter_combo.bind(
            "<<ComboboxSelected>>",
            lambda event: self.refresh_table()
        )

        table_frame = ttk.Frame(self.root)
        table_frame.pack(
            fill="both", expand=True, padx=8, pady=5
        )

        columns = (
            "enrollment",
            "name",
            "assignment",
            "status",
            "marks",
            "remarks"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        headings = {
            "enrollment": "Enrollment",
            "name": "Student Name",
            "assignment": "Assignment",
            "status": "Status",
            "marks": "Marks",
            "remarks": "Remarks"
        }

        widths = {
            "enrollment": 130,
            "name": 150,
            "assignment": 150,
            "status": 100,
            "marks": 100,
            "remarks": 200
        }

        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(
                column,
                width=widths[column],
                anchor="center"
            )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.select_record
        )

    def add_student(self):
        enrollment = self.enrollment_entry.get().strip()
        name = self.name_entry.get().strip()

        if not enrollment or not name:
            messagebox.showwarning(
                "Input Error",
                "Please enter enrollment number and student name."
            )
            return

        if enrollment in self.students:
            messagebox.showwarning(
                "Duplicate Student",
                "This enrollment number already exists."
            )
            return

        self.students[enrollment] = name
        self.save_data()

        messagebox.showinfo(
            "Success",
            "Student added successfully."
        )

    def get_marks(self):
        marks_text = self.marks_entry.get().strip()
        total_text = self.total_entry.get().strip()

        if not marks_text and not total_text:
            return None, None

        if not marks_text or not total_text:
            raise ValueError(
                "Enter both marks and total marks."
            )

        try:
            marks = float(marks_text)
            total = float(total_text)
        except ValueError:
            raise ValueError(
                "Marks must be valid numbers."
            )

        if total <= 0:
            raise ValueError("Total marks must be greater than zero.")

        if marks < 0 or marks > total:
            raise ValueError(
                "Marks must be between 0 and total marks."
            )

        return marks, total

    def add_submission(self):
        enrollment = self.enrollment_entry.get().strip()
        assignment = self.assignment_entry.get().strip()
        status = self.status_combo.get()
        remarks = self.remarks_entry.get().strip()

        if enrollment not in self.students:
            messagebox.showwarning(
                "Student Not Found",
                "Add the student first using Add Student."
            )
            return

        if not assignment:
            messagebox.showwarning(
                "Input Error",
                "Please enter an assignment name."
            )
            return

        try:
            marks, total = self.get_marks()
        except ValueError as error:
            messagebox.showerror("Invalid Marks", str(error))
            return

        if status == "Completed":
            if marks is None:
                messagebox.showwarning(
                    "Marks Required",
                    "Enter marks and total marks for a completed assignment."
                )
                return
        else:
            marks, total = None, None

        record = {
            "enrollment": enrollment,
            "name": self.students[enrollment],
            "assignment": assignment,
            "status": status,
            "marks": marks,
            "total": total,
            "remarks": remarks
        }

        self.submissions.append(record)
        self.save_data()
        self.refresh_table()

        messagebox.showinfo(
            "Success",
            "Submission added successfully."
        )

    def update_marks(self):
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Select a submission from the table first."
            )
            return

        try:
            marks, total = self.get_marks()
        except ValueError as error:
            messagebox.showerror("Invalid Marks", str(error))
            return

        if marks is None:
            messagebox.showwarning(
                "Marks Required",
                "Enter marks and total marks before updating."
            )
            return

        index = int(selected[0])
        record = self.submissions[index]

        record["marks"] = marks
        record["total"] = total
        record["status"] = "Completed"

        self.save_data()
        self.refresh_table()

        messagebox.showinfo(
            "Success",
            "Marks updated and status changed to Completed."
        )

    def delete_selected_submission(self):
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Select a submission from the table first."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this submission?"
        )

        if not confirm:
            return

        index = int(selected[0])
        del self.submissions[index]

        self.save_data()
        self.refresh_table()
        self.clear_form()

        messagebox.showinfo(
            "Deleted",
            "Submission deleted successfully."
        )

    def delete_selected_student(self):
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Select one of the student's submissions first."
            )
            return

        values = self.tree.item(selected[0], "values")
        enrollment = str(values[0])

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Delete this student and ALL their submissions?"
        )

        if not confirm:
            return

        self.students.pop(enrollment, None)

        self.submissions = [
            record for record in self.submissions
            if str(record["enrollment"]) != enrollment
        ]

        self.save_data()
        self.refresh_table()
        self.clear_form()

        messagebox.showinfo(
            "Deleted",
            "Student and all their submissions deleted successfully."
        )

    def select_record(self, event=None):
        selected = self.tree.selection()

        if not selected:
            return

        index = int(selected[0])
        record = self.submissions[index]

        self.enrollment_entry.delete(0, tk.END)
        self.enrollment_entry.insert(
            0, record["enrollment"]
        )

        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, record["name"])

        self.assignment_entry.delete(0, tk.END)
        self.assignment_entry.insert(
            0, record["assignment"]
        )

        self.status_combo.set(record["status"])

        self.marks_entry.delete(0, tk.END)
        if record.get("marks") is not None:
            self.marks_entry.insert(
                0, str(record["marks"])
            )

        self.total_entry.delete(0, tk.END)
        if record.get("total") is not None:
            self.total_entry.insert(
                0, str(record["total"])
            )

        self.remarks_entry.delete(0, tk.END)
        self.remarks_entry.insert(
            0, record.get("remarks", "")
        )

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        selected_filter = self.filter_combo.get()

        for index, record in enumerate(self.submissions):
            if (
                selected_filter != "All"
                and record["status"] != selected_filter
            ):
                continue

            marks = ""
            if record.get("marks") is not None:
                marks = str(record["marks"])

                if record.get("total") is not None:
                    marks += "/" + str(record["total"])

            self.tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    record["enrollment"],
                    record["name"],
                    record["assignment"],
                    record["status"],
                    marks,
                    record.get("remarks", "")
                )
            )

    def clear_form(self):
        self.enrollment_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.assignment_entry.delete(0, tk.END)
        self.marks_entry.delete(0, tk.END)
        self.total_entry.delete(0, tk.END)
        self.remarks_entry.delete(0, tk.END)

        self.status_combo.set("Pending")
        self.tree.selection_remove(self.tree.selection())

    def export_csv(self):
        if not self.submissions:
            messagebox.showwarning(
                "No Data",
                "There are no submissions to export."
            )
            return

        filename = filedialog.asksaveasfilename(
            title="Export Submissions",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")]
        )

        if not filename:
            return

        try:
            with open(
                filename, "w", newline="", encoding="utf-8-sig"
            ) as file:
                writer = csv.writer(file)

                writer.writerow([
                    "Enrollment",
                    "Name",
                    "Assignment",
                    "Status",
                    "Marks",
                    "Remarks"
                ])

                for record in self.submissions:
                    writer.writerow([
                        record["enrollment"],
                        record["name"],
                        record["assignment"],
                        record["status"],
                        (
                            record["marks"]
                            if record.get("marks") is not None
                            else ""
                        ),
                        record.get("remarks", "")
                    ])

            messagebox.showinfo(
                "Export Successful",
                "Submissions exported successfully."
            )

        except OSError as error:
            messagebox.showerror(
                "Export Error",
                f"Could not export CSV:\n{error}"
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = AssignmentTracker(root)
    root.mainloop()