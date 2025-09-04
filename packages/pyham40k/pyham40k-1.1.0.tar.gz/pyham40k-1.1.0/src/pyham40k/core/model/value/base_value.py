from abc import ABC, abstractmethod

from pyham40k.core.model.reroll import Reroll
from pyham40k.core.model.format_exception import Format_Exception


class Base_Value(ABC):

    modifier: int
    reroll: Reroll

    def __init__(self, in_modifier: int = 0, in_reroll: Reroll = Reroll.NO):
        if not isinstance(in_modifier, int):
            raise AttributeError("expected integer modifier")
        
        if not isinstance(in_reroll, Reroll):
            raise AttributeError("not a valid reroll type")

        self.modifier = in_modifier
        self.reroll = in_reroll
        super().__init__()

    def __eq__(self, other: "Base_Value"):
        return (self.modifier == other.modifier) and \
            (self.reroll == other.reroll)

    def __bool__(self):
        return True
    
    @abstractmethod
    def __hash__(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def __call__(self) -> int:
        "samples a scalar value"

    @abstractmethod
    def expected_value(self) -> float:
        "returns a scalar - EV of the value"

    # Check if the string represents a valid subclassing object, 
    # returning parsed arguments to a corresponding instance
    @staticmethod
    @abstractmethod
    def from_str_validate(in_str: str) -> tuple:
        pass

    # Common logic of converting subclassing values to string
    def _str_partial(self) -> str:
        out = ""

        if self.modifier:
            out += f" {self.modifier:+}"

        if self.reroll != Reroll.NO:
            out += f" {str(self.reroll)}"

        return out

    # Common logic of parsing subclassing values from string
    @staticmethod
    def _from_str_partial(in_str: str) -> tuple[str, int, Reroll]:
        args = in_str.split()

        if (len(args) < 1) or (len(args) > 3):
            raise Format_Exception(
                token=in_str,
                reason="must have between 1 and 3 values to unpack"
            )

        value = args[0]
        modifier = 0
        reroll = Reroll.NO

        if len(args) == 2:
            if args[1][0] == "r":
                reroll = Reroll.from_str(args[1])

            else:
                try:
                    modifier = Base_Value._parse_modifier(args[1])

                except Format_Exception:
                    raise Format_Exception(
                        token=args[1],
                        reason="not a valid modifier or reroll value"
                    )
        
        if len(args) == 3:
            modifier = Base_Value._parse_modifier(args[1])
            reroll = Reroll.from_str(args[2])

        return (value, modifier, reroll)

    @staticmethod
    def _parse_modifier(in_str: str) -> int:
        try:
            return int(in_str)

        except ValueError:
            raise Format_Exception(
                token=in_str,
                reason="modifier must be an integer"
            )
