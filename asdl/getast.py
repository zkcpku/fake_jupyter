# coding=utf-8

import ast
from asdl import *
import astor

asdl_text = open('py3_asdl.simplified.txt').read()
grammar = ASDLGrammar.from_text(asdl_text)


def python_ast_to_asdl_ast(py_ast_node, grammar):
    # node should be composite
    py_node_name = type(py_ast_node).__name__
    # assert py_node_name.startswith('_ast.')

    production = grammar.get_prod_by_ctr_name(py_node_name)

    fields = []
    for field in production.fields:
        field_value = getattr(py_ast_node, field.name)
        asdl_field = RealizedField(field)
        if field.cardinality == 'single' or field.cardinality == 'optional':
            if field_value is not None:  # sometimes it could be 0
                if grammar.is_composite_type(field.type):
                    child_node = python_ast_to_asdl_ast(field_value, grammar)
                    asdl_field.add_value(child_node)
                else:
                    asdl_field.add_value(str(field_value))
        # field with multiple cardinality
        elif field_value is not None:
                if grammar.is_composite_type(field.type):
                    for val in field_value:
                        child_node = python_ast_to_asdl_ast(val, grammar)
                        asdl_field.add_value(child_node)
                else:
                    for val in field_value:
                        asdl_field.add_value(str(val))

        fields.append(asdl_field)

    asdl_node = AbstractSyntaxTree(production, realized_fields=fields)

    return asdl_node


def asdl_ast_to_python_ast(asdl_ast_node, grammar):
    py_node_type = getattr(sys.modules['ast'], asdl_ast_node.production.constructor.name)
    py_ast_node = py_node_type()

    for field in asdl_ast_node.fields:
        # for composite node
        field_value = None
        if grammar.is_composite_type(field.type):
            if field.value and field.cardinality == 'multiple':
                field_value = []
                for val in field.value:
                    node = asdl_ast_to_python_ast(val, grammar)
                    field_value.append(node)
            elif field.value and field.cardinality in ('single', 'optional'):
                field_value = asdl_ast_to_python_ast(field.value, grammar)
        else:
            # for primitive node, note that primitive field may have `None` value
            if field.value is not None:
                if field.type.name == 'object':
                    if '.' in field.value or 'e' in field.value:
                        field_value = float(field.value)
                    elif isint(field.value):
                        field_value = int(field.value)
                    else:
                        raise ValueError('cannot convert [%s] to float or int' % field.value)
                elif field.type.name == 'int':
                    field_value = int(field.value)
                else:
                    field_value = field.value

            # FIXME: hack! if int? is missing value in ImportFrom(identifier? module, alias* names, int? level), fill with 0
            elif field.name == 'level':
                field_value = 0

        # must set unused fields to default value...
        if field_value is None and field.cardinality == 'multiple':
            field_value = list()

        setattr(py_ast_node, field.name, field_value)

    return py_ast_node

def to_dict(node,add_list):
    if type(node) == type(" "):
        add_list.append({'name':node,'children':[]})
        return
    this_dict = {'name':node.production.constructor.name,'children':[]}
    add_list.append(this_dict)
    for field in node.fields:
        if field.value is not None:
            for val_node in field.as_value_list:
                if isinstance(field.type, ASDLCompositeType):
                    to_dict(val_node,this_dict['children'])
                else:
                    to_dict(str(val_node),this_dict['children'])    

def asdl2dict(node):
    rst_list = []
    to_dict(node,rst_list)
    return rst_list[0]

def get_ast_dict(py_code):
    py_ast = ast.parse(py_code)
    # asdl_ast = python_ast_to_asdl_ast(py_ast.body[0], grammar)
    asdl_asts = [python_ast_to_asdl_ast(e, grammar) for e in py_ast.body]
    # rst = asdl2dict(asdl_ast)
    rsts = [asdl2dict(e) for e in asdl_asts]

    return {'name':'module','children':rsts}



if __name__ == '__main__':
    # read in the grammar specification of Python 2.7, defined in ASDL
    # asdl_text = open('py3_asdl.simplified.txt').read()
    # grammar = ASDLGrammar.from_text(asdl_text)

    py_code = """pandas.read('file.csv', nrows=100)"""
    py_code = '''
for i in range(10):
    print("hello world")
'''
    print(get_ast_dict(py_code))

    # # get the (domain-specific) python AST of the example Python code snippet
    # py_ast = ast.parse(py_code)

    # # convert the python AST into general-purpose ASDL AST used by tranX
    # asdl_ast = python_ast_to_asdl_ast(py_ast.body[0], grammar)
    # print('String representation of the ASDL AST: \n%s' % asdl_ast.to_string())
    # print('Size of the AST: %d' % asdl_ast.size)

    # # we can also convert the ASDL AST back into Python AST
    # py_ast_reconstructed = asdl_ast_to_python_ast(asdl_ast, grammar)

    # src1 = astor.to_source(py_ast).strip()
    # src2 = astor.to_source(py_ast_reconstructed).strip()

    # print(asdl_ast.fields)

    # assert src1 == src2  == "pandas.read('file.csv', nrows=100)"
