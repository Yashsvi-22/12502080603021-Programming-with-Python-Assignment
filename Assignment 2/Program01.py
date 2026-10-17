
import re

def extract_emails(file_path):
    pattern = r'\b[A-Za-z0-9+._-]+@[A-Za-z0-9.-]+\.(?:com|edu|org)\b'

    domain_emails = {}

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                emails = re.findall(pattern, line)

                for email in emails:
                    domain = email.split("@")[1]

                    if domain not in domain_emails:
                        domain_emails[domain] = set()

                    domain_emails[domain].add(email)

        for domain in sorted(domain_emails):
            emails = domain_emails[domain]
            smallest_email = min(emails)

            print(domain, len(emails), smallest_email)

    except FileNotFoundError:
        print("Error: File not found.")
    except OSError:
        print("Error: Unable to read the file.")


file_path = input("Enter the text file path: ")
extract_emails(file_path)