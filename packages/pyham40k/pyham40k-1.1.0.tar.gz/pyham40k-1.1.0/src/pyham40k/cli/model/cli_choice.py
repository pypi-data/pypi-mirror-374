# Describes choices that can be selected with several inputs
class Cli_Choice:

    text: str
    inputs: tuple[str]

    # Inputs are case-insensitive
    def __init__(self, in_text: str, in_inputs: tuple[str]):
        self.text = in_text

        upper_inputs = map(
            lambda x: x.upper(),
            in_inputs
        )
        # Enforce unique inputs
        self.inputs = tuple(dict.fromkeys(upper_inputs))
    
    def validate(self, input_str: str) -> bool:
        if input_str.upper() in self.inputs:
            return True
        
        else:
            return False

    def __str__(self):
        # Replace empty string input with str "default"
        processed = map(
            lambda x: x if x else "default",
            self.inputs
        )

        input_hint = " | ".join(processed)

        return f"( {input_hint} ) {self.text}"
