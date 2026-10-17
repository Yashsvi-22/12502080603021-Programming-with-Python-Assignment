
import re
from collections import defaultdict, deque
from datetime import datetime


LOG_PATTERN = re.compile(
    r"^(\d{2}:\d{2})\s+(\S+)\s+(\S+)\s+(FAIL|SUCCESS)$"
)


def time_to_minutes(timestamp):
    hours, minutes = map(int, timestamp.split(":"))
    return hours * 60 + minutes


def detect_suspicious_users(x, window_minutes, logs):
    failures = defaultdict(deque)

    suspicious = {}

    for line in logs:
        line = line.strip()
        match = LOG_PATTERN.fullmatch(line)

        if not match:
            continue

        timestamp, user, ip, status = match.groups()
        current_time = time_to_minutes(timestamp)

        user_failures = failures[user]

        while (
            user_failures
            and current_time - user_failures[0][0] > window_minutes
        ):
            user_failures.popleft()

        if status == "FAIL":
            user_failures.append((current_time, ip))

        elif status == "SUCCESS" and user not in suspicious:
            different_ip_failures = sum(
                1 for failure_time, failure_ip in user_failures
                if failure_ip != ip
                and current_time - failure_time <= window_minutes
            )

            if different_ip_failures >= x:
                suspicious[user] = timestamp

    return suspicious


def main():
    try:
        x, t = map(int, input().split())
        n = int(input())

        if not 1 <= x <= 100:
            print("X must be between 1 and 100.")
            return

        if not 1 <= t <= 1440:
            print("T must be between 1 and 1440.")
            return

        if n < 0:
            print("Number of logs cannot be negative.")
            return

        logs = []
        for _ in range(n):
            logs.append(input())

        suspicious = detect_suspicious_users(x, t, logs)

        for user in sorted(suspicious):
            print(user, suspicious[user])

    except ValueError:
        print("Invalid input format.")


if __name__ == "__main__":
    main()
