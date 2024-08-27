import re

class Token:  # token class
    def __init__(self, value_part, class_part, line_number):
        self.value_part = value_part
        self.class_part = class_part
        self.line_number = line_number

    def __repr__(self):  #return values for printing
        return f"Token(value='{self.value_part}', type='{self.class_part}', line={self.line_number})"

def Validate_string(temp): #validate function
    A = r"[\\|'|\"]" #  can not occur without / 
    B = r"[bntro]"   # can and can not occur with backslash /
    C = r"[@+.]"      #do not require a backslash
    D = r"[a-zA-Z\s+_]"
    char_const = rf"(\\{A}|\\{B}|{B}|{C}|{D})"
    #string and character RE
    strchar_pattern = rf"^\"({char_const})*\"$"
    #number RE include int and float 
    number_pattern=r'^[0-9]+$|^[+-]?[0-9]*\.[0-9]+$'
    #identifier RE start with alphabet or underscore and end with alpha or digit
    identifier_pattern = r'[a-zA-Z]|^[a-zA-Z_][a-zA-Z0-9_]*[a-zA-Z0-9]$'
    #dic for operators
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
    #dict for punctuator
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
    #matching temp with all scenarios
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
#function for breaking words from file
def break_word(file, index):
    temp = ""        #to store a complete word
    punct_array = [",", ".", "[", "]", "{", "}", "(", ")", ";"]
    opr_array = ["*", "/", "%"]
    check_opr_array = ["+", "-", "=", ">", "<", "!"]
    log_opr_arr = ["AND", "OR", "NOT"]
    result = []      #to store the broken words
    
    while index < len(file):     #iterate until the file ends
        char = file[index]       #reading file char by char

        # Handle spaces and new lines
        if char.isspace():
            if temp:
                result.append(temp.strip())    #strip removes spaces tabs newlines etc
                temp = ""
            if char == "\n":
                result.append(temp)        # to keep track of line change
            index += 1
            continue

        # Handle comments
        if char == "#":
            if index + 1 < len(file) and file[index + 1] == "#":   #check for multiline comment
                index += 2  # if ## is found move index by 2 (Skip the ##)
                # iterate through the file until the ## is found(indicating multi line comment is ended)
                while index + 1 < len(file) and not (file[index] == "#" and file[index + 1] == "#"):
                    index += 1
                if index + 1 < len(file) and file[index] == "#" and file[index + 1] == "#":
                    index += 2  # Skip the ##
                result.append(temp)
                continue
            else:
                #single line comment(until new line starts)
                while index < len(file) and file[index] != "\n":
                    index += 1
                continue
        
        # Handle operators
        if char in opr_array or char in check_opr_array:
            if temp:
                result.append(temp.strip())
                temp = ""
            if char == "+" and index + 1 < len(file) and file[index + 1] == "+":
                result.append("++")   #if there is increment oper 
                index += 1
            elif char == "-" and index + 1 < len(file) and file[index + 1] == "-":
                result.append("--")   #if there is decrement oper 
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
        # handle string or char
        elif char == "\"":
            if temp:
                result.append(temp.strip())
                temp = ""
            quote_type = char       #store "
            temp += char
            index += 1
            #iterate through the file 
            while index < len(file):
                char = file[index]
                temp += char
                if char == "\\" and index + 1 < len(file):  # Handle escape sequences
                    temp += file[index + 1]
                    index += 1
                elif char == quote_type:  # Found the closing quote
                    break
                index += 1
           
            result.append(temp.strip())
            temp = ""
        #not a break character
        else:
            temp += char

        index += 1  #increment index
    
    if temp:
        result.append(temp.strip())    #append temp

    return result, index

with open("C:\\Users\\Excalibur\\Downloads\\Labs\\tcs\\file.txt", "r") as f:
    file = f.read()
index = 0
line_number=1
tokens, _ = break_word(file, index)
#iterate through the array return by break_word function
for token in tokens:
    if token.startswith("##") or token.endswith("##"):
        print(token)
        line_number += 2
    elif token == "":
        line_number += 1
    elif "\n" in token:
        line_number += 1
        cp = Validate_string(token)
        t1 = Token(token, cp, line_number)
        print(f"Token(value='{t1.value_part}' type='{t1.class_part}' line='{t1.line_number-1}','{t1.line_number}')")
    else:
        cp = Validate_string(token)
        t1 = Token(token, cp, line_number)
        print(t1)
 
