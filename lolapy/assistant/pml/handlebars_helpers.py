

import json
from pybars import Compiler


def get_handlebars_compiler():
    compiler = Compiler()
    return compiler


def get_helpers():
    return {
        'if_equals': if_equals,
        'if_not_equals': if_not_equals,
        'json': json_helper,
        'json_pretty': json_pretty,
        'json_pretty_no_escaping': json_pretty_no_escaping,
        'key_value': key_value
    }

def if_equals(this, arg1, arg2, options):
    if arg1 == arg2:
        return options['fn'](this)
    else:
        return options['inverse'](this)

def if_not_equals(this, arg1, arg2, options):
    if arg1 != arg2:
        return options['fn'](this)
    else:
        return options['inverse'](this)

def json_helper(this, context):
    return json.dumps(context)

def json_pretty(this, context):
    return json.dumps(context, indent=2)

def json_pretty_no_escaping(this, context):
    return json.dumps(context, indent=2)

def key_value(this, context):
    output = ''
    for key in context:
        output += f'{key}: {context[key]}\n'
    return output