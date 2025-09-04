from .simple_value import Format_Exception, Simple_Value, Reroll


class Positive_Value(Simple_Value):

    def __init__(
        self,
        in_value: int,
        in_modifier: int = 0,
        in_reroll: Reroll = Reroll.NO
    ):
        if in_value <= 0:
            raise AttributeError("expected non-positive integer")
        
        super().__init__(in_value, in_modifier, in_reroll)

    
    @staticmethod
    def from_str_validate(in_str: str) -> tuple[int, int, Reroll]:
        value, mod, reroll = Simple_Value.from_str_validate(in_str)

        if value <= 0:
            raise Format_Exception(
                token=str(value),
                reason="expected positive integer"
            )
        
        return (value, mod, reroll)
