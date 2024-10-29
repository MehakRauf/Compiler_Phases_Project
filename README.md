# Compiler Project

This project implements a simple compiler with three main phases: **Lexical Analysis**, **Syntax Analysis**, and **Semantic Analysis**. Each phase is responsible for transforming source code into a structured representation and ensuring it follows the correct rules. The compiler code is organized to provide a clear flow from raw text input to meaningful output.

## Project Structure

## 1. Lexical Analysis

**Purpose**: To break down the raw source code into a list of **tokens**.

### How It Works
- The **lexical analyzer** reads the source code and identifies tokens like keywords, operators, and identifiers.
- Each token is represented by a `Token` class, with attributes like type and value.
- The output of this phase is a list of tokens, which the syntax analyzer will use.

### Files
- `lexical_analyzer.py`: Contains the main logic for breaking down source code into tokens.
- `file.txt`: Contains the source code.

## 2. Syntax Analysis

**Purpose**: Organize tokens into a parse tree following predefined grammar rules.

### How It Works
- The syntax analyzer (parser) takes the list of tokens and arranges them based on grammar rules.
- It builds a parse tree that represents the structure of the code.
- The Parser class includes methods for parsing statements, expressions, function calls, loops, and other language constructs.

### Files
- `syntax_analyzer.py`: Contains parsing logic using Token and Parser classes.

## 3. Semantic Analysis

**Purpose**: Ensure the code is meaningful and consistent.

### How It Works
- The semantic analyzer checks for valid variable types, function definitions, scopes, and other context-dependent rules.
- This phase detects issues like type mismatches, undeclared variables, and function misuse.

### Files
- `syntax_analyzer.py`: Implements type-checking and other semantic validation logic.

## Future Improvements
- Error Reporting: Enhance error messages to pinpoint exact line and character positions.
- Optimization: Implement code optimization in the semantic phase.
- Intermediate Code Generation: Add a phase to generate an intermediate representation of the code.

## Note
- This compiler project is a simplified implementation intended primarily for educational purposes in understanding basic compiler construction phases mainly focusing on the frontend/analytical phase.






