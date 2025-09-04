from rich.console import Console

from .cli_choice import Cli_Choice


# The class to promt user for input with options
class Cli_Prompt:

    # This prompt should appear above choices for clarity, as it might be long
    prompt: str
    choices: tuple[Cli_Choice]
    
    def __init__(self, in_prompt: str, in_choices: tuple[Cli_Choice]):
        self.prompt = in_prompt

        # Ensure there are no choices with the same inputs
        intersection = set.intersection(
            *map(
                lambda x: set(x.inputs),
                in_choices
            )
        )
        if len(intersection):
            raise AttributeError(
                "cannot have choices with the same inputs"
            )

        self.choices = in_choices

    def _collect_inputs(self) -> list[str]:
        out = []

        for c in self.choices:
            out.extend(c.inputs)

        return out

    def ask(self, in_console: Console) -> Cli_Choice:
        in_console.print(self.prompt)
        in_console.print(self.get_options_str())
        in_console.print("> ", end="")

        user_input = in_console.input()
        while not self._validate_str_with_choices(user_input):
            # Erase erroneous line with user input
            in_console.file.write("\x1b[1A\x1b[2K")

            in_console.print("Invalid option > ", end="")
            user_input = in_console.input()
            
        # When input was accepted
        in_console.file.write("\x1b[1A\x1b[2K")
        in_console.print(f"Ok > {user_input}")

        for c in self.choices:
            if c.validate(user_input):
                return c

    def get_options_str(self) -> str:
        return "\n".join(
            map(
                lambda x: str(x),
                self.choices
            )
        )

    def _validate_str_with_choices(self, in_str: str) -> bool:
        for c in self.choices:
            if c.validate(in_str):
                return True
            
        return False
