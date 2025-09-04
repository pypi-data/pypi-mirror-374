from rich.console import Console

from pyham40k.core.calculator import Real_Calculator, Floor_Calculator
from pyham40k.core.parser import Simple_Scanner
from pyham40k.core.model import Attacker, Defender, Format_Exception

from .constants import (
    Cli_Prompt_Enum,

    Startup_Choice, Calculator_Choice, Load_Attacker_Choice, 
    Load_Defender_Choice, Save_Choice,

    WELCOME_MESSAGE,
    QUICK_REFERENCE,
    GEQ_STR, MEQ_STR, TEQ_STR,
    FILE_PROMPT_OBJ
)


class Cli_Controller:

    def __init__(self, in_console: Console = None):
        if in_console:
            self.console = in_console

        else:
            self.console = Console(highlight=False)
            
        self.scanner = Simple_Scanner(self.console)

    # Runs "once-a-boot-up" logic, i.e. printing welcome messge
    def startup(self):
        self.console.print(WELCOME_MESSAGE)
        self.console.print("") # Newline for spacing

        resp = Cli_Prompt_Enum.STARTUP.value.ask(
            self.console
        )

        # If user wants quick reference
        if resp == Startup_Choice.REF.value:
            self.console.print(QUICK_REFERENCE)

        self.console.print("") # Newline for spacing

    # Gets attacker and defender and calculates expected wounds
    def run_calculation_once(self):
        # Choose calculator
        calc_choice = Cli_Prompt_Enum.CALCULATOR.value.ask(
            self.console
        )
        self.console.print("") # Newline for spacing

        atkr = self._get_attacker()
        self.console.print("") # Newline for spacing
        self._save_profile(atkr)
        self.console.print("") # Newline for spacing

        dfnr = self._get_defender()
        self.console.print("") # Newline for spacing
        self._save_profile(dfnr)
        self.console.print("") # Newline for spacing

        # Instantiate the calculator
        match calc_choice:
            case Calculator_Choice.REAL.value:
                calculator = Real_Calculator(atkr, dfnr)
                wounds = calculator.calculate_total_unsvaed_wounds()
                self.console.print(
                    f"Expected number of wounds is: {wounds:.6f}"
                )

            case Calculator_Choice.FLOOR.value:
                calculator = Floor_Calculator(atkr, dfnr)
                wounds = calculator.calculate_total_unsvaed_wounds()
                self.console.print(
                    f"Expected number of wounds is: {wounds:.6f}"
                )

            case Calculator_Choice.ALL.value:
                r_calculator = Real_Calculator(atkr, dfnr)
                f_calculator = Floor_Calculator(atkr, dfnr)

                r_wounds = r_calculator.calculate_total_unsvaed_wounds()
                f_wounds = f_calculator.calculate_total_unsvaed_wounds()

                self.console.print(
                    f"({Real_Calculator.VERBOSE_NAME}) " + \
                        f"Expected number of wounds is: {r_wounds:.6f}"
                )
                self.console.print(
                    f"({Floor_Calculator.VERBOSE_NAME}) " + \
                        f"Expected number of wounds is: {f_wounds:.6f}"
                )

            case _:
                self._invalid_case_terminate(
                    "Invalid calculator. How did we even get here?"
                )

        self.console.print("") # Newline for spacing

    # Runs startup logic once and loops to calculate wounds
    def run_calculation(self):
        self.startup()

        while True:
            self.run_calculation_once()

    def _get_attacker(self) -> Attacker:
        atkr_action_choice = Cli_Prompt_Enum.LOAD_ATKR.value.ask(
            self.console
        )

        match atkr_action_choice:
            case Load_Attacker_Choice.INTER.value:
                return self.scanner.scan_attacker_input()

            case Load_Attacker_Choice.FILE.value:
                while True:
                    try:
                        file_path = FILE_PROMPT_OBJ.ask(self.console)
                        values = self._parse_profile_str_from_file(file_path)
                        return self._attacker_from_str_and_print(values)

                    except AttributeError:
                        pass

                    except Format_Exception as e:
                        self.console.print(str(e))
                
            case _:
                self._invalid_case_terminate(
                    "Invalid attacker option. How did we even get here?"
                )

    def _get_defender(self) -> Defender:
        dfnr_action_choice = Cli_Prompt_Enum.LOAD_DEF.value.ask(
            self.console
        )

        match dfnr_action_choice:
            case Load_Defender_Choice.INTER.value:
                return self.scanner.scan_defender_input()

            case Load_Defender_Choice.FILE.value:
                file_path = FILE_PROMPT_OBJ.ask(self.console)

                with open(file_path, "r") as f:
                    dfnr_str = f.read()
                    return self._defender_from_str_and_print(dfnr_str)

            case Load_Defender_Choice.GEQ.value:
                return self._defender_from_str_and_print(GEQ_STR)

            case Load_Defender_Choice.MEQ.value:
                return self._defender_from_str_and_print(MEQ_STR)

            case Load_Defender_Choice.TEQ.value:
                return self._defender_from_str_and_print(TEQ_STR)
                
            case _:
                self._invalid_case_terminate(
                    "Invalid defender option. How did we even get here?"
                )

    # Lets user see loaded profile in console
    def _defender_from_str_and_print(self, dfnr_str: str) -> Defender:
        dfnr = self.scanner.parser.parse_defender(dfnr_str)
        self.console.print(str(dfnr))
        return dfnr
    
    # Lets user see loaded profile in console
    def _attacker_from_str_and_print(self, atkr_str: str) -> Attacker:
        atkr = self.scanner.parser.parse_attacker(atkr_str)
        self.console.print(str(atkr))
        return atkr

    # Asks user to save the profile
    def _save_profile(self, profile: Attacker | Defender):
        save_action_choice = Cli_Prompt_Enum.SAVE.value.ask(
            self.console
        )

        match save_action_choice:
            case Save_Choice.NO.value:
                return
            
            case Save_Choice.FILE.value:
                file_path = FILE_PROMPT_OBJ.ask(self.console)

                with open(file_path, "w") as f:
                    profile_str = str(profile)
                    f.write(profile_str)

                return

            case _:
                self._invalid_case_terminate(
                    "Invalid save option. How did we even get here?"
                )

    def _invalid_case_terminate(self, reason: str):
        self.console.print(
            reason
        )
        # If this case is reached even after prompt validation 
        # the program is bound to be in an invalid state and 
        # should be terminated
        raise ValueError

    # Helper that check whether or not file contains a profile 
    # and returns a string of values.
    # Throws AttributeError if reading from file failed but can be retried
    def _parse_profile_str_from_file(self, file_path: str) -> str:
        file_str = None
        try:
            with open(file_path, "r") as f:
                file_str = f.read()

        except OSError:
            self.console.print("an error occured while opening the file")
            raise AttributeError

        # Assume the file has the following structure:
        # 1. Must have a header line
        # 2. Value line must follow after header line
        lines = file_str.split("\n")

        if len(lines) < 2:
            self.console.print("file has too few lines")
            raise AttributeError
        
        # For header line it is assumed that it contains "|" as separators
        for i, line in enumerate(lines[:-1]):
            if line.find("|"):
                return lines[i+1]
            
        self.console.print("file has no header and/or value lines")
        raise AttributeError
