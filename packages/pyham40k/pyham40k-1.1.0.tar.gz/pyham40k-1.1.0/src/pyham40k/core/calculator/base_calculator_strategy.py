from abc import ABC, abstractmethod

from pyham40k.core.model import Attacker, Defender, Reroll


# Made with 10th edition in mind
class Base_Calculator_Strategy(ABC):

    VERBOSE_NAME = None
    QUICK_REF = None

    attacker: Attacker
    defender: Defender

    DIE_SIZE: int = 6 # Just in case they change it in 11th (hope)

    def __init__(self, in_attacker: Attacker, in_defender: Defender):
        if not isinstance(in_attacker, Attacker):
            raise AttributeError("expected Attacker object")

        if not isinstance(in_defender, Defender):
            raise AttributeError("expected Defender object")
        
        self.attacker = in_attacker
        self.defender = in_defender

        super().__init__()

    # Calculates how many wounds defender is expected to sustain
    def calculate_total_unsvaed_wounds(self) -> float:
        attacks = self.get_attacks()
        hits = attacks * self.get_hit_proportion()
        wounds = hits * self.get_wound_proportion()
        unsaved_wounds = wounds * self.get_unsaved_proportion()
        damage = unsaved_wounds * self.get_damage()
        felt = damage * self.get_felt_proprtion()

        return felt

    # Returns expected number of attacks
    @abstractmethod
    def get_attacks(self) -> float:
        pass

    # Returns a proportion between 0.0 and 1.0. Proportion represents how many 
    # attacks are expected to hit
    @abstractmethod
    def get_hit_proportion(self) -> float:
        pass

    # Returns a proportion between 0.0 and 1.0. Proportion represents how many 
    # hits are expected to wound
    @abstractmethod
    def get_wound_proportion(self) -> float:
        pass

    # Returns a proportion between 0.0 and 1.0. Proportion represents how many 
    # wounds are expected to remain unsaved
    @abstractmethod
    def get_unsaved_proportion(self) -> float:
        pass

    # Returns expected damage
    @abstractmethod
    def get_damage(self) -> float:
        pass

    # Returns a proportion between 0.0 and 1.0. Proportion represents how many 
    # wounds (damage points) are expected to fail feel no pain
    @abstractmethod
    def get_felt_proprtion(self) -> float:
        pass
    
    # Restrict modifier between -1 and +1 as per most rules
    @staticmethod
    def _clamp_modifier(mod: int) -> int:
        return max(-1, min(1, mod))

    # Ensures val is always within die limit and enforces rules such as
    # 1 always failing and {die_size} always passing for things like hitting
    # and wounding
    @staticmethod
    def _clamp_passing_value(to_pass_val: int) -> int:
        return max(2, min(Base_Calculator_Strategy.DIE_SIZE, to_pass_val))

    # Returns a proportion between 0.0 and 1.0 of how many die sides will 
    # allow the roll to pass
    @staticmethod
    def _proportion_passed(to_pass: int) -> float:
        if to_pass > Base_Calculator_Strategy.DIE_SIZE:
            return 0.0

        pass_sides = Base_Calculator_Strategy.DIE_SIZE - to_pass + 1
        return pass_sides / Base_Calculator_Strategy.DIE_SIZE
    
    # Calculates new proportion with a possibility of a reroll. 
    # New proportion of passed rolls follows the following logic:
    # 1. {pass_proportion} roll have already made it
    # 2. either no, 1/{die_size} or 1-{pass_proportion} results can be rerolled
    # 3. then, {pass_proportion} of all reroll will make it on 2nd roll
    @staticmethod
    def _proportion_rerolled(pass_proportion: float, in_reroll: Reroll):
        match in_reroll:
            case Reroll.NO:
                return pass_proportion
            
            case Reroll.ONES:
                return pass_proportion + \
                    (1 / Base_Calculator_Strategy.DIE_SIZE) * pass_proportion
            
            case Reroll.FULL:
                return pass_proportion + \
                     (1 - pass_proportion) * pass_proportion

    # A shorthand for:
    # 1. _clamp_passing_value()
    # 2. _proportion_passed()
    # 3. _proportion_rerolled()
    @staticmethod
    def _clamp_and_get_proportion_rerolled(
        to_pass_val: int,
        in_reroll: Reroll
    ) -> float:
        clamped = Base_Calculator_Strategy._clamp_passing_value(to_pass_val)
        passed = Base_Calculator_Strategy._proportion_passed(clamped)
        return Base_Calculator_Strategy._proportion_rerolled(passed, in_reroll)
