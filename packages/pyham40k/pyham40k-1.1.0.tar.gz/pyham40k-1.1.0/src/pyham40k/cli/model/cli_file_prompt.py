from rich.console import Console


class Cli_File_Prompt:
    
    def ask(self, in_console: Console) -> str:
        in_console.print("Enter file path > ", end="")
        return in_console.input()
