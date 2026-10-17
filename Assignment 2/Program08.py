
MOD = 1000000007

def matrix_path_optimizer():
    n, m = map(int, input().split())

    dp_score = [None] * m
    dp_count = [0] * m

    for i in range(n):
        row = input().split()

        diagonal_score = None
        diagonal_count = 0

        for j in range(m):
            old_score = dp_score[j]
            old_count = dp_count[j]

            if row[j] == "X":
                dp_score[j] = None
                dp_count[j] = 0
            elif i == 0 and j == 0:
                dp_score[j] = int(row[j])
                dp_count[j] = 1
            else:
                candidates = []

                if j > 0 and dp_score[j - 1] is not None:
                    candidates.append(
                        (dp_score[j - 1], dp_count[j - 1])
                    )

                if old_score is not None:
                    candidates.append((old_score, old_count))

                if j > 0 and diagonal_score is not None:
                    candidates.append(
                        (diagonal_score, diagonal_count)
                    )

                if not candidates:
                    dp_score[j] = None
                    dp_count[j] = 0
                else:
                    best = max(score for score, count in candidates)
                    ways = sum(
                        count for score, count in candidates
                        if score == best
                    ) % MOD

                    dp_score[j] = best + int(row[j])
                    dp_count[j] = ways

            diagonal_score = old_score
            diagonal_count = old_count

    if dp_score[m - 1] is None:
        print("IMPOSSIBLE")
    else:
        print(dp_score[m - 1], dp_count[m - 1])


matrix_path_optimizer()
