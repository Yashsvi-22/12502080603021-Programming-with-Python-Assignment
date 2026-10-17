
import re
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error


DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3307,
    "user": "root",
    "password": "",
    "database": "contact_manager"
}


EMAIL_PATTERN = r"^[A-Za-z0-9._+-]+@[A-Za-z0-9.-]+\.(com|edu|org)$"


class ContactManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Contact Manager")
        self.root.geometry("950x650")

        self.connection = None
        self.selected_id = None
        self.contact_ids = []

        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.category_var = tk.StringVar(value="Personal")
        self.search_var = tk.StringVar()
        self.search_type = tk.StringVar(value="name")

        self.connect_database()
        self.create_menu()
        self.create_widgets()
        self.load_contacts()

        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

    def connect_database(self):
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            cursor = self.connection.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Contact (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(150) NOT NULL UNIQUE,
                    phone VARCHAR(20),
                    category VARCHAR(50),
                    notes TEXT,
                    INDEX idx_name (name),
                    INDEX idx_phone (phone)
                )
            """)

            self.connection.commit()
            cursor.close()

        except Error as error:
            messagebox.showerror(
                "Database Error",
                f"Could not connect to MySQL.\n{error}"
            )
            self.root.destroy()

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Clear Fields", command=self.clear_fields)
        file_menu.add_command(label="Refresh", command=self.load_contacts)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.close_app)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menu_bar)

    def create_widgets(self):
        form = ttk.LabelFrame(self.root, text="Contact Details", padding=12)
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Name:").grid(row=0, column=0, sticky="w")
        ttk.Entry(
            form, textvariable=self.name_var, width=35
        ).grid(row=0, column=1, padx=8, pady=5)

        ttk.Label(form, text="Email:").grid(row=1, column=0, sticky="w")
        ttk.Entry(
            form, textvariable=self.email_var, width=35
        ).grid(row=1, column=1, padx=8, pady=5)

        ttk.Label(form, text="Phone:").grid(row=2, column=0, sticky="w")
        ttk.Entry(
            form, textvariable=self.phone_var, width=35
        ).grid(row=2, column=1, padx=8, pady=5)

        ttk.Label(form, text="Category:").grid(row=3, column=0, sticky="w")
        ttk.Combobox(
            form,
            textvariable=self.category_var,
            values=["Personal", "Family", "Friend", "Faculty", "Work"],
            state="readonly",
            width=32
        ).grid(row=3, column=1, padx=8, pady=5)

        ttk.Label(form, text="Notes:").grid(row=4, column=0, sticky="nw")
        self.notes_text = tk.Text(form, width=35, height=3)
        self.notes_text.grid(row=4, column=1, padx=8, pady=5)

        buttons = ttk.Frame(form)
        buttons.grid(row=5, column=0, columnspan=2, pady=8)

        ttk.Button(
            buttons, text="Add", command=self.add_contact
        ).pack(side="left", padx=4)

        ttk.Button(
            buttons, text="Update", command=self.update_contact
        ).pack(side="left", padx=4)

        ttk.Button(
            buttons, text="Delete", command=self.delete_contact
        ).pack(side="left", padx=4)

        ttk.Button(
            buttons, text="Clear", command=self.clear_fields
        ).pack(side="left", padx=4)

        search_frame = ttk.LabelFrame(
            self.root, text="Search Contacts", padding=10
        )
        search_frame.pack(fill="x", padx=10, pady=5)

        ttk.Entry(
            search_frame, textvariable=self.search_var, width=30
        ).pack(side="left", padx=5)

        for label, value in [
            ("Name", "name"),
            ("Email", "email"),
            ("Phone", "phone")
        ]:
            ttk.Radiobutton(
                search_frame,
                text=label,
                variable=self.search_type,
                value=value
            ).pack(side="left", padx=5)

        ttk.Button(
            search_frame, text="Search", command=self.search_contacts
        ).pack(side="left", padx=5)

        ttk.Button(
            search_frame, text="Show All", command=self.load_contacts
        ).pack(side="left", padx=5)

        list_frame = ttk.LabelFrame(
            self.root, text="Contacts (select one to edit)", padding=10
        )
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.contact_list = tk.Listbox(
            list_frame,
            font=("Consolas", 10),
            yscrollcommand=scrollbar.set
        )
        self.contact_list.pack(fill="both", expand=True)
        scrollbar.config(command=self.contact_list.yview)

        self.contact_list.bind(
            "<<ListboxSelect>>", self.select_contact
        )

    def validate_form(self):
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()
        phone = self.phone_var.get().strip()

        if not name or not email:
            messagebox.showwarning(
                "Validation", "Name and email are required."
            )
            return False

        if not re.fullmatch(EMAIL_PATTERN, email, re.IGNORECASE):
            messagebox.showwarning(
                "Invalid Email",
                "Enter a valid email ending in .com, .edu or .org."
            )
            return False

        if phone and not phone.isdigit():
            messagebox.showwarning(
                "Invalid Phone", "Phone must contain digits only."
            )
            return False

        return True

    def get_form_data(self):
        return (
            self.name_var.get().strip(),
            self.email_var.get().strip(),
            self.phone_var.get().strip(),
            self.category_var.get(),
            self.notes_text.get("1.0", "end-1c").strip()
        )

    def add_contact(self):
        if not self.validate_form():
            return

        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO Contact
                    (name, email, phone, category, notes)
                VALUES (%s, %s, %s, %s, %s)
            """, self.get_form_data())

            self.connection.commit()
            messagebox.showinfo("Success", "Contact added successfully.")
            self.clear_fields()
            self.load_contacts()

        except Error as error:
            self.connection.rollback()
            if error.errno == 1062:
                messagebox.showerror(
                    "Duplicate Email", "This email already exists."
                )
            else:
                messagebox.showerror("Database Error", str(error))
        finally:
            if cursor:
                cursor.close()

    def update_contact(self):
        if self.selected_id is None:
            messagebox.showwarning(
                "Select Contact", "Select a contact from the list first."
            )
            return

        if not self.validate_form():
            return

        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE Contact
                SET name=%s, email=%s, phone=%s, category=%s, notes=%s
                WHERE id=%s
            """, self.get_form_data() + (self.selected_id,))

            self.connection.commit()
            messagebox.showinfo("Success", "Contact updated.")
            self.clear_fields()
            self.load_contacts()

        except Error as error:
            self.connection.rollback()
            if error.errno == 1062:
                messagebox.showerror(
                    "Duplicate Email", "Another contact uses this email."
                )
            else:
                messagebox.showerror("Database Error", str(error))
        finally:
            if cursor:
                cursor.close()

    def delete_contact(self):
        if self.selected_id is None:
            messagebox.showwarning(
                "Select Contact", "Select a contact to delete."
            )
            return

        if not messagebox.askyesno(
            "Confirm Delete", "Delete the selected contact?"
        ):
            return

        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "DELETE FROM Contact WHERE id=%s",
                (self.selected_id,)
            )
            self.connection.commit()
            messagebox.showinfo("Success", "Contact deleted.")
            self.clear_fields()
            self.load_contacts()

        except Error as error:
            self.connection.rollback()
            messagebox.showerror("Database Error", str(error))
        finally:
            if cursor:
                cursor.close()

    def display_contacts(self, query, parameters=()):
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, parameters)
            rows = cursor.fetchall()

            self.contact_list.delete(0, tk.END)
            self.contact_ids = []

            for contact_id, name, email, phone, category in rows:
                self.contact_ids.append(contact_id)
                line = (
                    f"{contact_id} | {name} | {email} | "
                    f"{phone or '-'} | {category or '-'}"
                )
                self.contact_list.insert(tk.END, line)

        except Error as error:
            messagebox.showerror("Database Error", str(error))
        finally:
            if cursor:
                cursor.close()

    def load_contacts(self):
        if self.connection and self.connection.is_connected():
            self.display_contacts("""
                SELECT id, name, email, phone, category
                FROM Contact
                ORDER BY name ASC, id ASC
            """)

    def search_contacts(self):
        keyword = self.search_var.get().strip()
        field = self.search_type.get()

        allowed_fields = {
            "name": "name",
            "email": "email",
            "phone": "phone"
        }
        column = allowed_fields[field]

        self.display_contacts(
            f"""
                SELECT id, name, email, phone, category
                FROM Contact
                WHERE {column} LIKE %s
                ORDER BY name ASC, id ASC
            """,
            (f"%{keyword}%",)
        )

    def select_contact(self, event=None):
        selection = self.contact_list.curselection()
        if not selection:
            return

        index = selection[0]
        self.selected_id = self.contact_ids[index]

        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT name, email, phone, category, notes
                FROM Contact WHERE id=%s
            """, (self.selected_id,))

            row = cursor.fetchone()
            if row:
                self.name_var.set(row[0])
                self.email_var.set(row[1])
                self.phone_var.set(row[2] or "")
                self.category_var.set(row[3] or "Personal")
                self.notes_text.delete("1.0", tk.END)
                self.notes_text.insert("1.0", row[4] or "")

        except Error as error:
            messagebox.showerror("Database Error", str(error))
        finally:
            if cursor:
                cursor.close()

    def clear_fields(self):
        self.selected_id = None
        self.name_var.set("")
        self.email_var.set("")
        self.phone_var.set("")
        self.category_var.set("Personal")
        self.notes_text.delete("1.0", tk.END)
        self.contact_list.selection_clear(0, tk.END)

    def close_app(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ContactManager(root)
    root.mainloop()
