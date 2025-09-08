from .interpreter import S3Interpreter

# Create a single interpreter object that will be used for all calls
_interpreter = S3Interpreter()

# Define functions that use the single instance
def interpret(code_line):
    """
    Runs a single line of S-language code using the single interpreter instance.
    """
    _interpreter.interpret(code_line)

def multiline(*code_lines):
    """
    Runs multiple lines of S-language code using the single interpreter instance.
    """
    _interpreter.multiline(*code_lines)

__all__ = ['S3Interpreter', 'interpret', 'multiline']
