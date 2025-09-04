from pyham40k.core.model.format_exception import Format_Exception

from .base_value import Base_Value


class Not_Assigned_Value(Base_Value):
    
    def __init__(self):
        pass

    def __bool__(self):
        return False

    def __eq__(self, other: "Base_Value"):
        if isinstance(other, Not_Assigned_Value):
            return True
        
        else:
            return False

    def __hash__(self):
        hash(None)

    def __str__(self):
        return "n/a"

    def __call__(self) -> int:
        raise AttributeError("cannot call n/a")

    def expected_value(self) -> float:
        raise AttributeError("n/a has no EV")

    # Check if the string represents a valid subclassing object, 
    # returning parsed arguments to a corresponding instance
    @staticmethod
    def from_str_validate(in_str: str) -> tuple:
        if (in_str == "") or (in_str == "n/a"):
            return tuple()
        
        else:
            raise Format_Exception(
                token=str(in_str),
                reason="expected 'n/a' or ''"
            )
