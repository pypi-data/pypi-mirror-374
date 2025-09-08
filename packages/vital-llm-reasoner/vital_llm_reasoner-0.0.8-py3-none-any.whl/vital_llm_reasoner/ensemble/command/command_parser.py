from lark import Lark, Transformer

class CommandTransformer(Transformer):
    def command(self, items):
        # items[0] is the function/command name.
        # If a second item is present, it is the dict of parameters.
        function_name = items[0]
        params = items[1] if len(items) > 1 else {}
        return {"command": function_name, "params": params}

    def arg_list(self, items):
        # Merge individual argument dictionaries.
        result = {}
        for arg in items:
            result.update(arg)
        return result

    def arg(self, items):
        # Each argument becomes a key/value pair in a dict.
        return {items[0]: items[1]}

    def NAME(self, token):
        return token.value

    def DOUBLE_QUOTED_STRING(self, token):
        # Strip the surrounding double quotes.
        return token.value[1:-1]

    def SINGLE_QUOTED_STRING(self, token):
        # Strip the surrounding single quotes.
        return token.value[1:-1]

    def string(self, items):
        # The string rule returns the contained token.
        return items[0]

class CommandParser:
    grammar = r"""
        ?start: command

        // A command: NAME, then parenthesized arguments, then a period.
        command: NAME "(" [arg_list] ")" "."

        // A comma-separated list of arguments.
        arg_list: arg ("," arg)*

        // Each argument is NAME "=" string.
        arg: NAME "=" string

        // A string may be either a double-quoted or single-quoted string.
        ?string: DOUBLE_QUOTED_STRING | SINGLE_QUOTED_STRING

        // Define a NAME: a letter or underscore followed by alphanumerics or underscores.
        NAME: /[a-zA-Z_]\w*/

        // Define tokens for double-quoted and single-quoted strings.
        DOUBLE_QUOTED_STRING: /"([^"\\]*(\\.[^"\\]*)*)"/
        SINGLE_QUOTED_STRING: /'([^'\\]*(\\.[^'\\]*)*)'/

        // Ignore all whitespace (including spaces, tabs, and newlines).
        %ignore /\s+/
    """

    def __init__(self):
        # Create a LALR parser with our grammar and attach our transformer.
        self.parser = Lark(self.grammar, parser="lalr", transformer=CommandTransformer())

    def parse(self, text):
        try:
            return self.parser.parse(text)
        except Exception as e:
            # Return the error information in a dict.
            return {"error": str(e)}


# Example usage:
if __name__ == '__main__':
    cp = CommandParser()

    command_list = [

        'summarize(url="http://example.com", filepath=\'filename.txt\').',
        'summarize(url="http://example.com", filepath=\'filename.txt\')',
        'websearch().',
        """
        websearch(topic='
        this is a topic.
        it goes on for a while.
        here is some more', 
        keywords='science', goal='unified field theory').""",
    ]

    for c in command_list:
        result = cp.parse(c)
        print(result)
