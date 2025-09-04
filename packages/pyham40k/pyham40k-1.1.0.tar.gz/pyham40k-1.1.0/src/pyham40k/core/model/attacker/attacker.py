from pyham40k.core.model.value import (
    Random_Value,
    Non_Positive_Value,
    Positive_Value,
    Not_Assigned_Value
)
from pyham40k.core.model.format_exception import Format_Exception

from .constants import ATTACKER_STAT_COL_WIDTH, ATTACKER_STAT_HEADER


class Attacker:

    attacks: Positive_Value | Random_Value
    skill: Positive_Value | None
    strength: Positive_Value
    penetration: Non_Positive_Value
    damage: Positive_Value | Random_Value

    STAT_HEADER = ATTACKER_STAT_HEADER
    STAT_COL_WIDTH = ATTACKER_STAT_COL_WIDTH

    def __init__(
        self,
        in_attacks: Positive_Value | Random_Value,
        in_skill: Positive_Value | Not_Assigned_Value,
        in_strength: Positive_Value,
        in_penetration: Non_Positive_Value,
        in_damage: Positive_Value | Random_Value
    ):
        Attacker._validate_attacks(in_attacks)
        Attacker._validate_skill(in_skill)
        Attacker._validate_strength(in_strength)
        Attacker._validate_penetration(in_penetration)
        Attacker._validate_damage(in_damage)
        
        self.attacks = in_attacks
        self.skill = in_skill
        self.strength = in_strength
        self.penetration = in_penetration
        self.damage = in_damage

    @staticmethod
    def _validate_attacks(in_attacks: Positive_Value | Random_Value):
        if not (isinstance(in_attacks, Positive_Value) or \
            isinstance(in_attacks, Random_Value)
        ):
            raise Format_Exception(
                token=str(in_attacks),
                reason="not a valid value for attacker's attack"
            )
    
    @staticmethod
    def _validate_skill(in_skill: Positive_Value | Not_Assigned_Value):
        if not (isinstance(in_skill, Positive_Value) or \
            isinstance(in_skill, Not_Assigned_Value)
        ):
            raise Format_Exception(
                token=str(in_skill),
                reason="not a valid value for attacker's skill"
            )
    
    @staticmethod
    def _validate_strength(in_strength: Positive_Value):
        if not isinstance(in_strength, Positive_Value):
            raise Format_Exception(
                token=str(in_strength),
                reason="not a valid value for attacker's strength"
            )
    
    @staticmethod
    def _validate_penetration(in_penetration: Non_Positive_Value):
        if not isinstance(in_penetration, Non_Positive_Value):
            raise Format_Exception(
                token=str(in_penetration),
                reason="not a valid value for attacker's penetration"
            )
    
    @staticmethod
    def _validate_damage(in_damage: Positive_Value | Random_Value):
        if not (isinstance(in_damage, Positive_Value) or \
            isinstance(in_damage, Random_Value)
        ):
            raise Format_Exception(
                token=str(in_damage),
                reason="not a valid value for attacker's damage"
            )
    
    def __eq__(self, value: "Attacker"):
        return (self.attacks == value.attacks) and \
            (self.skill == value.skill) and \
            (self.strength == value.strength) and \
            (self.penetration == value.penetration) and \
            (self.damage == value.damage)

    def __str__(self):
        return Attacker.STAT_HEADER + "\n" + "|".join(
            (
                f"{str(self.attacks):^{Attacker.STAT_COL_WIDTH}}",
                f"{str(self.skill):^{Attacker.STAT_COL_WIDTH}}",
                f"{str(self.strength):^{Attacker.STAT_COL_WIDTH}}",
                f"{str(self.penetration):^{Attacker.STAT_COL_WIDTH}}",
                f"{str(self.damage):^{Attacker.STAT_COL_WIDTH}}"
            )
        )
    
    cool_reference =  "Angreifer"
