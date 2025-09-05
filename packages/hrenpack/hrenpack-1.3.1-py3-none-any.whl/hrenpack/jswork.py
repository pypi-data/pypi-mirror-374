from hrenpack.listwork import dict_enumerate


class StringToJavascriptVariable:
    def __init__(self, name: str):
        self.name = name


class DictArg:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __str__(self):
        output = "{ "
        ln = len(self.kwargs)
        for i, key, value in dict_enumerate(self.kwargs.items()):
            output += f"{key}: {value}"
            if ln - i != 1:
                output += ', '
        output += ' }'
        return output


def arg_js(arg) -> str:
    if isinstance(arg, StringToJavascriptVariable):
        output = arg.name
    elif isinstance(arg, str):
        output = f'"{arg}"'
    elif isinstance(arg, (list, tuple, set)):
        output = str(list(arg))
    else:
        output = str(arg)
    return output


def js_function(func_name: str, *args):
    output = func_name + '('
    ln = len(args)
    for i, arg in enumerate(args):
        if isinstance(arg, StringToJavascriptVariable):
            output += arg.name
        elif isinstance(arg, str):
            output += f'"{arg}"'
        elif isinstance(arg, (list, tuple, set)):
            output += str(list(arg))
        elif isinstance(arg, dict):
            pass
        else:
            output += str(arg)
        if ln - i != 1:
            output += ', '
