class Counter:
    def __init__(self):
        self.success = 0
        self.error = 0
        self.processed = 0
        self.total = 0

    def __str__(self):
        return f"total: {self.total}, processed: {self.processed}, error: {self.error}, success: {self.success}"

    def set_total(self, total):
        self.total = total

    def mark_succeed(self):
        self.success += 1

    def mark_error(self):
        self.error += 1

    def mark_processed(self):
        self.processed += 1


class BaseMigration:
    def migrate(self):
        pass

    def rollback(self):
        pass
