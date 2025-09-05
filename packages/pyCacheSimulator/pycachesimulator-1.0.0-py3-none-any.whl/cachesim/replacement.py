from abc import ABC, abstractmethod


class ReplacementPolicy(ABC):
    def __init__(self, num_lines: int):
        """Replacement policy for a set of *num_lines* lines"""
        self._nlines = num_lines

    @abstractmethod
    def __str__(self) -> str:
        """Returns the name of the ReplacementPolicy"""
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        """Reset policy to its initial state when cache is flushed (if needed)"""
        raise NotImplementedError

    @abstractmethod
    def onLineIndexReferenced(self, line_idx: int) -> None:
        """Called when a reference to the line at index *line_idx* (within set) was issued"""
        raise NotImplementedError

    @abstractmethod
    def getLineIndexToReplace(self) -> int:
        """Returns the index (within set) of the line that has to be replaced"""
        raise NotImplementedError


class LRU(ReplacementPolicy):
    def __init__(self, num_lines):
        super().__init__(num_lines)
        self.reset()

    def __str__(self) -> str:
        return "LRU"

    def reset(self):
        self._refs = [*range(self._nlines)]

    def onLineIndexReferenced(self, line_idx):
        """Move referenced line index to end of queue"""
        pos = self._refs.index(line_idx)
        i = self._refs.pop(pos)
        self._refs.append(i)

    def getLineIndexToReplace(self):
        """Least recently used is the head of the queue"""
        return self._refs[0]


class FIFO(ReplacementPolicy):
    def __init__(self, num_lines):
        super().__init__(num_lines)
        self.reset()

    def __str__(self) -> str:
        return "FIFO"

    def reset(self):
        self._i = 0

    def onLineIndexReferenced(self, line_idx):
        """References to lines do not affect FIFO policy"""
        pass

    def getLineIndexToReplace(self):
        """Advance index and cycle if end reached"""
        i = self._i
        self._i = (self._i + 1) % self._nlines

        return i
