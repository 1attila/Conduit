from typing import Union


class Range:
    """
    Advanced Range class
    """

    __min: float
    __max: float
    __equal_min: bool
    __equal_max: bool


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

        self.__equal_min = False
        self.__equal_max = False
        
        if _min.endswith("="):

            self.__equal_min = True
            _min = _min.replace("=", "")

        if _max.startswith("="):

            self.__equal_max = True
            _max = _max.replace("=", "")

        self.__min = float(_min)
        self.__max = float(_max)

        
    def __repr__(self) -> str:
        
        out = str(self.__min)

        if self.__equal_min:
            out += "="

        out += ".."

        if self.__equal_max:
            out += "="

        out += str(self.__max)
        
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


    def __compare_num(self, num: float) -> bool:

        if self.__equal_min:
            if self.__min > num:
                return False
        else:
            if self.__min >= num:
                return False

        if self.__equal_max:
            if self.__max < num:
                return False
        else:
            if self.__max <= num:
                return False

        return True
    

    def __compare_range(self, range: "Range") -> bool:

        if self.__min > range.min:
                return False
        
        if self.__max < range.max:    
                return False

        if self.left_included:
            
            if (not range.left_included and self.__min == range.min):
                    return False
            
        else:
            
            if (range.left_included and self.__min == range.min):
                    return False
        
        if self.rigth_included:
            
            if (not range.rigth_included and self.__max == range.max):    
                return False
            
        else:

            if (range.rigth_included and self.__max == range.max):
                return False

        return True


    @property
    def min(self) -> float:
        """Range left extreme"""

        return self.__min
    

    @property
    def max(self) -> float:
        """Range rigth extreme"""

        return self.__max


    @property
    def left_included(self) -> bool:
        """Returns True if the left extreme is included, False otherwise"""

        return self.__equal_min


    @property
    def rigth_included(self) -> bool:
        """Returns True if the rigth extreme is included, False otherwise"""

        return self.__equal_max

    
    def contains(self, number: Union["Range", float, int]) -> bool:
        """
        Checks if the given Range or number is contained by this range
        """

        if isinstance(number, (float, int)):
            return self.__compare_num(number)

        return self.__compare_range(number)