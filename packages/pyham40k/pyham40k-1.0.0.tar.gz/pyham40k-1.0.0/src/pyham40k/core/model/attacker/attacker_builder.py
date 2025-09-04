from pyham40k.core.model.value import Base_Value

from .attacker import Attacker
from .attacker_state import Attacker_Builder_State


class Attacker_Builder:

    state: Attacker_Builder_State

    def __init__(self):
        self.state = Attacker_Builder_State.ACCEPT_ATTACKS

    # Accepts sequence of values one by one, validates them and reports on them
    # 5 values are needed as per Attacker constructor
    # returns True when all 5 values were validated
    # else returns False. Also can raise Format_Exception
    # use build() method to get the resulting Attacker  
    def build_step(self, value: Base_Value | None) -> bool:
        match self.state:

            case Attacker_Builder_State.ACCEPT_ATTACKS:
                Attacker._validate_attacks(value)
                self.state = Attacker_Builder_State.ACCEPT_SKILL
                self.attacks = value
                return False
            
            case Attacker_Builder_State.ACCEPT_SKILL:
                Attacker._validate_skill(value)
                self.state = Attacker_Builder_State.ACCEPT_STRENGTH
                self.skill = value
                return False
            
            case Attacker_Builder_State.ACCEPT_STRENGTH:
                Attacker._validate_strength(value)
                self.state = Attacker_Builder_State.ACCEPT_PENETRATION
                self.strength = value
                return False
            
            case Attacker_Builder_State.ACCEPT_PENETRATION:
                Attacker._validate_penetration(value)
                self.state = Attacker_Builder_State.ACCEPT_DAMAGE
                self.penetration = value
                return False
            
            case Attacker_Builder_State.ACCEPT_DAMAGE:
                Attacker._validate_damage(value)
                self.state = Attacker_Builder_State.READY
                self.damage = value
                return True

            case Attacker_Builder_State.READY:
                raise AttributeError("have already consumed all the values")

    def build(self) -> Attacker:
        if self.state != Attacker_Builder_State.READY:
            raise AttributeError("Attacker has less valies than needed")
        
        return Attacker(
            self.attacks,
            self.skill,
            self.strength,
            self.penetration,
            self.damage
        )

    # Returns True when object is ready
    def __bool__(self):
        return self.state == Attacker_Builder_State.READY
