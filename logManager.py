from os import path
import time

#? Made this really simple logger, for tracing errors. 

class LogManager:
    def __init__(self) -> None:
        #? Constructor
        if path.exists("events.log"):
            self.log = open("events.log", "a", encoding="utf-8")
        else:
            self.log = open("events.log", "w", encoding="utf-8")
            self.log.write(f"---------------Log file created at: {time.ctime()}\n\n")
    
        self.log.write(f"---------------Log init at: {time.ctime()}\n")
        self.callCounter = 0

    def __del__(self) -> None:
        #? Destructor
        if self.callCounter == 0:
            self.log.write("No errors in this session\n")
        self.log.write(f"---------------Log destruct at: {time.ctime()}\n")
        self.log.close()

    def logEvent(self, event: str) -> None:
        '''This function logs the event into the log file'''
        self._incremetnCallCounter()
        self.log.write(f"{event}\n")
        self.log.flush()
    
    def _incremetnCallCounter(self) -> None:
        '''This function increments the call counter'''
        self.callCounter += 1