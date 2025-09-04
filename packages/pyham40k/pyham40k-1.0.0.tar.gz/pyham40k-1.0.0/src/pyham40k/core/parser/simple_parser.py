from pyham40k.core.model import Format_Exception, Attacker, Defender
from pyham40k.core.model.value import (
    Base_Value,
    Non_Positive_Value,
    Positive_Value,
    Random_Value,
    Value_Flyweight
)


class Simple_Parser:

    def parse_defender(self, defender_str: str) -> Defender:
        value_strs = defender_str.split("|")

        if len(value_strs) != 4:
            raise Format_Exception(
                token=defender_str,
                reason="invalid number of values for defender"
            )

        values = [
            self.parse_value(x) 
            for x in value_strs
        ]

        return Defender(*values)

    def parse_attacker(self, attacker_str: str) -> Attacker:
        value_strs = attacker_str.split("|")

        if len(value_strs) != 5:
            raise Format_Exception(
                token=attacker_str,
                reason="invalid number of values for attacker"
            )

        values = [
            self.parse_value(x) 
            for x in value_strs
        ]

        return Attacker(*values)

    def parse_value(self, value_str: str) -> Base_Value:
        trimmed = value_str.strip()

        # Check the first symbol to deduce the type:
        # 1. Not assigned is either "" or "n/a"
        # 1. Non positive starts with "-" or "0".
        # 2. Simple starts with any digit.
        # 3. Random starts contains "d".
        if (trimmed == "") or (trimmed == "n/a"):
            return Value_Flyweight.get_not_assigned_value()

        if (trimmed[0] == "-") or (trimmed[0] == "0"):
            return self._parse_non_positive(trimmed)
                
        # If "d" is in a string, than it either is a random value or not a
        # value at all. Both are handled by _parse_random()
        elif "d" in trimmed:
            return self._parse_random(trimmed)
        
        elif trimmed[0].isdigit():
            return self._parse_positive(trimmed)
        
        else:
            raise Format_Exception(
                token=trimmed,
                reason="could not parse any value"
            )

    def _parse_non_positive(self, value_str: str) -> Non_Positive_Value:
        value, mod, reroll = Non_Positive_Value.from_str_validate(value_str)

        return Value_Flyweight.get_non_positive_value(
            value,
            mod,
            reroll
        )
    
    def _parse_positive(self, value_str: str) -> Positive_Value:
        value, mod, reroll = Positive_Value.from_str_validate(value_str)

        return Value_Flyweight.get_positive_value(
            value,
            mod,
            reroll
        )

    def _parse_random(self, value_str: str) -> Random_Value:
        die_size, mod, reroll, multiplier = Random_Value.from_str_validate(value_str)

        return Value_Flyweight.get_random_value(
            die_size,
            mod,
            reroll,
            multiplier
        )
