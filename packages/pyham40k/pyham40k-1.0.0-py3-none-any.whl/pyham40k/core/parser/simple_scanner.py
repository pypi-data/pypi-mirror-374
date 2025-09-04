from rich.console import Console

from pyham40k.core.model.attacker import Attacker, Attacker_Builder
from pyham40k.core.model.defender import Defender, Defender_Builder
from pyham40k.core.model.value import Base_Value
from pyham40k.core.model import Format_Exception

from .simple_parser import Simple_Parser


class Simple_Scanner:
    
    console: Console
    parser: Simple_Parser
    
    def __init__(self, in_console: Console = Console()):
        self.console = in_console
        self.parser = Simple_Parser()
    
    # Produces Attacker instance from console input
    def scan_attacker_input(self) -> Attacker:
        builder = Attacker_Builder()

        self.console.print("Please, input attacker below:\n")
        self.console.print("Status: ok")
        self.console.print(Attacker.STAT_HEADER)

        return self._scan_input_helper(
            builder,
            Attacker.STAT_HEADER
        )

    # Produces Defender instance from console input
    def scan_defender_input(self) -> Attacker:
        builder = Defender_Builder()

        self.console.print("Please, input defender below:\n")
        self.console.print("Status: ok")
        self.console.print(Defender.STAT_HEADER)

        return self._scan_input_helper(
            builder,
            Defender.STAT_HEADER
        )

    # Helper that encapsulates common input loop
    def _scan_input_helper(
        self,
        builder: Attacker_Builder | Defender_Builder,
        stat_header: str
    ) -> Attacker | Defender:
        
        displayed_values: list[Base_Value] = []
        while not builder:
            try:
                val_str = self.console.input()

                val = self.parser.parse_value(val_str)
                builder.build_step(val)
                displayed_values.append(val)
                
                self._reprint_stat_block(
                    f"Status: ok",
                    stat_header,
                    self._format_value_list_to_table(displayed_values)
                )
            
            except Format_Exception as e:
                self._reprint_stat_block(
                    f"Status: {str(e)}",
                    stat_header,
                    self._format_value_list_to_table(displayed_values)
                )

        return builder.build()

    # clears lines and reprints them with new information
    def _reprint_stat_block(self, status: str, header: str, value_str: str):
        self._clear_lines_up(3) # Will clear status, header, values
        self.console.print(status)
        self.console.print(header)
        self.console.print(value_str, end="")

    def _clear_lines_up(self, n_lines: int):
        for _ in range(n_lines):
            self.console.file.write("\x1b[1A\x1b[2K")
        
        self.console.file.flush()

    def _format_value_list_to_table(self, values: list[Base_Value]) -> str:
        return "|".join(
            map(
                lambda x: f"{str(x):^{Attacker.STAT_COL_WIDTH}}",
                values
            )
        )
