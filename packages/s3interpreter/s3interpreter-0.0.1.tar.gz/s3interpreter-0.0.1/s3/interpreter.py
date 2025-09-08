import re
import sys

class S3Interpreter:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(S3Interpreter, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.variables = {}
            self.functions = {}
            self.last_input = ""
            S3Interpreter._initialized = True
    
    # Rest of your methods
    def _evaluate_expression(self, expr_string):
        expr_string = expr_string.strip()
        expr_string = expr_string.replace('((input))', str(self.last_input))
        def var_replace(match):
            var_name = match.group(1)
            if var_name in self.variables:
                return str(self.variables[var_name])
            else:
                raise Exception(f"Undefined variable '{var_name}'")
        processed_expr = re.sub(r'\(([a-zA-Z_][a-zA-Z0-9_]*)\)', var_replace, expr_string)
        if "++" in processed_expr:
            parts = [p.strip() for p in processed_expr.split("++")]
            return ''.join(parts)
        if not re.fullmatch(r'[0-9+\-*/().\s]+', processed_expr):
            raise Exception("Invalid characters or syntax in arithmetic expression.")
        try:
            result = eval(processed_expr, {"__builtins__": None}, {})
            if isinstance(result, (int, float)):
                return result
            else:
                raise Exception("Expression did not evaluate to a valid number.")
        except Exception as e:
            raise Exception(f"Could not evaluate expression: {str(e)}")

    def _parse_line(self, line):
        line = line.split('$')[0].strip()
        if not line:
            return None
        if line.strip().lower() == "end":
            return ("end",)
        m = re.match(r'^func\s+<([a-zA-Z_][a-zA-Z0-9_]*)>$', line)
        if m:
            return ('func_def', m.group(1))
        m = re.match(r'^<([a-zA-Z_][a-zA-Z0-9_]*)>$', line)
        if m:
            return ('call_func', m.group(1))
        m = re.match(r'^if\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*"([^"]*)"\s*then$', line)
        if m:
            return ('if', m.group(1), m.group(2))
        m = re.match(r'^writeinput\s+(.*)$', line)
        if m:
            return ('writeinput', m.group(1))
        m = re.match(r'^img\s+"([^"]+)"$', line)
        if m:
            return ('img', m.group(1))
        if re.match(r'^write\s+\(\(input\)\)$', line):
            return ('write_system_input',)
        m = re.match(r'^write\s+\((.+)\)$', line)
        if m:
            content = m.group(1).strip()
            if re.fullmatch(r'[a-zA-Z_][a-zA-Z0-9_]*', content):
                return ('write_var', content)
            else:
                return ('write_expr', content)
        m = re.match(r'^write\s+(.*)$', line)
        if m:
            return ('write_literal', m.group(1))
        m = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s+(.*)$', line)
        if m:
            var, val = m.group(1), m.group(2).strip()
            expr_match = re.match(r'^\((.+)\)$', val)
            if val == '((input))':
                return ('var_assign_input', var)
            elif expr_match:
                return ('var_assign_expr', var, expr_match.group(1).strip())
            else:
                return ('var_assign_literal', var, val)
        return ('error', line)

    def _run_s_code(self, lines):
        idx = 0
        skip_stack = []
        def get_input(prompt):
            try:
                if sys.stdin.isatty():
                    return input(prompt + " ")
                else:
                    with open('/dev/tty', 'r') as tty:
                        print(prompt, end=' ', flush=True)
                        return tty.readline().rstrip('\n')
            except Exception:
                print("\nError: No interactive input possible (no terminal found).")
                sys.exit(1)
        while idx < len(lines):
            line = lines[idx]
            parsed = self._parse_line(line)
            if not parsed:
                idx += 1
                continue
            if parsed[0] == "func_def":
                funcname = parsed[1]
                fstart = idx + 1
                fend = fstart
                depth = 1
                while fend < len(lines):
                    p2 = self._parse_line(lines[fend])
                    if p2 and p2[0] == "func_def":
                        depth += 1
                    elif p2 and p2[0] == "end":
                        depth -= 1
                        if depth == 0:
                            break
                    fend += 1
                self.functions[funcname] = lines[fstart:fend]
                idx = fend + 1
                continue
            if skip_stack:
                if parsed[0] == "if":
                    skip_stack.append("if")
                elif parsed[0] == "end":
                    skip_stack.pop()
                idx += 1
                continue
            try:
                if parsed[0] == 'call_func':
                    fname = parsed[1]
                    if fname in self.functions:
                        self._run_s_code(self.functions[fname])
                    else:
                        print(f"Error: Function <{fname}> not found (Line {idx+1})")
                elif parsed[0] == 'if':
                    varname, value = parsed[1], parsed[2]
                    if self.variables.get(varname, None) == value:
                        idx += 1
                    else:
                        skip_stack.append("if")
                        idx += 1
                    continue
                elif parsed[0] == 'end':
                    idx += 1
                    continue
                elif parsed[0] == 'writeinput':
                    prompt = parsed[1]
                    self.last_input = get_input(prompt)
                elif parsed[0] == 'img':
                    url = parsed[1]
                    print(f"[Image: {url}]")
                elif parsed[0] == 'write_system_input':
                    print(self.last_input)
                elif parsed[0] == 'write_var':
                    var = parsed[1]
                    if var in self.variables:
                        print(self.variables[var])
                    else:
                        print(f"Error: Variable '{var}' not found (Line {idx+1})")
                elif parsed[0] == 'write_expr':
                    expr = parsed[1]
                    try:
                        result = self._evaluate_expression(expr)
                        print(result)
                    except Exception as e:
                        print(f"Error: {e} (Line {idx+1})")
                elif parsed[0] == 'write_literal':
                    val = parsed[1]
                    def var_sub(match):
                        v = match.group(1)
                        return str(self.variables.get(v, f"(Error: Var '{v}' not found)"))
                    print(re.sub(r'\(([a-zA-Z_][a-zA-Z0-9_]*)\)', var_sub, val))
                elif parsed[0] == 'var_assign_input':
                    var = parsed[1]
                    self.variables[var] = self.last_input
                elif parsed[0] == 'var_assign_expr':
                    var, expr = parsed[1], parsed[2]
                    try:
                        self.variables[var] = self._evaluate_expression(expr)
                    except Exception as e:
                        print(f"Error assigning to '{var}': {e} (Line {idx+1})")
                elif parsed[0] == 'var_assign_literal':
                    var, val = parsed[1], parsed[2]
                    self.variables[var] = val
                elif parsed[0] == 'error':
                    print(f"Error on line {idx+1}: Invalid syntax or unrecognized command: \"{parsed[1]}\"")
            except Exception as e:
                print(f"Error on line {idx+1}: {e}")
            idx += 1
    def interpret(self, code_line):
        self._run_s_code([code_line])
    def multiline(self, *code_lines):
        self._run_s_code(list(code_lines))

def display_help():
    print("""
S Language Commands:
  func <function_name>         Function definition. Ends with end. Call with <function_name> on a line.
  <function_name>              Calls a function previously defined.
  write <text>                 Prints literal text.
  write (variable_name)        Prints the value of a variable.
  write ((input))              Prints last input value.
  write (<expression>)         Prints result of arithmetic or string expr.
                               Operators: +, -, *, /, ++ (concatenation)
  writeinput <prompt>          Prompts for user input.
  variable_name <value>        Assigns a literal value.
  variable_name ((input))      Assigns last input to variable.
  variable_name (<expr>)       Assigns expr result to variable.
  img "image_url"              Prints image URL (CLI only).
  if var = "value" then ... end   Conditional block, executes code inside if var matches value.
  $                            Comments after $ are ignored.
""")
