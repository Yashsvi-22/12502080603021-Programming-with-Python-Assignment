
class BankError(Exception):
    """Base exception for bank operations."""
    pass


class AccountNotFoundError(BankError):
    pass


class InsufficientFundsError(BankError):
    pass


class InvalidAmountError(BankError):
    pass


class Account:
    def __init__(self, account_id, balance):
        if balance < 0:
            raise InvalidAmountError("Initial balance cannot be negative")
        self.account_id = account_id
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    def deposit(self, amount):
        if amount <= 0:
            raise InvalidAmountError("Amount must be positive")
        self._balance += amount

    def withdraw(self, amount):
        if amount <= 0:
            raise InvalidAmountError("Amount must be positive")
        if amount > self._balance:
            raise InsufficientFundsError("Insufficient balance")
        self._balance -= amount


class Transaction:
    def __init__(self, operation, details):
        self.operation = operation
        self.details = details


class Bank:
    def __init__(self):
        self.accounts = {}
        self.history = []
        self.batch_number = 0
        self.failed_batches = []

    def add_account(self, account_id, balance):
        if account_id in self.accounts:
            raise BankError("Duplicate account")
        self.accounts[account_id] = Account(account_id, balance)

    def get_account(self, account_id):
        if account_id not in self.accounts:
            raise AccountNotFoundError("Account not found")
        return self.accounts[account_id]

    def execute(self, operation):
        parts = operation.split()
        if not parts:
            raise BankError("Empty operation")

        command = parts[0]

        if command == "DEPOSIT" and len(parts) == 3:
            account = self.get_account(parts[1])
            amount = int(parts[2])
            account.deposit(amount)
            details = (parts[1], amount)

        elif command == "WITHDRAW" and len(parts) == 3:
            account = self.get_account(parts[1])
            amount = int(parts[2])
            account.withdraw(amount)
            details = (parts[1], amount)

        elif command == "TRANSFER" and len(parts) == 4:
            source = self.get_account(parts[1])
            destination = self.get_account(parts[2])
            amount = int(parts[3])

            if amount <= 0:
                raise InvalidAmountError("Amount must be positive")
            if source.balance < amount:
                raise InsufficientFundsError("Insufficient balance")

            source.withdraw(amount)
            destination.deposit(amount)
            details = (parts[1], parts[2], amount)

        else:
            raise BankError("Invalid operation")

        self.history.append(Transaction(command, details))

    def process(self, operations):
        batch_active = False
        batch_snapshot = None
        batch_history_length = 0
        batch_failed = False

        for operation in operations:
            command = operation.strip()

            if command == "BATCH_BEGIN":
                if batch_active:
                    print("INVALID BATCH")
                    continue

                self.batch_number += 1
                batch_active = True
                batch_failed = False
                batch_snapshot = {
                    key: account.balance
                    for key, account in self.accounts.items()
                }
                batch_history_length = len(self.history)
                continue

            if command == "BATCH_END":
                if not batch_active:
                    print("INVALID BATCH")
                    continue

                if batch_failed:
                    for key, balance in batch_snapshot.items():
                        self.accounts[key]._balance = balance
                    del self.history[batch_history_length:]
                    self.failed_batches.append(self.batch_number)
                    print("FAILED", self.batch_number)

                batch_active = False
                batch_snapshot = None
                continue

            try:
                self.execute(command)
            except (BankError, ValueError) as error:
                if batch_active:
                    batch_failed = True
                else:
                    print("ERROR:", error)

        if batch_active:
            for key, balance in batch_snapshot.items():
                self.accounts[key]._balance = balance
            del self.history[batch_history_length:]
            self.failed_batches.append(self.batch_number)
            print("FAILED", self.batch_number)

    def print_balances(self):
        for account_id in sorted(self.accounts):
            print(account_id, self.accounts[account_id].balance)


def main():
    try:
        n = int(input().strip())
        if not 1 <= n <= 100000:
            print("INVALID")
            return

        bank = Bank()

        for _ in range(n):
            account_id, balance_text = input().split()
            balance = int(balance_text)
            bank.add_account(account_id, balance)

        q = int(input().strip())
        if not 1 <= q <= 300000:
            print("INVALID")
            return

        operations = [input().strip() for _ in range(q)]
        bank.process(operations)
        bank.print_balances()

    except (ValueError, EOFError, BankError):
        print("INVALID")


if __name__ == "__main__":
    main()