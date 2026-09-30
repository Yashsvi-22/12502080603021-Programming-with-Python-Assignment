
from collections import deque
import string


def build_banned_trie(banned_words):
    trie = [{}]
    failure = [0]
    terminal = [False]

    for word in banned_words:
        node = 0

        for char in word.lower():
            if char not in trie[node]:
                trie[node][char] = len(trie)
                trie.append({})
                failure.append(0)
                terminal.append(False)

            node = trie[node][char]

        terminal[node] = True

    queue = deque()

    for child in trie[0].values():
        queue.append(child)

    while queue:
        node = queue.popleft()

        for char, child in trie[node].items():
            queue.append(child)
            fallback = failure[node]

            while fallback and char not in trie[fallback]:
                fallback = failure[fallback]

            failure[child] = trie[fallback].get(char, 0)
            terminal[child] = (
                terminal[child] or terminal[failure[child]]
            )

    return trie, failure, terminal


def contains_banned_word(password, trie, failure, terminal):
    node = 0

    for char in password.lower():
        while node and char not in trie[node]:
            node = failure[node]

        node = trie[node].get(char, 0)

        if terminal[node]:
            return True

    return False


def classify_password(password, trie, failure, terminal):
    if contains_banned_word(password, trie, failure, terminal):
        return "COMPROMISED"

    if not 6 <= len(password) <= 12:
        return "WEAK_LENGTH"

    for i in range(len(password) - 3):
        if password[i] == password[i + 1] == password[i + 2] == password[i + 3]:
            return "WEAK_PATTERN"

    has_lower = any(char.islower() for char in password)
    has_upper = any(char.isupper() for char in password)
    has_digit = any(char.isdigit() for char in password)
    has_special = any(char in "$#@" for char in password)

    if has_lower and has_upper and has_digit and has_special:
        return "STRONG"

    return "WEAK_PATTERN"


def main():
    b = int(input())
    banned_words = []

    for _ in range(b):
        banned_words.append(input().strip())

    trie, failure, terminal = build_banned_trie(banned_words)

    n = int(input())

    for index in range(1, n + 1):
        password = input().strip()
        result = classify_password(
            password, trie, failure, terminal
        )
        print(f"{index}: {result}")


if __name__ == "__main__":
    main()