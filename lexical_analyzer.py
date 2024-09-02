import re

class Token:  # token class
    def __init__(self, value_part, class_part, line_number):
        self.value_part = value_part
        self.class_part = class_part
        self.line_number = line_number

    def __repr__(self):  # return values for printing
        return f"Token(value='{self.value_part}', type='{self.class_part}', line={self.line_number})"

def Validate_string(temp):  # validate function
    A = r"[\\|'|\"]"  # can not occur without /
    B = r"[bntro]"  # can and can not occur with backslash /
    C = r"[@+.]"  # do not require a backslash
    D = r"[a-zA-Z\s+_]"
    char_const = rf"(\\{A}|\\{B}|{B}|{C}|{D})"
    # string and character RE
    strchar_pattern = rf"^\"({char_const})*\"$"
    # number RE include int and float
    number_pattern = r'^[0-9]+$|^[+-]?[0-9]*\.[0-9]+$'
    # identifier RE start with alphabet or underscore and end with alpha or digit
    identifier_pattern = r'[a-zA-Z]|^[a-zA-Z_][a-zA-Z0-9_]*[a-zA-Z0-9]$'
    # dic for operators
    operator_list = {
        "+": "PM",  # PM=Plus Minus
        "-": "PM",
        "*": "MDM",  # MDM=Multiply Divide Modulo
        "/": "MDM",
        "%": "MDM",
        "<": "ROP",  # ROP=Relational Operator
        ">": "ROP",
        "<=": "ROP",
        ">=": "ROP",
        "!=": "ROP",
        "==": "ROP",
        "++": "Inc_Dec",
        "--": "Inc_Dec",
        "=": "="
    }
    # dict for keywords
    keywords_list = {
        "class": "class",
        "universal": "AM",  # AM=Access Modifier
        "restricted": "AM",
        "void": "void",
        "ext": "extends",
        "ret": "return",
        "this": "this",
        "new": "new",
        "final": "final",
        "num": "DT",  # DT=Data Type
        "StrChar": "DT",
        "when": "when",
        "otherwise": "else",
        "input": "input",
        "display": "print",
        "while": "while",
        "brk": "break",
        "cont": "continue",
        "try": "try",
        "catch": "catch",
        "finally": "finally",
        "NOT": "NOT",
        "AND": "AND",
        "OR": "OR"
    }
    # dict for punctuators
    punctuator_list = {
        "{": "{",
        "}": "}",
        "(": "(",
        ")": ")",
        "[": "[",
        "]": "]",
        ".": ".",
        ",": ",",
        ";": ";"
    }
    # matching temp with all scenarios
    if re.match(strchar_pattern, temp):
        return "StrChar"
    elif re.match(number_pattern, temp):
        return "num"
    elif temp in operator_list:
        return operator_list.get(temp)
    elif temp in punctuator_list:
        return punctuator_list.get(temp)
    elif temp in keywords_list:
        return keywords_list.get(temp)
    elif re.match(identifier_pattern, temp):
        return "ID"
    else:
        return "Invalid Lexeme"

def break_word(file):
    temp = ""  # to store a complete word
    punct_array = [",", ".", "[", "]", "{", "}", "(", ")", ";"]
    opr_array = ["*", "/", "%"]
    check_opr_array = ["+", "-", "=", ">", "<", "!"]
    line_number = 1
    
    index = 0
    while index < len(file):  # iterate until the file ends
        char = file[index]  # reading file char by char

        # Handle spaces and new lines
        if char.isspace():
            if temp:
                cp = Validate_string(temp.strip())
                yield Token(temp.strip(), cp, line_number)
                temp = ""
            if char == "\n":
                line_number += 1
            index += 1
            continue

        # Handle comments
        if char == "#":
            if index + 1 < len(file) and file[index + 1] == "#":  # check for multiline comment
                index += 2  # Skip the ##
                while index + 1 < len(file) and not (file[index] == "#" and file[index + 1] == "#"):
                    if file[index] == "\n":
                        line_number += 1
                    index += 1
                if index + 1 < len(file) and file[index] == "#" and file[index + 1] == "#":
                    index += 2  # Skip the ##
                continue
            else:
                while index < len(file) and file[index] != "\n":
                    index += 1
                continue

        # Handle operators
        if char in opr_array or char in check_opr_array:
            if temp:
                cp = Validate_string(temp.strip())
                yield Token(temp.strip(), cp, line_number)
                temp = ""
            if char == "+" and index + 1 < len(file) and file[index + 1] == "+":
                cp = Validate_string("++")
                yield Token("++", cp, line_number)  # increment operator
                index += 1
            elif char == "-" and index + 1 < len(file) and file[index + 1] == "-":
                cp = Validate_string("--")
                yield Token("--", cp, line_number)  # decrement operator
                index += 1
            elif char == "=" and index + 1 < len(file) and file[index + 1] == "=":
                cp = Validate_string("==")
                yield Token("==", cp , line_number)
                index += 1
            elif char == "<" and index + 1 < len(file) and file[index + 1] == "=":
                cp = Validate_string("<=")
                yield Token("<=", cp, line_number)
                index += 1
            elif char == ">" and index + 1 < len(file) and file[index + 1] == "=":
                cp = Validate_string(">=")
                yield Token(">=", cp, line_number)
                index += 1
            elif char == "!" and index + 1 < len(file) and file[index + 1] == "=":
                cp = Validate_string("!=")
                yield Token("!=", cp, line_number)
                index += 1
            else:
                yield Token(char, Validate_string(char), line_number)
        elif char in punct_array:
            if temp:
                cp = Validate_string(temp.strip())
                yield Token(temp.strip(), cp, line_number)
                temp = ""
            yield Token(char, char, line_number)
        # handle string or char
        elif char == "\"":
            if temp:
                cp = Validate_string(temp.strip())
                yield Token(temp.strip(), cp, line_number)
                temp = ""
            quote_type = char  # store "
            temp += char
            index += 1
            start_line = line_number
            while index < len(file):
                char = file[index]
                temp += char
                if char == "\\" and index + 1 < len(file):  # Handle escape sequences
                    temp += file[index + 1]
                    index += 1
                elif char == quote_type:  # Found the closing quote
                    break
                if char == "\n":
                    line_number += 1
                index += 1
            cp = Validate_string(temp.strip())
            yield Token(temp.strip(), cp, start_line)
            temp = ""
        # not a break character
        else:
            temp += char

        index += 1  # increment index
    
    if temp:
        cp = Validate_string(temp.strip())
        yield Token(temp.strip(), cp, line_number)

# file reading
with open("C:\\Users\\Excalibur\\Downloads\\Labs\\tcs\\file.txt", "r") as f:
    file = f.read()

# Tokenize and print tokens
for token in break_word(file):
    print(token)
