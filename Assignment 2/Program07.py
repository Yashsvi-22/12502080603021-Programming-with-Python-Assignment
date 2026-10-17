
import json
import math
from collections import defaultdict


def read_records(file_path):
    """Read and validate sensor records one line at a time."""
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            device_id = None

            try:
                record = json.loads(line)

                if isinstance(record, dict):
                    device_id = record.get("device_id")

                if not isinstance(record, dict):
                    yield None, None
                    continue

                required_fields = [
                    "device_id", "timestamp",
                    "temperature_c", "humidity"
                ]

                if any(field not in record for field in required_fields):
                    yield device_id, None
                    continue

                temperature = record["temperature_c"]
                humidity = record["humidity"]

                if (
                    isinstance(temperature, bool)
                    or not isinstance(temperature, (int, float))
                    or not math.isfinite(temperature)
                    or isinstance(humidity, bool)
                    or not isinstance(humidity, (int, float))
                    or not math.isfinite(humidity)
                ):
                    yield device_id, None
                    continue

                if (
                    not isinstance(device_id, str)
                    or not device_id.strip()
                    or not isinstance(record["timestamp"], str)
                    or not record["timestamp"].strip()
                    or not 0 <= humidity <= 100
                ):
                    yield device_id, None
                    continue

                yield device_id, float(temperature)

            except (json.JSONDecodeError, TypeError, ValueError):
                yield device_id, None


def process_file(file_path):
    """Calculate summary statistics without loading the whole file."""
    stats = defaultdict(
        lambda: {
            "count": 0,
            "min": None,
            "max": None,
            "total": 0.0,
            "corrupted": 0
        }
    )

    unassigned_corrupted = 0

    for device_id, temperature in read_records(file_path):
        if not isinstance(device_id, str) or not device_id.strip():
            if temperature is None:
                unassigned_corrupted += 1
            continue

        device_id = device_id.strip()
        device = stats[device_id]

        if temperature is None:
            device["corrupted"] += 1
            continue

        device["count"] += 1
        device["total"] += temperature

        if device["min"] is None or temperature < device["min"]:
            device["min"] = temperature

        if device["max"] is None or temperature > device["max"]:
            device["max"] = temperature

    for device_id in sorted(stats):
        device = stats[device_id]

        if device["count"] == 0:
            print(
                f"{device_id} count=0 min=N/A max=N/A "
                f"avg=N/A corrupted={device['corrupted']}"
            )
        else:
            average = device["total"] / device["count"]

            print(
                f"{device_id} count={device['count']} "
                f"min={device['min']:g} "
                f"max={device['max']:g} "
                f"avg={average:.2f} "
                f"corrupted={device['corrupted']}"
            )

    if unassigned_corrupted:
        print(
            f"Corrupted records with unknown device ID: "
            f"{unassigned_corrupted}"
        )


def main():
    file_path = input("Enter JSONL file path: ").strip()

    if not file_path:
        print("File path cannot be empty.")
        return

    try:
        process_file(file_path)
    except OSError as error:
        print("File error:", error)


if __name__ == "__main__":
    main()
