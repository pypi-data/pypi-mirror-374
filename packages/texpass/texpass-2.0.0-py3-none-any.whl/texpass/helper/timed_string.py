from time import time_ns


class TimeString:
    """
    Object that returns characters sent within a time chunk as a concatenated string

    Note that this does not return a string at the end of a time chunk, 
    but everytime a character is sent
    """
    def __init__(self, timeout_ns: int):
        self._final_str: str = ""
        self._start: int = time_ns()
        self._timed_out = True

        self._timeout = timeout_ns
    
    def __is_timeout(self) -> bool:
        return (time_ns() - self._start) > self._timeout
    
    def __refresh(self) -> None:
        self._start = time_ns()
        self._timed_out = False
        self._final_str = ""

    def send(self, char: str) -> str:
        """
        Send a character. Returns all characters since the start of time chunk
        """
        # checks if it has been 400+ ms since last send()
        if not self._timed_out:
            if self.__is_timeout():
                self._timed_out = True
            
        # if timed out, start fresh
        if self._timed_out:
            self.__refresh()

        # concatenate string-digits
        self._final_str += char
        
        return self._final_str
