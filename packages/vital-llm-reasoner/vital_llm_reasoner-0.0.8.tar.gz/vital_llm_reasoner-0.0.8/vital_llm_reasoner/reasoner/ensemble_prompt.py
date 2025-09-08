
class EnsemblePrompt:

    def __init__(self, *, prompt: list[dict[str, str]] = None):
        self.prompt = prompt

    def set_prompt(self, prompt: list[dict[str, str]]):
        self.prompt = prompt


