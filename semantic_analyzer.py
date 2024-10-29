class SemanticAnalyzer:
    def __init__(self, ast):
        self.ast = ast  # Abstract syntax tree
        self.symbol_table = {}  # Store declared variables and their types
        self.functions = {}  # Store declared functions
        self.classes = {}  # Store declared classes
        self.current_scope = None  # Track the current scope

    def analyze(self):
        ## check the complete ast
        for statement in self.ast:
            self.analyze_statement(statement, inherited=None)
            
    ## check each statement
    def analyze_statement(self, statement, inherited):
        if "type" not in statement:
            raise Exception("Unknown statement type")

        if statement["type"] == "variable_declaration":
            return self.analyze_variable_declaration(statement, inherited)
        elif statement["type"] == "variable_initialization":
            return self.analyze_variable_initialization(statement, inherited)
        elif statement["type"] == "class":
            return self.analyze_class(statement, inherited)
        elif statement["type"] == "when":
            return self.analyze_conditional(statement, inherited)
        elif statement["type"] == "function_call":
            return self.analyze_function_call(statement, inherited)
        elif statement["type"] == "function_declaration":
            return self.analyze_function_declaration(statement, inherited)
        elif statement["type"] == "while":
            return self.analyze_loop(statement, inherited)
        elif statement["type"] == "try":
            return self.analyze_try_catch(statement, inherited)
        elif statement["type"] == "object_declare":
            return self.analyze_object_declare(statement, inherited)
        elif statement["type"] == "expression":
            return self.analyze_expression(statement, inherited)
        elif statement["type"] == "object_calling":
            return self.analyze_objects_calling(statement, inherited)
        elif statement["type"] == "input":
            return self.analyze_input(statement, inherited)
        elif statement["type"] == "print":
            return self.analyze_print(statement, inherited)
        elif statement["type"] == "child_Class":
            return self.analyze_child_class(statement, inherited)


    def analyze_variable_declaration(self, statement, inherited):
        var_name = statement['name']
        
        # Check if the variable is already declared (cannot redeclare)
        if var_name in self.symbol_table:
            raise Exception(f"Variable '{var_name}' is already declared.")

        # Determine the type, it can be 'num' or 'StrChar'
        var_type = inherited if inherited else statement.get('data_type', 'num')  # Default to 'num' if not provided

        if var_type not in ['num', 'StrChar']:
            raise Exception(f"Unsupported variable type '{var_type}' for variable '{var_name}'. Allowed types: 'num', 'StrChar'.")

        # Store the variable in the symbol table with its type
        self.symbol_table[var_name] = {'type': var_type}
        statement['attributes'] = {'type': var_type}

        return var_type  

    def analyze_variable_initialization(self, statement, inherited):
        var_name = statement['name']
        # cannot use without declaring
        if var_name not in self.symbol_table:
            raise Exception(f"Variable '{var_name}' used without declaration.")

        value_type = self.analyze_expression(statement['value'], inherited)
        return value_type

    def analyze_expression(self, expression, inherited):
        if isinstance(expression, dict) and "ID" in expression:
            var_name = expression["ID"]
            # cannot use without declaration
            if var_name not in self.symbol_table:
                raise Exception(f"Variable '{var_name}' used without declaration.")
            expression['attributes'] = {'type': self.symbol_table[var_name]['type']}
            return self.symbol_table[var_name]['type']  

        elif isinstance(expression, dict) and "value" in expression:
            expression['attributes'] = {'type': 'literal'}
            return 'literal'  

        elif isinstance(expression, dict):
            left_type = self.analyze_expression(expression['left'], inherited)
            right_type = self.analyze_expression(expression['right'], inherited)
            return left_type  

    def analyze_function_declaration(self, statement, inherited):
        func_name = statement["name"]
        # cannot redeclare
        if func_name in self.functions:
            raise Exception(f"Function '{func_name}' is already declared.")

        # Store function signature
        params = statement.get("arguments", [])
        return_type = statement.get("return_type", "void")

        self.functions[func_name] = {
            "parameters": params,
            "return_type": return_type
        }

        # Analyze function body
        self.analyze_block(statement['body'], inherited=return_type)
        return return_type  

    def analyze_conditional(self, statement, inherited):
        condition_type = self.analyze_expression(statement['condition'], inherited)
        self.analyze_block(statement['true_block'], inherited)
        if 'otherwise_block' in statement:
            self.analyze_block(statement['otherwise_block'], inherited)
        return condition_type  

    def analyze_function_call(self, statement, inherited):
        func_name = statement["name"]
        # cannot call if not defined
        if func_name not in self.functions:
            raise Exception(f"Function '{func_name}' is called but not defined.")
        expected_params = self.functions[func_name]["parameters"]
        actual_args = statement["arguments"]
        if len(expected_params) != len(actual_args):
            raise Exception(f"Function '{func_name}' expects {len(expected_params)} arguments, but got {len(actual_args)}.")

        # Analyze each argument
        for arg in actual_args:
            self.analyze_expression(arg, inherited)

        statement['attributes'] = {'called_function': func_name, 'arguments': actual_args}
        return self.functions[func_name]['return_type']  
    
    def analyze_objects_calling(self, statement, inherited):
        object_name = statement["object"]
        method_name = statement["method"]

        # cannot call if not defined
        if object_name not in self.symbol_table:
            raise Exception(f"Object '{object_name}' is used without declaration.")

        if method_name not in self.symbol_table[object_name]["methods"]:
            raise Exception(f"Method '{method_name}' does not exist in object '{object_name}'.")

        statement['attributes'] = {'object': object_name, 'method': method_name}
        return self.symbol_table[object_name]["methods"][method_name]["return_type"]  

    def analyze_input(self, statement, inherited):
        var_name = statement["variable"]
        # cannot call if not defined
        if var_name not in self.symbol_table:
            raise Exception(f"Input variable '{var_name}' is used without declaration.")
        # update the table
        statement['attributes'] = {'input_variable': var_name}
        return self.symbol_table[var_name]['type'] 
    
    def analyze_print(self, statement, inherited):
        var_name = statement["variable"]
        if var_name not in self.symbol_table:
            raise Exception(f"Prnum variable '{var_name}' is used without declaration.")
        statement['attributes'] = {'prnum_variable': var_name}
        return self.symbol_table[var_name]['type']  

    def analyze_class(self, statement, inherited):
        class_name = statement['class_name']
        if class_name in self.classes:
            raise Exception(f"Class '{class_name}' is already declared.")
        self.classes[class_name] = statement
        statement['attributes'] = {'class_name': class_name}

        # Analyze class body
        self.analyze_block(statement['block'], inherited)
        return 'class'  

    def analyze_object_declare(self, statement,inherited):
        class_name = statement["class_name"]
        
        # Check if the class is declared
        if class_name not in self.classes:
            raise Exception(f"Class '{class_name}' is not declared.")
        
        # If there are arguments, analyze them
        if "arguments" in statement:
            arguments = statement["arguments"]
            if "constructor" in self.classes[class_name]:
                expected_params = self.classes[class_name]["constructor"]
                if len(arguments) != len(expected_params):
                    raise Exception(f"Class '{class_name}' constructor expects {len(expected_params)} arguments, but got {len(arguments)}.")
                for arg, expected in zip(arguments, expected_params):
                    self.analyze_expression(arg)  # Analyze each argument
            
        # If the object creation is valid, store its attributes
        statement["attributes"] = {"class_name": class_name}

    def analyze_child_class(self, statement, inherited):
        # check the names
        child_class_name = statement['child_class_name']
        parent_class_name = statement['parent_class_name']

        if child_class_name in self.classes:
            raise Exception(f"Class '{child_class_name}' is already declared.")

        # parent doesn't exist error
        if parent_class_name not in self.classes:
            raise Exception(f"Parent class '{parent_class_name}' does not exist.")

        self.classes[child_class_name] = statement
        statement['attributes'] = {'child_class_name': child_class_name, 'parent_class_name': parent_class_name}

        if 'block' in statement:
            self.analyze_block(statement['block'], inherited)

        return 'child_class'  

    def analyze_loop(self, statement, inherited):
        # check the condition
        condition_type = self.analyze_expression(statement['condition'], inherited)
        self.analyze_block(statement['block'], inherited)
        return condition_type  

    def analyze_try_catch(self, statement, inherited):
        self.analyze_block(statement['try_block'], inherited)
        self.analyze_block(statement['catch_block'], inherited)
        if 'final_block' in statement:
            self.analyze_block(statement['final_block'], inherited)
        return 'try_catch'  

    def analyze_block(self, block, inherited):
        # check all the statements int he block
        for stmt in block['statements']:
            self.analyze_statement(stmt, inherited)

    # print the final output
    def print_attributed_ast(self):
        import json
        print(json.dumps(self.ast, indent=2))

# AST as input
ast = [
    {
        "type": "variable_declaration",
        "name": "x",
        "value": {"type": "value", "value": 10}
    },
    {
        "type": "class",
        "class_name": "MyClass",
        "block": {
            "statements": []
        }
    },
    {
        "type": "when",
        "condition": {"type": "ID", "ID": "x"},
        "true_block": {
            "statements": []
        },
        "otherwise_block": {
            "statements": []
        }
    },
    {
        "type": "function_declaration",
        "name": "myFunction",
        "arguments": [
            {"name": "param1", "type": "num"}
        ],
        "return_type": "void",
        "body": {
            "statements": []
        }
    },
    {
        "type": "function_call",
        "name": "myFunction",
        "arguments": [
            {"type": "value", "value": 5}
        ]
    },
    {
        "type": "while",
        "condition": {"type": "value", "value": 1},
        "block": {
            "statements": []
        }
    },
    {
        "type": "try",
        "try_block": {
            "statements": []
        },
        "catch_block": {
            "statements": []
        }
    },
    {
    "type": "object_declare",
    "class_name": "MyClass",
    "arguments": [
        {"type": "value", "value": 10},  
        {"type": "value", "value": "example"}
    ]
}
]

analyzer = SemanticAnalyzer(ast)
try:
    analyzer.analyze()
    print("Semantic analysis passed!")
    analyzer.print_attributed_ast()  # Print the attributed AST
except Exception as e:
    print(f"Semantic analysis error: {e}")
