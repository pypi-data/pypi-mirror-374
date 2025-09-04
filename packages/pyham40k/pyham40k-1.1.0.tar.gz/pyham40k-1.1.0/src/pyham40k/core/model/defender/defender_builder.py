from pyham40k.core.model.value import Base_Value

from .defender import Defender
from .defender_state import Defender_Builder_State


class Defender_Builder:

    state: Defender_Builder_State

    def __init__(self):
        self.state = Defender_Builder_State.ACCEPT_TOUGHNESS

    # Accepts sequence of values one by one, validates them and reports on them
    # 4 values are needed as per Defender constructor
    # returns True when all 4 values were validated
    # else returns False. Also can raise Format_Exception and AtributeError
    # use build() method to get the resulting Defender  
    def build_step(self, value: Base_Value | None) -> bool:
        match self.state:

            case Defender_Builder_State.ACCEPT_TOUGHNESS:
                Defender._validate_toughness(value)
                self.state = Defender_Builder_State.ACCEPT_SAVE
                self.toughness = value
                return False
            
            case Defender_Builder_State.ACCEPT_SAVE:
                Defender._validate_save(value)
                self.state = Defender_Builder_State.ACCEPT_INVULNERABLE
                self.save = value
                return False
            
            case Defender_Builder_State.ACCEPT_INVULNERABLE:
                Defender._validate_invulnerable(value)
                self.state = Defender_Builder_State.ACCEPT_FEEL_NO_PAIN
                self.invulerable = value
                return False
            
            case Defender_Builder_State.ACCEPT_FEEL_NO_PAIN:
                Defender._validate_feel_no_pain(value)
                self.state = Defender_Builder_State.READY
                self.feel_no_pain = value
                return True

            case Defender_Builder_State.READY:
                raise AttributeError("have already consumed all the values")

    def build(self) -> Defender:
        if self.state != Defender_Builder_State.READY:
            raise AttributeError("Defender has less valies than needed")
        
        return Defender(
            self.toughness,
            self.save,
            self.invulerable,
            self.feel_no_pain
        )

    # Returns True when object is ready
    def __bool__(self):
        return self.state == Defender_Builder_State.READY
