from logging import Filter


class ConsoleOneTimeFilter(Filter):
    """
    ConsoleOneTimeFilter class filters log messages to only allow them to be logged once.
    :param logging.Filter: A class representing a log filter.
    :param name: A string indicating the name of the filter.
    :ivar logged_messages: A set to store logged messages.
    """
    def __init__(self, name="ConsoleWarnOneTime"):
        super().__init__(name)
        self.logged_messages = set()

    def filter(self, record):
        # We only log the message if it has not been logged before
        if record.msg not in self.logged_messages:
            self.logged_messages.add(record.msg)
            return True
        return False
