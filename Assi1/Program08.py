
import os
import re
import sys
import pickle
import zipfile
from collections import defaultdict


def normalize_tokens(text):
    """Convert text into lowercase words."""
    return re.findall(r"\b[a-zA-Z0-9_]+\b", text.lower())


def build_index(folder_path, zip_name):
    if not os.path.isdir(folder_path):
        print("Error: Folder does not exist.")
        return

    index = defaultdict(list)
    total_files = 0
    total_lines = 0
    log_files = []

    for filename in sorted(os.listdir(folder_path)):
        file_path = os.path.join(folder_path, filename)

        if not os.path.isfile(file_path):
            continue

        try:
            with open(file_path, "r", encoding="utf-8",
                      errors="replace") as file:
                total_files += 1
                log_files.append(file_path)

                for line_number, line in enumerate(file, start=1):
                    total_lines += 1
                    tokens = set(normalize_tokens(line))

                    for token in tokens:
                        index[token].append((filename, line_number))

        except OSError as error:
            print(f"Error reading {filename}: {error}")
            return

    index = dict(index)

    zip_path = os.path.abspath(zip_name)
    pickle_path = os.path.splitext(zip_path)[0] + ".pkl"

    try:
        with open(pickle_path, "wb") as file:
            pickle.dump(index, file)

        with zipfile.ZipFile(zip_path, "w",
                             zipfile.ZIP_DEFLATED) as archive:
            for file_path in log_files:
                archive.write(
                    file_path,
                    arcname=os.path.basename(file_path)
                )

            archive.write(pickle_path,
                          arcname=os.path.basename(pickle_path))

    except OSError as error:
        print(f"Error creating output files: {error}")
        return

    print(f"FILES {total_files}")
    print(f"LINES {total_lines}")
    print(f"TOKENS {len(index)}")


def search_index(pickle_path, query_tokens):
    if not os.path.isfile(pickle_path):
        print("Error: Pickle index file does not exist.")
        return

    try:
        with open(pickle_path, "rb") as file:
            index = pickle.load(file)
    except (OSError, pickle.UnpicklingError) as error:
        print(f"Error loading index: {error}")
        return

    for query in query_tokens:
        tokens = normalize_tokens(query)

        if not tokens:
            print(f"{query}: No matches")
            continue

        for token in tokens:
            matches = index.get(token, [])

            print(f"{token}:")

            if matches:
                for filename, line_number in matches:
                    print(f"{filename}:{line_number}")
            else:
                print("No matches")


def main():
    try:
        mode = input("Enter mode (BUILD/SEARCH): ").strip().upper()

        if mode == "BUILD":
            folder_path = input("Enter log folder path: ").strip()
            zip_name = input("Enter output ZIP name: ").strip()

            if not zip_name.lower().endswith(".zip"):
                zip_name += ".zip"

            build_index(folder_path, zip_name)

        elif mode == "SEARCH":
            pickle_path = input("Enter pickle file path: ").strip()
            q = int(input("Enter number of search tokens: "))

            if q < 0:
                print("Error: Number of tokens cannot be negative.")
                return

            queries = [
                input("Enter search token: ").strip()
                for _ in range(q)
            ]

            search_index(pickle_path, queries)

        else:
            print("Error: Mode must be BUILD or SEARCH.")

    except ValueError:
        print("Error: Please enter a valid number.")


if __name__ == "__main__":
    main()
