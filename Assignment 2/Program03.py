
import csv
import getpass
import mysql.connector
from mysql.connector import Error


BATCH_SIZE = 1000


def load_students(cursor, file_path):
    query = """
        INSERT INTO Student (student_id, name, spi)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            spi = VALUES(spi)
    """

    batch = []

    with open(file_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            student_id = int(row["student_id"])
            name = row["name"].strip()
            spi = float(row["spi"])

            if not name or not 0.0 <= spi <= 10.0:
                raise ValueError("Invalid student name or SPI.")

            batch.append((student_id, name, spi))

            if len(batch) >= BATCH_SIZE:
                cursor.executemany(query, batch)
                batch.clear()

        if batch:
            cursor.executemany(query, batch)


def load_registrations(cursor, file_path):
    query = """
        INSERT IGNORE INTO CourseRegistration
            (student_id, course_id)
        VALUES (%s, %s)
    """

    batch = []

    with open(file_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            student_id = int(row["student_id"])
            course_id = row["course_id"].strip()

            if not course_id:
                raise ValueError("Course ID cannot be empty.")

            batch.append((student_id, course_id))

            if len(batch) >= BATCH_SIZE:
                cursor.executemany(query, batch)
                batch.clear()

        if batch:
            cursor.executemany(query, batch)


def create_tables(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Student (
            student_id INT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            spi DECIMAL(4,2) NOT NULL
                CHECK (spi >= 0 AND spi <= 10)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CourseRegistration (
            student_id INT NOT NULL,
            course_id VARCHAR(20) NOT NULL,
            PRIMARY KEY (student_id, course_id),
            FOREIGN KEY (student_id)
                REFERENCES Student(student_id)
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_course_student
        ON CourseRegistration(course_id, student_id)
    """)


def main():
    connection = None
    cursor = None

    try:
        print("Enter your MySQL connection details.")
        host = input("Host (default localhost): ").strip() or "localhost"
        user = input("Username (default root): ").strip() or "root"
        password = getpass.getpass("MySQL password: ")
        database = input(
            "Database name (default student_analytics): "
        ).strip() or "student_analytics"

        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        cursor = connection.cursor()
        print("Connected to MySQL successfully.")

        create_tables(cursor)
        connection.commit()

        student_file = input("Enter student.csv path: ").strip()
        registration_file = input(
            "Enter registration.csv path: "
        ).strip()

        load_students(cursor, student_file)
        load_registrations(cursor, registration_file)
        connection.commit()

        course_id = input("Enter course ID: ").strip()
        threshold = float(input("Enter SPI threshold: "))

        if not 0.0 <= threshold <= 10.0:
            raise ValueError("SPI threshold must be between 0 and 10.")

        query = """
            SELECT s.student_id, s.name, s.spi, cr.course_id
            FROM Student AS s
            JOIN CourseRegistration AS cr
                ON s.student_id = cr.student_id
            WHERE cr.course_id = %s AND s.spi > %s
            ORDER BY s.spi DESC, s.student_id ASC
        """

        cursor.execute(query, (course_id, threshold))
        results = cursor.fetchall()

        if results:
            for student_id, name, spi, course in results:
                print(student_id, name, float(spi), course)
        else:
            print("No matching students found.")

    except Error as error:
        print("MySQL error:", error)

    except (OSError, ValueError, KeyError) as error:
        print("Input or file error:", error)

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()
            print("Database connection closed.")


if __name__ == "__main__":
    main()
