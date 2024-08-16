import re

class Token:
    def __init__(self, value_part, class_part, line_number):
        self.value_part = value_part
        self.class_part = class_part
        self.line_number = line_number

    def __repr__(self):
        return f"Token(value='{self.value_part}', type='{self.class_part}', line={self.line_number})"

def Validate_string(temp):
    # A: Set of characters that can be escaped with a backslash or used as is
    A = r"[\\|'|\"]"

    # B: Set of characters that represent special sequences and cannot occur without a backslash
    B = r"[bntro]"

    # C: Set of characters that do not require a backslash
    C = r"[@+]"

    # D: Set of alphabetic characters and underscores (a-z, A-Z, _)
    D = r"[a-zA-Z_]"

    char_const = rf"(\\{A}|\\{B}|{B}|{C}|{D})"

    strchar_pattern = rf"^\"({char_const})*\"$"
    number_pattern=r'^[0-9]+$|^[+-]?[0-9]*\.[0-9]+$'
    # number_pattern = r'^[+-]?(\d*\.\d+|\d+\.\d*|\d+)([eE][+-]?\d+)?$'
    identifier_pattern = r'[a-zA-Z]|^[a-zA-Z_][a-zA-Z0-9_]*[a-zA-Z0-9]$'
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
    keywords_list = {
        "class": "class",
        "public": "AM",  # AM=Access Modifier
        "private": "AM",
        "void": "void",
        "extends": "extends",
        "return": "return",
        "this": "this",
        "new": "new",
        "final": "final",
        "num": "DT",  # DT=Data Type
        "StrChar": "DT",
        "when": "when",
        "else": "else",
        "input": "input",
        "print": "print",
        "while": "while",
        "break": "break",
        "continue": "continue",
        "try": "try",
        "catch": "catch",
        "finally": "finally",
        "NOT": "NOT",
        "AND": "AND",
        "OR": "OR"
    }
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

def break_word(file, index):
    temp = ""
    punct_array = [",", ".", "[", "]", "{", "}", "(", ")", ";"]
    opr_array = ["*", "/", "%"]
    check_opr_array = ["+", "-", "=", ">", "<", "!"]
    log_opr_arr = ["AND", "OR", "NOT"]
    result = []
    
    while index < len(file):
        char = file[index]

        # Handle spaces and new lines
        if char.isspace():
            if temp:
                result.append(temp.strip())
                temp = ""
            if char == "\n":
                result.append(temp)
            index += 1
            continue

        # Handle comments
        if char == "#":
            if index + 1 < len(file) and file[index + 1] == "#":
                index += 2  # Skip the ##
                while index + 1 < len(file) and not (file[index] == "#" and file[index + 1] == "#"):
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
                result.append(temp.strip())
                temp = ""
            if char == "+" and index + 1 < len(file) and file[index + 1] == "+":
                result.append("++")
                index += 1
            elif char == "-" and index + 1 < len(file) and file[index + 1] == "-":
                result.append("--")
                index += 1
            elif char == "=" and index + 1 < len(file) and file[index + 1] == "=":
                result.append("==")
                index += 1
            elif char == "<" and index + 1 < len(file) and file[index + 1] == "=":
                result.append("<=")
                index += 1
            elif char == ">" and index + 1 < len(file) and file[index + 1] == "=":
                result.append(">=")
                index += 1
            elif char == "!" and index + 1 < len(file) and file[index + 1] == "=":
                result.append("!=")
                index += 1
            else:
                result.append(char)
        elif char in punct_array:
            if char == '.':
                # Check for previous and next parts around '.'
                prev_part = temp
                next_part = file[index + 1:].lstrip()
                prev_word = re.findall(r'\w+', prev_part)[-1] if re.findall(r'\w+', prev_part) else ''
                next_word = re.findall(r'\w+', next_part)[0] if re.findall(r'\w+', next_part) else ''

                # Check if the previous part is a number and the next part starts with a digit
                if prev_word.isdigit() and next_word.isdigit():
                    if '.' in temp:  # If there's already a dot in the temp, break the word
                        result.append(temp.strip())  # Add the current word to result
                        temp = '.'  # Start a new token with the dot
                    else:
                        temp += char  # Add the '.' to temp since it's part of a number
                else:
                    if temp:
                        result.append(temp.strip())
                        temp = ""
                    result.append(char)  # Treat the '.' as a punctuator
            else:
                if temp:
                    result.append(temp.strip())
                    temp = ""
                result.append(char)

        elif char == "\"":
            if temp and temp[-1] == "\"":
                result.append(temp.strip())
                temp = ""
            temp += char
        else:
            temp += char

        index += 1
    
    if temp:
        result.append(temp.strip())

    return result, index

# Example usage
with open("C:\\Users\\Excalibur\\Downloads\\Labs\\tcs\\file.txt", "r") as f:
    file = f.read()
index = 0
line_number=1
tokens, _ = break_word(file, index)
for token in tokens:
    if token == "":
        line_number += 1
    else:
        cp = Validate_string(token)  # Assuming Validate_string is defined
        t1 = Token(token, cp, line_number)
        print(t1)  # This will call __repr__ method automatically
break_word(file,0)
