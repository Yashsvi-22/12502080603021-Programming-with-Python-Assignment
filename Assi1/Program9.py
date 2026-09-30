
import heapq


def schedule_jobs(worker_count, jobs):
    jobs.sort(key=lambda job: (job["arrival"], job["order"]))

    waiting_jobs = []
    running_jobs = []
    available_workers = list(range(1, worker_count + 1))
    heapq.heapify(available_workers)

    results = []
    current_time = 0
    next_job = 0
    total_waiting = 0

    while next_job < len(jobs) or waiting_jobs or running_jobs:

        if not waiting_jobs and not available_workers and running_jobs:
            current_time = max(current_time, running_jobs[0][0])
        while running_jobs and running_jobs[0][0] <= current_time:
            finish, worker_id, job = heapq.heappop(running_jobs)
            heapq.heappush(available_workers, worker_id)

        while (next_job < len(jobs)
               and jobs[next_job]["arrival"] <= current_time):
            job = jobs[next_job]
            heapq.heappush(
                waiting_jobs,
                (-job["priority"], job["order"], job)
            )
            next_job += 1

        while waiting_jobs and available_workers:
            _, _, job = heapq.heappop(waiting_jobs)
            worker_id = heapq.heappop(available_workers)

            start_time = current_time
            finish_time = start_time + job["duration"]
            waiting_time = start_time - job["arrival"]
            total_waiting += waiting_time

            results.append((
                job["order"],
                job["job_id"],
                worker_id,
                start_time,
                finish_time
            ))

            heapq.heappush(
                running_jobs,
                (finish_time, worker_id, job)
            )

        if next_job < len(jobs) or running_jobs:
            next_arrival = (
                jobs[next_job]["arrival"]
                if next_job < len(jobs)
                else float("inf")
            )
            next_finish = (
                running_jobs[0][0]
                if running_jobs
                else float("inf")
            )

            current_time = min(next_arrival, next_finish)

    results.sort(key=lambda result: result[0])

    for _, job_id, worker_id, start, finish in results:
        print(f"{job_id} W{worker_id} {start} {finish}")

    average_wait = total_waiting / len(jobs) if jobs else 0
    print(f"AVG_WAIT {average_wait:.2f}")


def main():
    try:
        worker_count, job_count = map(
            int, input("Enter workers and jobs: ").split()
        )

        if worker_count < 1 or worker_count > 64 or job_count < 1:
            print("Error: Invalid worker or job count.")
            return

        jobs = []

        for i in range(job_count):
            arrival, job_id, priority, duration, resources = (
                input().split()
            )

            arrival = int(arrival)
            priority = int(priority)
            duration = int(duration)
            resources = int(resources)

            if arrival < 0 or duration < 1 or resources < 1:
                print("Error: Invalid job details.")
                return

            jobs.append({
                "arrival": arrival,
                "job_id": job_id,
                "priority": priority,
                "duration": duration,
                "resources": resources,
                "order": i
            })

        schedule_jobs(worker_count, jobs)

    except ValueError:
        print("Error: Please enter valid input.")


if __name__ == "__main__":
    main()