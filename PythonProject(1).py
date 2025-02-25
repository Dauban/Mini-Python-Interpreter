#Authors- Daniel Cohen ID: 213509714, Gal Elhiani: 207233248, Or Adar: 305468506, Dmitri Shpak: 321371320

import ast

values = {}
temp_values = {}

# Supported functions
functions = {'len': lambda x: len(x), 'print': lambda *args: print(*args), 'max': lambda *args: max(*args), 'min': lambda *args: min(*args),
    'tuple': lambda x=None: tuple(x) if x is not None else (),
    'int': lambda x=None: int(x) if x is not None else 0,
    'float': lambda x=None: float(x) if x is not None else 0.0,
    'str': lambda x=None: str(x) if x is not None else '',
    'bool': lambda x=None: bool(x) if x is not None else False,
    'list': lambda x=None: list(x) if x is not None else [],
    'dict': lambda x=None: dict(x) if x is not None else {},
    'set': lambda x=None: set(x) if x is not None else set(),
    'sum' : lambda x: sum(x),
    'range': lambda x, y=None, z=None: range(x) if y is None and z is None else range(x, y) if z is None else range(x, y, z)}

# Helper recursive function to get the value of a node
def get_value(node):
    if isinstance(node, ast.Name):
        # If the value is a variable, return its value
        if node.id in temp_values:
            return temp_values.get(node.id, None)
        elif node.id in values:
            return values.get(node.id, None)
        elif node.id in functions:
            return functions.get(node.id, None)
        else:
            return None
    # Handle constants
    elif isinstance(node, ast.Constant):
        # If the value is a constant, return it directly
        return node.value
    # Handle lists
    elif isinstance(node, ast.List):
        return [get_value(item) for item in node.elts]
    # Handle tuples
    elif isinstance(node, ast.Tuple):
        return tuple(get_value(item) for item in node.elts)
    # Handle dictionaries
    elif isinstance(node, ast.Dict):
        return {get_value(key): get_value(value) for key, value in zip(node.keys, node.values)}
    # Handle sets
    elif isinstance(node, ast.Set):
        return {get_value(item) for item in node.elts}
    # Handle binary operations (+, -, *, /)
    elif isinstance(node, ast.BinOp):
        left_value = get_value(node.left)
        right_value = get_value(node.right)
        if isinstance(node.op, ast.Add):
            return left_value + right_value
        elif isinstance(node.op, ast.Mult):
            return left_value * right_value
        elif isinstance(node.op, ast.Sub):
            return left_value - right_value
        elif isinstance(node.op, ast.Div):
            return left_value / right_value
        elif isinstance(node.op, ast.Pow):
            return left_value ** right_value
        elif isinstance(node.op, ast.Mod):
            return left_value % right_value
    # Handle boolean operations (and, or)
    elif isinstance(node, ast.BoolOp):
        Lst_values = [get_value(value) for value in node.values]
        if isinstance(node.op, ast.And):
            return all(Lst_values)
        elif isinstance(node.op, ast.Or):
            return any(Lst_values)
    # Handle comparisons (==, !=, <, >)
    elif isinstance(node, ast.Compare):
        # We get the values of the nodes from the AST
        left_value = get_value(node.left)
        right_value = get_value(node.comparators[0])
        if isinstance(node.ops[0], ast.Eq):
            return left_value == right_value
        elif isinstance(node.ops[0], ast.NotEq):
            return left_value != right_value
        elif isinstance(node.ops[0], ast.Lt):
            return left_value < right_value
        elif isinstance(node.ops[0], ast.LtE):
            return left_value <= right_value
        elif isinstance(node.ops[0], ast.Gt):
            return left_value > right_value
        elif isinstance(node.ops[0], ast.GtE):
            return left_value >= right_value
    # Handle unary operations (negation, not)
    elif isinstance(node, ast.UnaryOp):
        value = get_value(node.operand)
        if isinstance(node.op, ast.USub):
            return -value
        elif isinstance(node.op, ast.Not):
            return not value
    # Handle attributes
    elif isinstance(node, ast.Attribute):
        obj = get_value(node.value)  # Get the object the attribute is accessed on
        attr_name = node.attr  # The name of the attribute being accessed
        if hasattr(obj, attr_name):
            attr = getattr(obj, attr_name)  # Get the actual attribute
            return attr  # Return the method itself (for later calls)
    # Handle subscript access (list[index])
    elif isinstance(node, ast.Subscript):
        obj = get_value(node.value)
        if obj is not None:
            index = get_value(node.slice)
            if index is not None:
                return obj[index]
    # Handle function calls
    elif isinstance(node, ast.Call):
        value = get_value(node.func)  # Extract function
        if value and callable(value):
            args = [get_value(arg) for arg in node.args]  # Get the given variables
            return value(*args)
    elif isinstance(node, ast.Expr):
        return get_value(node.value)
    # Handle other node types as needed
    else:
        return None

# Main function to process nodes
def main(child, in_func=False):  # in_func is a flag that will be used to check if a variable is a function
    # Handle assignment statements
    if isinstance(child, ast.Assign):
        for target in child.targets:
            if isinstance(target, ast.Name):
                if target.id in temp_values:
                    temp_values[target.id] = get_value(child.value)
                elif in_func:
                    temp_values[target.id] = get_value(child.value)
                else:
                    values[target.id] = get_value(child.value)
    # Handle augmented assign operations (+=, -=, *=, /=)
    elif isinstance(child, ast.AugAssign):
        target_name = child.target.id if isinstance(child.target, ast.Name) else None
        target_value = get_value(child.target)
        target_change = get_value(child.value)

        if isinstance(child.op, ast.Add):
            result = target_value + target_change
        elif isinstance(child.op, ast.Sub):
            result = target_value - target_change
        elif isinstance(child.op, ast.Mult):
            result = target_value * target_change
        elif isinstance(child.op, ast.Div):
            result = target_value / target_change
        if child.target.id in temp_values:
            temp_values[child.target.id] = result
        else:
            values[child.target.id] = result
    # Handle function calls
    elif isinstance(child, ast.Call):
        if not child:
            return None
        value = get_value(child.func)  # Extract function name
        if value and callable(value):
            args = [get_value(arg) for arg in child.args]
            return value(*args)
    # Handle expressions (obj.expr)
    elif isinstance(child, ast.Expr):
        get_value(child.value)
    # Handle if statements
    elif isinstance(child, ast.If):
        if get_value(child.test):
            for item in child.body:
                main(item)
        elif child.orelse:
            for item in child.orelse:
                main(item)
    # Handle while loop using helper function (main2)
    elif isinstance(child, ast.While):
        while get_value(child.test):
            main2(child)
    # Handle for loop
    elif isinstance(child, ast.For):
        iter_value = get_value(child.iter)

        # Check if the iterable is a dictionary
        if isinstance(iter_value, type({}.items())):
            for key, value in iter_value:
                # Assuming the target is a tuple (key, value)
                if isinstance(child.target, ast.Tuple):
                    temp_values[child.target.elts[0].id] = key
                    temp_values[child.target.elts[1].id] = value
                else:  # Handle other cases, e.g., just iterating over keys
                    temp_values[child.target.id] = key
                main2(child)
                if isinstance(child.target, ast.Tuple):
                    temp_values.pop(child.target.elts[0].id)
                    temp_values.pop(child.target.elts[1].id)
                else:
                    temp_values.pop(child.target.id)
        else:  # For other iterable types
            for item in iter_value:
                temp_values[child.target.id] = item
                main2(child)
                temp_values.pop(child.target.id)
    # Handle function definitions
    elif isinstance(child, ast.FunctionDef):
        local_variables = {}
        arg_names = [param.arg for param in child.args.args]
        default_values = [get_value(default) for default in child.args.defaults]

        # Calculate the number of parameters without defaults
        non_default_count = len(arg_names) - len(default_values)

        # Assign None to parameters without default values
        for name in arg_names[:non_default_count]:
            local_variables[name] = None

        # Assign actual default values to the remaining parameters
        for name, default in zip(arg_names[non_default_count:], default_values):
            local_variables[name] = default

        if in_func:  # If it's a function inside a function, save the outer variables
            outer_values = temp_values.copy()

        def function_body(*args):
            result = None
            diff = len(arg_names) - len(args)
            args_idx = 0
            for i, (variable, default) in enumerate(local_variables.items()):
                if diff > 0 and default != None:
                    temp_values[variable] = default
                    diff -= 1
                else:
                    temp_values[variable] = args[args_idx]
                    args_idx += 1
            if in_func:  # For functions inside functions, add variables from the outer function
                for variable, value in outer_values.items():
                    temp_values[variable] = value
            for item in child.body:
                main(item, True)  # process the body of the function
                if isinstance(item, ast.Return):  # Handle return statements
                    result = get_value(item.value)
            for variable in local_variables:
                temp_values.pop(variable)  # clean up local variables after execution
            return result
        functions[child.name] = function_body  # Add the function to the dictionary
    else:
        main2(child)  # Process the child nodes recursively

# Helper function for processing child nodes
def main2(node):
    for child in ast.iter_child_nodes(node):
        main(child)
