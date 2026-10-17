
import json
import mysql.connector
from mysql.connector import Error


COLUMNS = {
    "student.id": "s.student_id",
    "student.name": "s.name",
    "student.spi": "s.spi",
    "course.id": "c.course_id",
    "course.name": "c.name",
}

OPERATORS = {"=", "!=", ">", ">=", "<", "<=", "LIKE", "BETWEEN"}


def build_query(request):
    columns = request.get("columns", [])
    filters = request.get("where", [])
    order = request.get("order", {})
    limit = request.get("limit", 10)

    if not isinstance(columns, list) or not columns:
        raise ValueError("Select at least one column.")

    if not all(isinstance(col, str) and col in COLUMNS for col in columns):
        raise ValueError("Invalid selected column.")

    if not isinstance(filters, list):
        raise ValueError("Filters must be a list.")

    if not isinstance(limit, int) or isinstance(limit, bool):
        raise ValueError("LIMIT must be an integer.")

    if not 1 <= limit <= 1000:
        raise ValueError("LIMIT must be between 1 and 1000.")

    selected_columns = ", ".join(COLUMNS[col] for col in columns)

    sql = f"""
        SELECT {selected_columns}
        FROM Student AS s
        JOIN CourseRegistration AS cr
            ON s.student_id = cr.student_id
        JOIN Course AS c
            ON cr.course_id = c.course_id
    """

    conditions = []
    parameters = []

    for item in filters:
        if not isinstance(item, dict):
            raise ValueError("Each filter must be an object.")

        field = item.get("field")
        operator = item.get("op")
        value = item.get("value")

        if field not in COLUMNS:
            raise ValueError("Invalid filter column.")

        if operator not in OPERATORS:
            raise ValueError("Invalid filter operator.")

        column = COLUMNS[field]

        if operator == "BETWEEN":
            if not isinstance(value, list) or len(value) != 2:
                raise ValueError("BETWEEN requires two values.")

            conditions.append(f"{column} BETWEEN %s AND %s")
            parameters.extend(value)

        else:
            conditions.append(f"{column} {operator} %s")
            parameters.append(value)

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    if order:
        if not isinstance(order, dict):
            raise ValueError("Order must be an object.")

        order_column = order.get("field")
        direction = order.get("direction", "ASC").upper()

        if order_column not in COLUMNS:
            raise ValueError("Invalid sort column.")

        if direction not in {"ASC", "DESC"}:
            raise ValueError("Sort direction must be ASC or DESC.")

        sql += f" ORDER BY {COLUMNS[order_column]} {direction}"

    sql += " LIMIT %s"
    parameters.append(limit)

    return sql, parameters


def main():
    connection = None
    cursor = None

    try:
        host = input("MySQL host [localhost]: ").strip() or "localhost"
        user = input("MySQL username [root]: ").strip() or "root"
        password = input("MySQL password: ")
        database = input("Database name: ").strip()

        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        print("\nEnter the query request as one JSON object.")
        print('Example: {"columns":["student.name","course.name"],')
        print(' "where":[{"field":"course.id","op":"=","value":"PY101"}],')
        print(' "order":{"field":"student.spi","direction":"DESC"},')
        print(' "limit":2}')

        request = json.loads(input("\nJSON: "))

        sql, parameters = build_query(request)

        print("\nSQL_OK")
        print("SQL template:")
        print(sql)
        print("Parameters:", parameters)

        cursor = connection.cursor()
        cursor.execute(sql, parameters)
        rows = cursor.fetchall()

        print("\nQuery results:")
        if not rows:
            print("No matching records.")
        else:
            for row in rows:
                print(*row)

    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
        print("Invalid request:", error)

    except Error as error:
        print("MySQL error:", error)

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    main()
