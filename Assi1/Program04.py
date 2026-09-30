
import csv
import os
from datetime import datetime
from collections import defaultdict


def validate_transaction(row):
    """Validate one transaction and return an error reason if invalid."""
    required = ["tid", "acc", "type", "amount", "time"]

    for field in required:
        if field not in row or not row[field].strip():
            return "Missing " + field

    if row["type"].strip() not in ("CREDIT", "DEBIT"):
        return "Invalid transaction type"

    try:
        amount = float(row["amount"])
        if amount <= 0:
            return "Amount must be greater than zero"
    except ValueError:
        return "Amount is not numeric"

    try:
        datetime.strptime(row["time"], "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return "Invalid timestamp"

    return None


def process_transactions(file_path):
    balances = defaultdict(float)
    output_fields = ["tid", "acc", "type", "amount", "time"]

    with open("credit.csv", "w", newline="", encoding="utf-8") as credit_file, \
         open("debit.csv", "w", newline="", encoding="utf-8") as debit_file, \
         open("error.csv", "w", newline="", encoding="utf-8") as error_file:

        credit_writer = csv.DictWriter(
            credit_file, fieldnames=output_fields
        )
        debit_writer = csv.DictWriter(
            debit_file, fieldnames=output_fields
        )
        error_writer = csv.writer(error_file)

        credit_writer.writeheader()
        debit_writer.writeheader()
        error_writer.writerow(output_fields + ["reason"])

        try:
            with open(file_path, "r", newline="", encoding="utf-8-sig") as input_file:
                reader = csv.DictReader(input_file)

                if reader.fieldnames != output_fields:
                    print("Invalid CSV header.")
                    return

                for row in reader:
                    try:
                        reason = validate_transaction(row)

                        if reason:
                            error_writer.writerow(
                                [row.get(field, "") for field in output_fields]
                                + [reason]
                            )
                            continue

                        transaction_type = row["type"].strip()
                        account = row["acc"].strip()
                        amount = float(row["amount"])

                        if transaction_type == "CREDIT":
                            credit_writer.writerow(row)
                            balances[account] += amount
                        else:
                            debit_writer.writerow(row)
                            balances[account] -= amount

                    except (ValueError, TypeError, KeyError) as error:
                        error_writer.writerow(
                            [row.get(field, "") for field in output_fields]
                            + ["Processing error: " + str(error)]
                        )

        except FileNotFoundError:
            print("Input CSV file not found.")
            return
        except PermissionError:
            print("Permission denied while opening a file.")
            return
        except OSError as error:
            print("File error:", error)
            return

    for account, balance in sorted(
        balances.items(), key=lambda item: (-abs(item[1]), item[0])
    ):
        print(account, f"{balance:g}")


if __name__ == "__main__":
    process_transactions("transactions.csv")
