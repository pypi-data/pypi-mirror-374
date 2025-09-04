from enum import Enum


class Attacker_Builder_State(Enum):
    ACCEPT_ATTACKS = 0,
    ACCEPT_SKILL = 1,
    ACCEPT_STRENGTH = 2,
    ACCEPT_PENETRATION = 3,
    ACCEPT_DAMAGE = 4,
    READY = 5
