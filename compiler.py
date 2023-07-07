import re
import copy

numbers = re.compile(r"[0-9]")
alphabet = re.compile(r"[a-zA-Z]")

def tokenizer(input):
    tokens = []
    filtered_input = input.strip()
    position = 0

    while position < len(filtered_input):
        character = filtered_input[position]

        if character == "(":
            tokens.append({'type': 'left_parenthesis', 'value': '('})
            position += 1
        elif character == ")":
            tokens.append({'type': 'right_parenthesis', 'value': ')'})
            position += 1
        elif re.match(numbers, character):
            value = ""

            while position < len(filtered_input) and re.match(numbers, character):
                value += character
                position += 1

                if position < len(filtered_input):
                    character = filtered_input[position]

            tokens.append({'type': 'number', 'value': value})
        elif re.match(alphabet, character):
            value = ""

            while position < len(filtered_input) and re.match(alphabet, character):
                value += character
                position += 1

                if position < len(filtered_input):
                    character = filtered_input[position]

            tokens.append({'type': 'name', 'value': value})
        else:
            position += 1

    return tokens




def parser(tokens):
    current = 0

    def walk():
        nonlocal current

        if current >= len(tokens):
            return None

        token = tokens[current]
        print("Current token:", token)

        if token.get('type') == 'number':
            current += 1
            return {
                'type': 'NumberLiteral',
                'value': token.get('value')
            }

        if token.get('type') == 'left_parenthesis':
            current += 1
            token = tokens[current]
            node = {
                'type': 'CallExpression',
                'name': token.get('value'),
                'parameters': []
            }

            current += 1
            token = tokens[current]
            while token.get('type') != 'right_parenthesis':
                child_node = walk()
                if child_node is not None:
                    node['parameters'].append(child_node)
                else:
                    break  # Return if child_node is None
                token = tokens[current]

            current += 1
            return node

        if token.get('type') == 'name':
            current += 1
            return {
                'type': 'Identifier',
                'name': token.get('value')
            }

        raise TypeError(f"Unexpected token type: {token.get('type')}")

    ast = {
        'type': 'Program',
        'body': []
    }

    while current < len(tokens):
        ast['body'].append(walk())
    
    return ast


def traverser(ast, visitor):
    def traverseArray(array, parent):
        for child in array:
            traverseNode(child, parent)

    def traverseNode(node, parent):
        method = visitor.get(node['type'])
        if method:
            method(node, parent)
        elif node['type'] == 'Program':
            traverseArray(node['body'], node)
        elif node['type'] == 'CallExpression':
            traverseNode(node['callee'], node)
            traverseArray(node['arguments'], node)  # Add 'node' as the second argument
        elif node['type'] == 'NumberLiteral':
            0
        else:
            raise TypeError(node['type'])

    traverseNode(ast, None)


def transformer(ast):
    newAst = {
        'type': 'Program',
        'body': []
    }

    oldAst = ast
    ast = copy.deepcopy(oldAst)
    ast['_context'] = newAst.get('body')

    def CallExpressionTraverse(node, parent):
        expression = {
            'type': 'CallExpression',
            'callee': {
                'type': 'Identifier',
                'name': node['name']
            },
            'arguments': []
        }
        node['_context'] = parent['_context']  # Update this line

        # Store nested call expression references
        if parent['type'] != 'CallExpression':
            expression = {
                'type': 'ExpressionStatement',
                'expression': expression
            }
        
        # Store the expression in the context property
        parent['_context'].append(expression)


    def NumberLiteralTraverse(node, parent):
        parent['_context'].append({
            'type': 'NumberLiteral',
            'value': node['value']
        })

    traverser(ast, {
        'NumberLiteral': NumberLiteralTraverse,
        'CallExpression': CallExpressionTraverse
    })

    return newAst


def codeGenerator(node):
    if node['type'] == 'Program':
        return '\n'.join(codeGenerator(child) for child in node['body'])
    elif node['type'] == 'Identifier':
        return node['name']
    elif node['type'] == 'NumberLiteral':
        return node['value']
    elif node['type'] == 'ExpressionStatement':
        expression = codeGenerator(node['expression'])
        return f"{expression};"
    elif node['type'] == 'CallExpression':
        callee = codeGenerator(node['callee'])
        arguments = ', '.join(codeGenerator(arg) for arg in node['arguments'])
        return f"{callee}({arguments})"
    else:
        raise TypeError(node['type'])





def compiler(input):
    tokens = tokenizer(input)
    ast = parser(tokens)
    newAst = transformer(ast)
    output = codeGenerator(newAst)
    return output


def main():
    # Test
    input = "(add 2 (subtract 4 2))"
    output = compiler(input)
    print(output)


if __name__ == "__main__":
    main()
