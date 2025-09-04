from pyham40k.core.model.value import Positive_Value, Not_Assigned_Value
from pyham40k.core.model.format_exception import Format_Exception

from .constants import DEFENDER_STAT_COL_WIDTH, DEFENDER_STAT_HEADER

class Defender:

    toughness: Positive_Value
    save: Positive_Value
    invulnerable: Positive_Value | Not_Assigned_Value
    feel_no_pain: Positive_Value | Not_Assigned_Value
    
    STAT_HEADER = DEFENDER_STAT_HEADER
    STAT_COL_WIDTH = DEFENDER_STAT_COL_WIDTH

    def __init__(
        self, in_toughness: Positive_Value, in_save: Positive_Value,
        in_invulnerable: Positive_Value | Not_Assigned_Value = Not_Assigned_Value(),
        in_feel_no_pain: Positive_Value | Not_Assigned_Value = Not_Assigned_Value()
    ):
        Defender._validate_toughness(in_toughness)
        Defender._validate_save(in_save)
        Defender._validate_invulnerable(in_invulnerable)
        Defender._validate_feel_no_pain(in_feel_no_pain)

        self.toughness = in_toughness
        self.save = in_save
        self.invulnerable = in_invulnerable
        self.feel_no_pain = in_feel_no_pain

    @staticmethod
    def _validate_toughness(in_toughness: Positive_Value):
        if not isinstance(in_toughness, Positive_Value):
            raise Format_Exception(
                token=str(in_toughness),
                reason="not a valid value for defender's toughness"
            )
        
    @staticmethod
    def _validate_save(in_save: Positive_Value):
        if not isinstance(in_save, Positive_Value):
            raise Format_Exception(
                token=str(in_save),
                reason="not a valid value for defender's save"
            )
        
    @staticmethod
    def _validate_invulnerable(in_invulnerable: Positive_Value | Not_Assigned_Value):
        if not (isinstance(in_invulnerable, Positive_Value) or \
            isinstance(in_invulnerable, Not_Assigned_Value)
        ):
            raise Format_Exception(
                token=str(in_invulnerable),
                reason="not a valid value for defender's invulnerable"
            )
        
    @staticmethod
    def _validate_feel_no_pain(in_feel_no_pain: Positive_Value | Not_Assigned_Value):
        if not (isinstance(in_feel_no_pain, Positive_Value) or \
            isinstance(in_feel_no_pain, Not_Assigned_Value)
        ):
            raise Format_Exception(
                token=str(in_feel_no_pain),
                reason="not a valid value for defender's feel no pain"
            )
        
    def __eq__(self, value: "Defender"):
        return (self.toughness == value.toughness) and \
            (self.save == value.save) and \
            (self.invulnerable == value.invulnerable) and \
            (self.feel_no_pain == value.feel_no_pain)

    def __str__(self):        
        return Defender.STAT_HEADER + "\n" + "|".join(
            (
                f"{str(self.toughness):^{Defender.STAT_COL_WIDTH}}",
                f"{str(self.save):^{Defender.STAT_COL_WIDTH}}",
                f"{str(self.invulnerable):^{Defender.STAT_COL_WIDTH}}",
                f"{str(self.feel_no_pain):^{Defender.STAT_COL_WIDTH}}"
            )
        )
