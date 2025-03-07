
import ast
import os
import jedi      
from pathlib import Path
from src.utils.config import logger
from typing import List


def find_python_files(root: str):
    """
    Yield all .py files under the given root directory, 
    skipping any directories named 'tests' (case-insensitive).
    """
    root_path = Path(root)
    for path in root_path.rglob("*.py"):
        # Use pathlib to inspect parts of the path:
        if any(part.lower() == "tests" for part in path.parts):
            continue
        if path.name == "__init__.py":
            continue
        yield path


def parse_source(source: str, filename: str):
    """
    Parse Python source code into an AST.
    """
    try:
        return ast.parse(source, filename=filename)
    except SyntaxError as e:
        logger.error(f"Syntax error in {filename}: {e}")
        raise

def get_parent_id(definition):
    try:
        parent = definition.parent()
        if parent is not None and parent.type in ('function', 'class'):
            parent_id = parent.full_name
        else:
            parent_id = None
    except Exception as e:
        print(f"Error getting parent for {definition.name}: {e}")
        parent_id = None
    finally:
        return parent, parent_id

def get_definitions_info(defs,tree, source, file_path):
    definitions = {}

    for d in defs:
        # Consider only functions, methods and classes
        if d.type in ('function', 'class') and d.full_name:

            # Get parent id for nested relationships
            parent, parent_id = get_parent_id(d)

            # Determine if the function is actually a method
            node_type = ("method" if ((d.type == "function") and (parent.type == "class"))
                         else d.type)

            # Extract source code of the definition
            code_segment = ""
            docstring = ""
            inherits_from = []
            # Walk tree until definition is found with ast
            if tree is not None:
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == d.name and node.lineno == d.line:
                        code_segment = ast.get_source_segment(source, node)
                        docstring = d.docstring()

                        # Capture inheritance information for classes
                        add_node_inheritance(node=node, 
                                            inheritance_list=inherits_from)
                        
                        break
            
            # For methods, include class name in its name
            # node_name = ".".join(d.full_name.split(".")[-2]) if node_type == "method" else d.name
            node_name = d.name
            if node_type == "method":
                node_name = ".".join([parent.name, d.name])
            
            # Save the extracted information in the dictionary
            definitions[d.full_name] = {
                'id': d.full_name,
                'name': node_name,
                'type': node_type,
                'file': file_path,
                'line': d.line,
                'code': code_segment,
                'docstring': docstring,
                'definition': d,
                'inherits_from': inherits_from,
                'parent_id': parent_id
            }

    return definitions

def add_node_inheritance(node: ast.ClassDef, inheritance_list: List) -> None:
    if isinstance(node, ast.ClassDef):
        for base in node.bases:
            if isinstance(base, ast.Name):
                inheritance_list.append(base.id)
            elif isinstance(base, ast.Attribute):
                inheritance_list.append(base.attr)


def resolve_base_class_names(script, base_class_names, lineno, col_offset):
    """Resolve the full names of base classes using Jedi."""
    resolved_base_classes = []

    for base_class_name in base_class_names:
        definitions = script.goto(lineno, col_offset, follow_imports=True)

        for definition in definitions:
            if definition.name == base_class_name:
                resolved_base_classes.append(definition.full_name)
                break

    return resolved_base_classes



def find_call_nodes(tree):
    """Find all call nodes in the AST."""
    call_nodes = []
    for node in ast.walk(tree):

        if isinstance(node, ast.Call):
            call_nodes.append(node)

    return call_nodes

def get_class_context(script, lineno, col_offset):
    """Get the class context for a given position in the source code."""
    # Get the context at the given position
    context = script.get_context(lineno, col_offset)
    
    # Walk up all the context hierarchy to find the class
    while context:
        if context.type == 'class':
            return context
        context = context.parent()
    return None

def get_full_name_of_call(script, call_node):
    """Get the full name of a call node, handling `self`."""

    # Handle self method calls
    if (
        isinstance(call_node.func, ast.Attribute)
        and isinstance(call_node.func.value, ast.Name)
        and call_node.func.value.id == 'self'
    ):

        class_context = get_class_context(script, call_node.lineno, call_node.col_offset) 

        if class_context:
            # Construct the full name of the method
            class_name = class_context.full_name
            method_name = call_node.func.attr
            return f"{class_name}.{method_name}"
        else:
            return None
        
    # normal calls
    else:
        definitions = script.goto(call_node.lineno, call_node.col_offset, follow_imports=True)

        if definitions:
            return definitions[0].full_name

    return None

def get_enclosing_definition(script, lineno, col_offset):
    """
    Use Jedi to determine the innermost definition (function or class)
    that encloses the given line and column position in the file.
    This is used to figure out which definition a function call belongs to.
    """
    try:
        context = script.get_context(line=lineno, column=col_offset)
        # Return the context if it represents a function or class definition
        if context and context.type in ('function', 'class'):
            return context
    except Exception:
        return None
    return None

def get_call_pair_id(call_nodes_list, script):
    call_pairs_list = []

    for call_node in call_nodes_list:
        caller_context = get_enclosing_definition(script, call_node.lineno, call_node.col_offset) # Context calling the function
        if not caller_context:
            continue

        called_function_id = get_full_name_of_call(script, call_node)

        call_pairs_list.append({"caller_id":caller_context.full_name, "candidate_id":called_function_id})
    
    return call_pairs_list


def get_definitions_relationships(source, tree, file_path, project):
    """
    Extract definitions (functions, classes, and methods) and relationships (nested in, calls, and inheritance) from a file using Jedi.
    Returns a dictionary mapping a unique ID to another dictionary containing:
      - id: Unique identifier for the definition
      - name: The name of the function, class, or method
      - type: Type ('class', 'function', or 'method')
      - file: File path where the definition is found
      - line: Line number of the definition
      - code: Source code segment for the definition
    """
    definitions = {}

    # Use Jedi to extract all definitions in the source code
    script = jedi.Script(source, path=file_path, project=project)
    defs = script.get_names(all_scopes=True, definitions=True, references=False)
    
    definitions = get_definitions_info(defs=defs, tree=tree, source=source, file_path=file_path)

    # Resolve inheritance relationships
    for def_id, info in definitions.items():
        if info['type'] == 'class' and info['inherits_from']:
            # Find the AST node for the class definition
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == info['name'] and node.lineno == info['line']:
                    # Extract the correct lineno and col_offset for the base class
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            base_class_name = base.id
                            lineno = base.lineno
                            col_offset = base.col_offset
                        elif isinstance(base, ast.Attribute):
                            base_class_name = base.attr
                            lineno = base.lineno
                            col_offset = base.col_offset
                        else:
                            continue

                        # Resolve the base class name
                        resolved_base_classes = resolve_base_class_names(script, [base_class_name], lineno, col_offset)
                        info['inherits_from'].extend(resolved_base_classes)
                    break

    call_ast_nodes = find_call_nodes(tree)

    call_pairs_list = get_call_pair_id(call_ast_nodes, script)   

    return definitions, call_pairs_list