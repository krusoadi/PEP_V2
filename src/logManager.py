from os import path
import time


# Made this really simple logger, for tracing errors.

class LogManager:
    def __init__(self) -> None:
        # Constructor
        script_dir = path.dirname(path.relpath(__file__))
        log_path = path.join(script_dir, '..', 'log', 'events.log')

        if path.exists(log_path):
            self.log = open(log_path, "a", encoding="utf-8")
        else:
            self.log = open(log_path, "w", encoding="utf-8")
            self.log.write(f"---------------Log file created at: {time.ctime()}\n\n")

        self.log.write(f"---------------Log init at: {time.ctime()}\n")
        self.callCounter = 0

    def __del__(self) -> None:
        # Destructor
        if self.callCounter == 0:
            self.log.write("No errors in this session\n")
        self.log.write(f"---------------Log destruct at: {time.ctime()}\n")
        self.log.close()

    def log_event(self, event: str) -> None:
        """This function logs the event into the log file"""
        self._increment_call_counter()
        self.log.write(f"{event}\n")
        self.log.flush()

    def _increment_call_counter(self) -> None:
        """This function increments the call counter"""
        self.callCounter += 1
