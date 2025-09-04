from random import randint

from pyham40k.core.model.format_exception import Format_Exception

from .base_value import Base_Value, Reroll


class Random_Value(Base_Value):

    die_size: int
    multiplier: int

    def __init__(
        self,
        in_die_size: int,
        in_modifier: int = 0,
        in_reroll: Reroll = Reroll.NO,
        in_multiplier: int = 1,
    ):

        if (in_die_size < 2) or not isinstance(in_die_size, int):
            raise AttributeError("dice size nonsensical")
        
        if (in_multiplier < 1) or not isinstance(in_multiplier, int):
            raise AttributeError("multiplier nonsensical")

        self.die_size = in_die_size
        self.multiplier = in_multiplier
        super().__init__(in_modifier, in_reroll)

    def __eq__(self, other: "Random_Value"):
        return (self.die_size == other.die_size) and \
             (self.multiplier == other.multiplier) and super().__eq__(other)

    def __hash__(self):
        return hash((self.die_size, self.modifier, self.reroll, self.multiplier))

    def __str__(self):
        out = f"{self.multiplier if self.multiplier > 1 else ""}d{self.die_size}"
        return out + self._str_partial()

    def __call__(self) -> int:
        out_sum = 0
        for _ in range(self.multiplier):
            out_sum += randint(1, self.die_size) + self.modifier
        
        return out_sum

    @staticmethod
    def from_str_validate(in_str: str) -> tuple[int, int, Reroll, int]:
        value, mod, reroll = Base_Value._from_str_partial(in_str)
        possible_mult_die = value.split("d") # drop the "d" and get "ints"

        multiplier = None
        die = None
        if len(possible_mult_die) == 2:
            # multiplier may be omitted, producing an empty str after split()
            multiplier = possible_mult_die[0] if possible_mult_die[0] else 1
            die = possible_mult_die[1]

        else:
            raise Format_Exception(
                token=value,
                reason="too many 'd's"
            )

        # validate die_size
        try:
            die = int(die)

        except ValueError:
            raise Format_Exception(
                token=value,
                reason="not a valid integer for die size"
            )
        
        if die < 2:
            raise Format_Exception(
                token=value,
                reason="die size nonsensical"
            )
        
        # validate multiplier
        try:
            multiplier = int(multiplier)

        except ValueError:
            raise Format_Exception(
                token=value,
                reason="not a valid integer for multiplier"
            )
        
        if multiplier < 1:
            raise Format_Exception(
                token=value,
                reason="multiplier nonsensical"
            )
        
        return (die, mod, reroll, multiplier)

    def expected_value(self) -> float:
        
        # total EV of 1 die. As per the linearity ofexpectation, EV of sum of
        # random variables (die rolls) is the sum of resective EVs. Since dice
        # are the same, the EVs are also the same. Therefore EV of 1 die can 
        # be multiplied by nember of dice (multiplier) to produce EV of sum.
        total_ev = None

        match self.reroll:
            case Reroll.NO:
                total_ev = ((self.die_size + 1) / 2 + self.modifier)

            case Reroll.ONES:
                # The EV finite sum with a reroll substitutes the
                # first term 1/die_size for a rerolled term EV/die_size.
                # As such, the final EV is computed by adding the difference
                # between sums.

                normal_ev = (self.die_size + 1) / 2
                total_ev = normal_ev + (normal_ev - 1) / self.die_size + self.modifier
        
            case Reroll.FULL:
                # The strategy of full reroll is to reroll all the values lower
                # or equal to the ev. Therefore, the finite sum that defines EV
                # can be broken down into 2 peices: 
                # 1) probability of die landing on side that is <= EV, multiplied
                # by the EV of a new roll.
                # 2) part of "normal" EV sum with values > EV.
                # 
                # As such, the algorithm works in the following way:
                # 1. Compute "normal" EV.
                # 2. Compute the number of values <= EV. This is the floor of EV.
                # 3. Compute point 1) of strategy.
                # 4. Compute point 2) of strategy.
                # 5. Sum up the parts and the modifier.

                normal_ev = (self.die_size + 1) / 2
                floored_nat_ev = int(normal_ev)
                lower_rerolled_ev = (floored_nat_ev / self.die_size) * normal_ev
                upper_ev = (floored_nat_ev + 1 + self.die_size) * \
                    (self.die_size - floored_nat_ev) / (2 * self.die_size) 
                total_ev = lower_rerolled_ev + upper_ev + self.modifier

        return self.multiplier * total_ev
    