from pyham40k.core.model.format_exception import Format_Exception

from .base_value import Base_Value, Reroll


class Simple_Value(Base_Value):

    value: int

    def __init__(
        self,
        in_value: int,
        in_modifier: int = 0,
        in_reroll: Reroll = Reroll.NO
    ):
        self.value = in_value
        super().__init__(in_modifier, in_reroll)

    def __eq__(self, other: "Simple_Value"):
        return (self.value == other.value) and super().__eq__(other)

    def __hash__(self):
        return hash((self.value, self.modifier, self.reroll))

    def __str__(self):
        out = str(self.value)
        return out + self._str_partial()
    
    def __call__(self) -> int:
        return self.value

    @staticmethod
    def from_str_validate(in_str: str) -> tuple[int, int, Reroll]:
        value, mod, reroll = Base_Value._from_str_partial(in_str)

        try:
            value = int(value)

        except ValueError:
            raise Format_Exception(
                token=value,
                reason="not a valid integer"
            )
        
        return (value, mod, reroll)

    def expected_value(self) -> float:
        return float(self.value)
    
    def get_value(self) -> int:
        return self.value
    