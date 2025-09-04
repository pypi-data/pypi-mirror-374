from enum import Enum
from typing import Any, Iterable

from pyham40k.core.calculator import Floor_Calculator, Real_Calculator
from .model import Cli_Prompt, Cli_Choice, Cli_File_Prompt


WELCOME_MESSAGE = "pyham - to overanalyze your Warhammer 40k 10e gameplay"
QUICK_REFERENCE = "this is a tool to compare weapon performance against\n" + \
"one another with a specific target in terms of epected number of wounds\n" + \
"enter keys in parenthesis to choose actions\n\n" + \
"attacker and defender profiles are represented in table format\n" + \
"for attacker:\n" + \
"A - attacks; H - to hit (bs/ws); S - strength;\n" + \
"P - penetration (ap); D -damage\n" + \
"for defender:\n" + \
"T - toughness; S - save (sv); I - invulnerable; F - feel no pain\n\n" + \
"some of these values can be random (example d6 attacks)\n" + \
"some of these values can be modified (example: +1 strength means +1 to wound)\n" + \
"some of these values can be rerooled (example: r1 hit is reroll of 1s to hit)\n" + \
"some values are not assigned and can be skipped (example: n/a hit for torrent)\n\n" + \
"example attacker:\n" + \
"  A  |  H  |  S  |  P  |  D  \n" + \
" 12  |3 r1 |  6  |-1 +1|  1  \n" + \
"example defender:\n" + \
"  T  |  S  |  I  |  F  \n" + \
"  3  |  5  | n/a | n/a \n"

GEQ_STR = " 3 | 5 | n/a | n/a "
MEQ_STR = " 4 | 3 | n/a | n/a "
TEQ_STR = " 5 | 2 |  4  | n/a "


INTER_SHARED = Cli_Choice(
    "Interactive input (No loading)",
    ("1", "N", "")
)
FILE_SHARED = Cli_Choice(
    "Load file",
    ("2", "Y")
)


FILE_PROMPT_OBJ = Cli_File_Prompt()


# "Quick Values" as in "has a shortcut to extract all values"
class Enum_Quick_Values(Enum):

    @classmethod
    def get_values(cls) -> Iterable[Any] :
        return map(
            lambda x: x.value,
            cls._member_map_.values()
        )
    
    @classmethod
    def get_values_tuple(cls) -> tuple[Any] :
        return tuple(cls.get_values())
    

class Startup_Choice(Enum_Quick_Values):
    CALCULATE = Cli_Choice(
        "Calculate",
        ("1", "")
    )
    REF = Cli_Choice(
        "Print quick reference",
        ("2",)
    )


class Calculator_Choice(Enum_Quick_Values):
    ALL = Cli_Choice(
        f"All ({Real_Calculator.VERBOSE_NAME}," + \
            f"{Floor_Calculator.VERBOSE_NAME})",
        ("1", "")
    )
    REAL = Cli_Choice(
        f"{Real_Calculator.VERBOSE_NAME} ({Real_Calculator.QUICK_REF})",
        ("2",)
    )
    FLOOR = Cli_Choice(
        f"{Floor_Calculator.VERBOSE_NAME} ({Floor_Calculator.QUICK_REF})",
        ("3",)
    )


class Load_Attacker_Choice(Enum_Quick_Values):
    INTER = INTER_SHARED
    FILE = FILE_SHARED


class Load_Defender_Choice(Enum_Quick_Values):
    INTER = INTER_SHARED
    FILE = FILE_SHARED
    GEQ = Cli_Choice(
        "Load GEQ",
        ("3",)
    )
    MEQ = Cli_Choice(
        "Load MEQ",
        ("4",)
    )
    TEQ = Cli_Choice(
        "Load TEQ",
        ("5",)
    )


class Save_Choice(Enum_Quick_Values):
    FILE = Cli_Choice(
        "Yes",
        ("1", "Y")
    )
    NO = Cli_Choice(
        "No",
        ("2", "N", "")
    )


class Cli_Prompt_Enum(Enum_Quick_Values):
    STARTUP = Cli_Prompt(
        "Select action",
        in_choices=Startup_Choice.get_values_tuple()
    )

    CALCULATOR = Cli_Prompt(
        "Select calculator",
        in_choices=Calculator_Choice.get_values_tuple()
    )

    LOAD_ATKR = Cli_Prompt(
        "Load attacker profile from file?",
        in_choices=Load_Attacker_Choice.get_values_tuple()
    )

    LOAD_DEF = Cli_Prompt(
        "Load defender profile from file?",
        in_choices=Load_Defender_Choice.get_values_tuple()
    )

    SAVE = Cli_Prompt(
        "Save this profile?",
        in_choices=Save_Choice.get_values_tuple()
    )
