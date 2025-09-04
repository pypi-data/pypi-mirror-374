from enum import Enum


class Defender_Builder_State(Enum):
    ACCEPT_TOUGHNESS = 0,
    ACCEPT_SAVE = 1,
    ACCEPT_INVULNERABLE = 2,
    ACCEPT_FEEL_NO_PAIN = 3,
    READY = 4
