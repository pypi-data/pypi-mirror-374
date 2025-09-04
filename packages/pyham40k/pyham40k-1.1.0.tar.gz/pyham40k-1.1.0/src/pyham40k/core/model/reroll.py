from enum import Enum

from pyham40k.core.model.format_exception import Format_Exception


class Reroll(Enum):
    NO = 0
    ONES = 1
    FULL = 2

    def __str__(self):
        match self:
            case Reroll.NO:
                return ""

            case Reroll.ONES:
                return "r1"
            
            case Reroll.FULL:
                return "r"
            
    @staticmethod
    def from_str(in_str: str):
        match in_str:
            case "r1":
                return Reroll.ONES
            
            case "r":
                return Reroll.FULL
            
            case "":
                return Reroll.NO
            
            case _:
                raise Format_Exception(
                    token=in_str,
                    reason="invalid reroll value"
                )
