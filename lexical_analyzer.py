import re

class Token:  # token class
    def __init__(self, value_part, class_part, line_number):
        self.value_part = value_part
        self.class_part = class_part
        self.line_number = line_number

    def __repr__(self):  # return values for printing
        return f"Token('{self.value_part}', '{self.class_part}', {self.line_number})"

def Validate_string(temp):  # validate function
    A = r"[\\|'|\"]"  # can not occur without /
    B = r"[bntro]"  # can and can not occur with backslash /
    C = r"[@+.]"  # do not require a backslash
    D = r"[a-zA-Z\s+_]"
    char_const = rf"(\\{A}|\\{B}|{B}|{C}|{D})"
    strchar_pattern = rf"^\"({char_const})*\"$"
    number_pattern = r'^[0-9]+$|^[+-]?[0-9]*\.[0-9]+$'
    identifier_pattern = r'[a-zA-Z]|^[a-zA-Z_][a-zA-Z0-9_]*[a-zA-Z0-9]$'
    operator_list = {
        "+": "PM", "-": "PM", "*": "MDM", "/": "MDM", "%": "MDM",
        "<": "ROP", ">": "ROP", "<=": "ROP", ">=": "ROP", "!=": "ROP", "==": "ROP",
        "++": "Inc_Dec", "--": "Inc_Dec", "=": "="
    }
    keywords_list = {
        "class": "class", "universal": "AM", "restricted": "AM", "void": "void", 
        "extends": "extends", "return": "return", "this": "this", "new": "new", "final": "final",
        "num": "DT", "StrChar": "DT", "when": "when", "otherwise": "otherwise", "input": "input", 
        "display": "display", "while": "while", "brk": "break", "cont": "continue", 
        "try": "try", "catch": "catch", "finally": "finally", "NOT": "NOT", "AND": "AND", "OR": "OR"
    }
    punctuator_list = {
        "{": "{", "}": "}", "(": "(", ")": ")", "[": "[", "]": "]", ".": ".", ",": ",", ";": ";"
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

def break_word(file):
    tokens = []  # List to store tokens
    temp = ""
    punct_array = [",", ".", "[", "]", "{", "}", "(", ")", ";"]
    opr_array = ["*", "/", "%"]
    check_opr_array = ["+", "-", "=", ">", "<", "!"]
    line_number = 1
    
    index = 0
    while index < len(file):  # iterate until the file ends
        char = file[index]  # reading file char by char

        if char.isspace():
            if temp:
                cp = Validate_string(temp.strip())
                tokens.append(Token(temp.strip(), cp, line_number))
                temp = ""
            if char == "\n":
                line_number += 1
            index += 1
            continue

        if char == "#":
            if index + 1 < len(file) and file[index + 1] == "#":
                index += 2
                while index + 1 < len(file) and not (file[index] == "#" and file[index + 1] == "#"):
                    if file[index] == "\n":
                        line_number += 1
                    index += 1
                if index + 1 < len(file) and file[index] == "#" and file[index + 1] == "#":
                    index += 2
                continue
            else:
                while index < len(file) and file[index] != "\n":
                    index += 1
                continue

        if char in opr_array or char in check_opr_array:
            if temp:
                cp = Validate_string(temp.strip())
                tokens.append(Token(temp.strip(), cp, line_number))
                temp = ""
            if char == "+" and index + 1 < len(file) and file[index + 1] == "+":
                cp = Validate_string("++")
                tokens.append(Token("++", cp, line_number))
                index += 1
            elif char == "-" and index + 1 < len(file) and file[index + 1] == "-":
                cp = Validate_string("--")
                tokens.append(Token("--", cp, line_number))
                index += 1
            elif char == "=" and index + 1 < len(file) and file[index + 1] == "=":
                cp = Validate_string("==")
                tokens.append(Token("==", cp , line_number))
                index += 1
            elif char == "<" and index + 1 < len(file) and file[index + 1] == "=":
                cp = Validate_string("<=")
                tokens.append(Token("<=", cp, line_number))
                index += 1
            elif char == ">" and index + 1 < len(file) and file[index + 1] == "=":
                cp = Validate_string(">=")
                tokens.append(Token(">=", cp, line_number))
                index += 1
            elif char == "!" and index + 1 < len(file) and file[index + 1] == "=":
                cp = Validate_string("!=")
                tokens.append(Token("!=", cp, line_number))
                index += 1
            else:
                tokens.append(Token(char, Validate_string(char), line_number))
        elif char in punct_array:
            if char == '.':
                # Check for previous and next parts around '.'
                prev_part = temp
                next_part = file[index + 1:].lstrip()
                prev_word = re.findall(r'\w+', prev_part)[-1] if re.findall(r'\w+', prev_part) else ''
                next_word = re.findall(r'\w+', next_part)[0] if re.findall(r'\w+', next_part) else ''

                # Check if the previous part is a number and the next part starts with a digit
                if prev_word.isdigit() and next_word.isdigit():
                    if '.' in temp:  # If there's already a dot in temp, break the word
                        if temp.strip():
                            cp = Validate_string(temp.strip())
                            tokens.append(Token(temp.strip(), cp, line_number))
                        temp = '.'  # Start a new token with the dot
                    else:
                        temp += char  # Add the '.' to temp since it's part of a number
                else:
                    if temp:
                        cp = Validate_string(temp.strip())
                        tokens.append(Token(temp.strip(), cp, line_number))
                        temp = ""
                    tokens.append(Token(char, Validate_string(char), line_number))  # Treat the '.' as a punctuator
            else:
                if temp:
                    cp = Validate_string(temp.strip())
                    tokens.append(Token(temp.strip(), cp, line_number))
                    temp = ""
                tokens.append(Token(char, Validate_string(char), line_number))  # Add the punctuation token

        elif char == "\"":
            if temp:
                cp = Validate_string(temp.strip())
                tokens.append(Token(temp.strip(), cp, line_number))
                temp = ""
            quote_type = char
            temp += char
            index += 1
            start_line = line_number
            while index < len(file):
                char = file[index]
                temp += char
                if char == "\\" and index + 1 < len(file):
                    temp += file[index + 1]
                    index += 1
                elif char == quote_type:
                    break
                if char == "\n":
                    line_number += 1
                index += 1
            cp = Validate_string(temp.strip())
            tokens.append(Token(temp.strip(), cp, start_line))
            temp = ""
        else:
            temp += char

        index += 1  # increment index

    if temp:
        cp = Validate_string(temp.strip())
        tokens.append(Token(temp.strip(), cp, line_number))

    return tokens

# file reading
with open("file.txt", "r") as f:
    file = f.read()

# Tokenize
tokens = break_word(file)

for i in range (len(tokens)):
    print(tokens[i])
