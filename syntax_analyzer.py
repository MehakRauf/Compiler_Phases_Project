import json
from lexical_analyzer import tokens  # Assuming tokens is a list of Token objects

class Token:
    def __init__(self, value_part, class_part, line_number):
        self.value_part = value_part
        self.class_part = class_part
        self.line_number = line_number

    def __repr__(self):
        return f"Token(value='{self.value_part}', type='{self.class_part}', line={self.line_number})"

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_index = 0
        self.current_token = tokens[0] if tokens else None
    
    def eat(self, token_type):
        if self.current_token and self.current_token.class_part == token_type:
            self.current_index += 1
            if self.current_index < len(self.tokens):
                self.current_token = self.tokens[self.current_index]
            else:
                self.current_token = None
        else:
            raise Exception(f"Expected token type {token_type}, but got {self.current_token}")

    def parse_program(self):
        statements = []
        while self.current_index < len(self.tokens):
            statements.append(self.parse_statement())
        return statements

    def parse_statement(self):
        # Check for 'break' statement
        if self.current_token.value_part == "break":
            self.eat("break")
            return {"type": "break"}

        # Check for 'continue' statement
        elif self.current_token.value_part == "continue":
            self.eat("continue")
            return {"type": "continue"}
        
        # Check for 'return' statement
        elif self.current_token.value_part == "return":
            return self.parse_return()
        
        # Check for identifier (ID)
        if self.current_token.class_part == "ID":
            if self.current_index + 1 < len(self.tokens):
                next_token = self.tokens[self.current_index + 1]
                
                if next_token.class_part == "(":
                    # Function call
                    return self.parse_funcCalling()
                elif next_token.class_part == "ID":
                    # Object creation
                    return self.parse_objects()
                elif next_token.class_part == ".":
                    # Object method calling
                    return self.parse_objCalling()
                
            # Default to initialization
            return self.parse_initialization()

        # Check for 'number' declaration
        elif self.current_token.class_part == "num":
            return self.parse_declaration()

        # Check for 'when' conditional block
        elif self.current_token.value_part == "when":
            return self.parse_conditional()

        # Check for 'while' loop
        elif self.current_token.value_part == "while":
            return self.parse_loop()

        # Check for 'try' block
        elif self.current_token.value_part == "try":
            return self.parse_tryCatch()

        # Check for class/function declarations
        elif self.current_token.class_part in ["AM", "abstract"]:
            if self.current_index + 1 < len(self.tokens):
                next_token = self.tokens[self.current_index + 1]
                if next_token.value_part == "class":
                    if self.current_index + 2 < len(self.tokens) and self.tokens[self.current_index + 2].class_part == "ID":
                        if self.current_index + 3 < len(self.tokens) and self.tokens[self.current_index + 3].value_part == "extends":
                            # Child class with inheritance
                            return self.parse_childClass()
                    return self.parse_class()  # Regular class declaration
                elif next_token.class_part in ["void", "ID", "DT"]:
                    # Function declaration
                    return self.parse_function()

        # Check for abstract class definition
        elif self.current_token.value_part == "abstract":
            return self.parse_class()

        # Check for 'display' 
        elif self.current_token.value_part == "display":
            return self.parse_print()

        # Check for 'input'
        elif self.current_token.value_part == "input":
            return self.parse_input()
        
        raise Exception(f"Unexpected token: {self.current_token}")

    def parse_declaration(self):
        self.eat("num")  # Expecting 'num' keyword
        identifier = self.current_token.value_part
        self.eat("ID")    # Expecting an identifier
        return {'type': 'declaration', 'name': identifier}
    
    def parse_initialization(self):
        identifier = self.current_token.value_part
        self.eat("ID")    # Expecting an identifier
        self.eat("=")      # Expecting '='
        value = self.parse_expression()  # Parse the expression after '='
        return {"type": "initialization", 'name': identifier, "=": "=", 'value': value}
    
    def parse_expression(self):
        left = self.parse_term()
        
        while self.current_token and self.current_token.class_part in ["ROP", "PM", "MDM", "Inc_Dec", "="]:
            operator = self.current_token.value_part
            self.eat(self.current_token.class_part)  # Consume the operator
            right = self.parse_term()  # Get the second part of the expression
            left = {"type": "condition", 'left': left, 'operator': operator, 'right': right}
        
        return left
    
    def parse_return(self):
        self.eat("return")  # Consume the 'return' keyword
        
        if self.current_index + 1 < len(self.tokens):
            next_token = self.tokens[self.current_index]
            if next_token.class_part in ["StrChar", "ID", "num"]:
                self.eat(next_token.class_part)  # Consume the value being returned
                return {"type": "return", "value_type": next_token.class_part}
        
        return {"type": "return"}  # Return None if there's no value
    
    def parse_term(self):
        if self.current_token.class_part == "ID":
            identifier = self.current_token.value_part
            self.eat("ID")
            return {'type': 'identifier', 'value': identifier}
        elif self.current_token.class_part == "num":
            value = self.current_token.value_part
            self.eat("num")
            return {'type': 'number', 'value': value}
        else:
            raise Exception(f"Unexpected token in term: {self.current_token}")

    def parse_conditional(self):
        self.eat("when")     # Expecting 'when'
        self.eat("(")        # Expecting '('
        condition = self.parse_expression()  # Parse the condition
        self.eat(")")        # Expecting ')'
        true_block = self.parse_block()      # Parse the true block
        false_block = None
        if self.current_token and self.current_token.value_part == "otherwise":
            self.eat("otherwise")
            false_block = self.parse_block()  # Parse the false block
        
        return {'type': 'conditional', 'condition': condition, 'true_block': true_block, 'false_block': false_block}

    def parse_loop(self):
        self.eat("while")  # Expecting 'while'
        self.eat("(")       # Expecting '('
        condition = self.parse_expression()  # Parse the loop condition
        self.eat(")")       # Expecting ')'
        block = self.parse_block()            # Parse the loop body
        return {'type': 'loop', 'condition': condition, 'block': block}
    
    def parse_class(self):
        if self.current_token.class_part in ["universal", "abstract", "restricted" , "AM"]:
            self.eat(self.current_token.class_part)  # Consume modifier if present
        self.eat("class")  # Match 'class' keyword
        class_name = self.is_identifier()
        block = self.parse_block()
        return {"type": "class", "class_name": class_name, "block": block}

    def parse_print(self):
        self.eat("display")  # Match the "display" keyword
        self.eat("(")        # Match the opening parenthesis
        display = None
        
        if self.current_token.class_part == "ID":
            display = self.is_identifier()
        elif self.current_token.class_part == "num":
            display = self.is_number()
        elif self.current_token.class_part == "StrChar":
            display = self.is_string()
        else:
            raise SyntaxError("Expected identifier, number, or string in display statement")

        self.eat(")")  # Match the closing parenthesis
        return {"type": "print", "value": display}

    def parse_input(self):
        self.eat("input")  # Match the "input" keyword
        self.eat("(")      # Match the opening parenthesis
        
        if self.current_token.class_part == "StrChar":
            display = self.is_string()  # Parse the identifier
        else:
            display = None  # Handle blank input

        self.eat(")")  # Match the closing parenthesis
        return {"type": "input", "value": display}
    
    def parse_function(self):
        if self.current_token.class_part in ["AM", "abstract"]:
            AM = self.current_token.value_part
            self.eat(self.current_token.class_part)  # Consume modifier

        if self.current_token.class_part in ["void", "DT"]:
            return_type = self.eat(self.current_token.class_part)  # Consume return type
        else:
            raise Exception("Expected return type got"  , self.current_token.class_part)

        identifier = self.is_identifier()
        self.eat("(")

        parameters = []
        if self.current_token.class_part != ")":  # Check if there are any parameters
            while True:
                # Parse the parameter type
                if self.current_token.class_part in ["DT"]:
                    param_type = self.current_token.value_part
                    self.eat(self.current_token.class_part)  # Consume the type
                else:
                    raise Exception(f"Expected parameter type but found: {self.current_token.class_part}")

                # Parse parameter name (identifier)
                if self.current_token.class_part == "ID":
                    param_name = self.is_identifier()  # Consume identifier for parameter name
                else:
                    raise Exception("Expected parameter identifier")

                # Add the parameter as a tuple of (type, name) to the list
                parameters.append((param_type, param_name))

                # Check for more parameters
                if self.current_token.class_part == ",":
                    self.eat(",")  # Consume the comma
                    parameters.append(",")
                elif self.current_token.class_part == ")":
                    break  # End of parameters list

        self.eat(")")  # Match closing parenthesis

        # Assuming we parse the function body or block after the parameters
        block = self.parse_block()  # This will handle the function body
        return {
            "type": "function",
            "return_type": return_type,
            "name": identifier,
            "parameters": parameters,
            "block": block,
            "access_modifier": AM
        }

    def parse_tryCatch(self):
        self.eat("try")
        try_block = self.parse_block()  # Changed variable name for clarity
        
        self.eat("catch")
        self.eat("(")
        identifier = self.is_identifier()  
        id = self.is_identifier()
        self.eat(")")
        
        catch_block = self.parse_block()  
        final_block = None

        if(self.current_token.class_part == "finally"):
            self.eat("finally")
            final_block = self.parse_block() 

        # Return a structured representation of the try-catch
        return {
            "type": "try",
            "{":"{",
            "try_block": try_block,
            "}":"}",
            "type":"catch",
            "(":"(",
            "catch_identifier": identifier,
            ")":")",
            "{":"{",
            "catch_block": catch_block,
            "}":"}",
            "type":"finally",
            "{":"{",
            "final_block": final_block,
            "}":"}"
        }
    
    def is_identifier(self):
        identifier = self.current_token.value_part
        self.eat("ID")  # Consume identifier token
        return identifier

    def is_string(self):
        string = self.current_token.value_part
        self.eat("StrChar")  # Consume string token
        return string

    def is_number(self):
        number = self.current_token.value_part
        self.eat("DT")  # Consume number token
        return number
    
    def parse_block(self):
        """Parse a block of statements."""
        self.eat("{")       # Expecting '{'
        statements = []
        while self.current_token and self.current_token.value_part != "}":
            statements.append(self.parse_statement())
        
        self.eat("}")       # Expecting '}'
        return {'type': 'block', "{":"{",'statements': statements,"}":"}"}
    
    def parse_childClass(self):
         # This assumes self.eat() verifies and consumes the next token.
        if self.current_token.class_part in ["AM"]:
            AM= self.current_token.value_part
            self.eat(self.current_token.class_part)
        self.eat("class")  # Match 'class' keyword
        # Parse the class name, assuming self.identifier() will handle extracting a valid identifier
        class_name = self.is_identifier()
        self.eat("extends")
        parent_class=self.is_identifier()
        # Parse the body or block inside the class definition
        block = self.parse_block()  # Assuming parse_block() is a method that handles parsing statements inside the class
        # Return the class name and the parsed block as part of the parsed result
        return {"type": "childClass","AM":AM,"child_class": class_name, "extends":"extends","parent_class":parent_class,"block": block}

    def parse_objects(self):
        # Parse the class name
        class_name = self.is_identifier()  
        
        object_name = self.is_identifier()  
        
        # Check for '='
        if self.current_token.value_part != '=':
            raise Exception(f"Expected '=', got {self.current_token.value_part}.")
        self.eat("=")  # Match the = operator
       
        # Check for 'new'
        if self.current_token.value_part != 'new':
            raise Exception(f"Expected 'new', got {self.current_token.value_part}.")
        self.eat("new")  # Match the new keyword

        # Parse the class name again
        new_class_name = self.is_identifier()  # Should capture 'Stu'
        
        # Check that both class names match
        if new_class_name != class_name:
            raise Exception(f"Class name mismatch: expected '{class_name}', got '{new_class_name}'.")

        # Match the opening parenthesis
        self.eat("(")  # Match the opening parenthesis
        
        # Parse arguments if they exist
        parameters = []
        if not self.is_blank():  # If there are arguments
            parameters = self.parse_arguments()  # Call method to parse arguments

        # Match the closing parenthesis
        self.eat(")")  # Match the closing parenthesis

        # Return a dictionary representing the object creation
        return {
            "type" : "objectCreation",
            "object_name": object_name,  # The object being created
            "class_name": class_name,     # The class from which the object is created
            "parameters": parameters       # The constructor arguments (if any)
        }

    def parse_objCalling(self):
        # Parse the object name
        object_name = self.is_identifier()  # e.g., 's1'
        self.eat(".")  # Match the dot operator for method access
        
        # Parse the method name
        method_name = self.is_identifier()  # e.g., 'details'
        
        # Print the current token for debugging (can be removed later)
        print(self.current_token)

        # Parse arguments if there is a function call
        parameters = []
        if not self.is_blank():  # If there are arguments
            self.eat("(")  # Match the opening parenthesis
            if not self.is_blank():
                parameters = self.parse_arguments()  # Call method to parse arguments
            self.eat(")")  # Match the closing parenthesis

        # Return the parsed object method call
        return {
            "type" : "objectCreation",
            "object_name": object_name,  # The object being accessed
            "method_name": method_name,  # The method being called
            "parameters": parameters,     # The arguments to the method call
        }

    def parse_parameter(self):
        # This method parses an individual expression; handle literals and identifiers
        if self.is_identifier():
            return self.is_identifier()  # Return the identifier
        
        if self.is_literal():  # Check if the current token is a literal
            return self.is_string()  # Return the literal value

        raise Exception(f"Unexpected token: {self.current_token.value_part}")

    def parse_arguments(self):
        arguments = []
        
        while True:
            # Parse each argument
            argument = self.parse_parameter()  # Parse a single expression (identifier/literal)
            arguments.append(argument)  # Add the argument to the list

            # Check for a comma to continue parsing more arguments
            if self.current_token.value_part == ',':
                self.eat(",")  # Match the comma
            else:
                break  # Exit the loop if there are no more arguments

        return arguments
    
    def is_blank(self):
        if(self.current_token==")"):
            return 0
        return 1

    def peek(self):
        if self.current_index + 1 < len(self.tokens):
            return self.tokens[self.current_index + 1].value_part
        return None
    
# Initialize and run parser on token list
parser = Parser(tokens)
ast = parser.parse_program()

# Print and visualize the AST
print(json.dumps(ast, indent=4))
