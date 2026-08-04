from typing import Union


class Range:
    """
    Advanced Range class
    """

    _min: float
    _max: float
    _equal_min: bool
    _equal_max: bool


    def __init__(self, range: str) -> None:

        if not range.__contains__(".."):
            raise ValueError("Wrong Range syntax")
        
        extremes = range.split("..")
        
        if not len(extremes) == 2:
            raise ValueError("Wrong Range syntaxt")
        
        _min = extremes[0].strip()
        _max = extremes[1].strip()

        if _min == "":
            _min = "-inf"
        if _max == "":
            _max = "inf"

        self._equal_min = False
        self._equal_max = False
        
        if _min.endswith("="):

            self._equal_min = True
            _min = _min.replace("=", "")

        if _max.startswith("="):

            self._equal_max = True
            _max = _max.replace("=", "")

        self._min = float(_min)
        self._max = float(_max)

        
    def __repr__(self) -> str:
        
        out = str(self._min)

        if self._equal_min:
            out += "="

        out += ".."

        if self._equal_max:
            out += "="

        out += str(self._max)
        
        return out

    
    def __eq__(self, other: object) -> bool:

        if not isinstance(other, Range):
            return False

        return (
            self.min == other.min and
            self.left_included == other.left_included and
            self.max == other.max and
            self.rigth_included == other.rigth_included
        )


    def _compare_num(self, num: float) -> bool:

        if self._equal_min:
            if self._min > num:
                return False
        else:
            if self._min >= num:
                return False

        if self._equal_max:
            if self._max < num:
                return False
        else:
            if self._max <= num:
                return False

        return True
    

    def _compare_range(self, range: "Range") -> bool:

        if self._min > range.min:
                return False
        
        if self._max < range.max:    
                return False

        if self.left_included:
            
            if (not range.left_included and self._min == range.min):
                return False
            
        else:
            
            if (range.left_included and self._min == range.min):
                return False
        
        if self.rigth_included:
            
            if (not range.rigth_included and self._max == range.max):    
                return False
            
        else:

            if (range.rigth_included and self._max == range.max):
                return False

        return True


    @property
    def min(self) -> float:
        """Range left extreme"""

        return self._min
    

    @property
    def max(self) -> float:
        """Range rigth extreme"""

        return self._max


    @property
    def left_included(self) -> bool:
        """Returns True if the left extreme is included, False otherwise"""

        return self._equal_min


    @property
    def rigth_included(self) -> bool:
        """Returns True if the rigth extreme is included, False otherwise"""

        return self._equal_max

    
    def contains(self, number: Union["Range", float, int]) -> bool:
        """
        Checks if the given Range or number is contained by this range
        """

        if isinstance(number, (float, int)):
            return self._compare_num(number)

        return self._compare_range(number)