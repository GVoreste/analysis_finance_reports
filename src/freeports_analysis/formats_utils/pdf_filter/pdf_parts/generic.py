"""Utilities for handling generic PDF parts and components."""


class Range:
    """A class representing a range with start and end values.

    Attributes
    ----------
    start : float
        The starting value of the range.
    end : float
        The ending value of the range.
    size : float
        The size of the range (end - start).
    """

    def __init__(self, start: float, end: float):
        """Initialize the Range with start and end values.

        Parameters
        ----------
        start : float
            The starting value of the range.
        end : float
            The ending value of the range.
        """
        self._start = start
        self._end = end

    @property
    def start(self) -> float:
        """Get the start value of the range.
        Returns
        -------
        float
            The start value of the range.
        """
        return self._start

    @property
    def end(self) -> float:
        """Get the end value of the range.

        Returns
        -------
        float
            The end value of the range.
        """
        return self._end

    @property
    def size(self) -> float:
        """Calculate the size of the range (end - start).

        Returns
        -------
        float
            The size of the range.
        """
        return self.end - self.start

    def __contains__(self, value: float) -> bool:
        """Check if a value is within the range.

        Parameters
        ----------
        value : float
            The value to check.

        Returns
        -------
        bool
            True if the value is within the range, False otherwise.
        """
        return (self.start is None or self.start <= value) and (
            self.end is None or value <= self.end
        )

    def __str__(self) -> str:
        """Return a string representation of the range.

        Returns
        -------
        str
            The string representation of the range in the format [start,end].
        """
        return f"[{self.start},{self.end}]"

    def __iter__(self):
        yield self.start
        yield self.end
