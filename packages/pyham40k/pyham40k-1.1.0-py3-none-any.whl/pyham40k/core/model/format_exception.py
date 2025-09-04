# Exception that relates to str representation of models
class Format_Exception(AttributeError):
    token = str

    def __init__(self, token: str, reason: str, *args, name = ..., obj = ...):
        self.token = token
        self.reason = reason
        super().__init__(*args, name=name, obj=obj)

    def __str__(self):
        return f"'{self.token}' - {self.reason}"
