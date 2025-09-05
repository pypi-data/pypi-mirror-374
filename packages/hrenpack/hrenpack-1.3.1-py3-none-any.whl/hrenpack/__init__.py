import os
from typing import Union, Optional, Literal
from hrenpack.classes import range_plus
from hrenpack.strwork import randstr
from hrenpack.listwork import split_list


def literal_add(base, *args):
    return Union[base, Literal[*args]]


si = Union[int, str]
IntStr = si
NullStr = Optional[str]
integer, string, boolean = int, str, bool
ColorTyping = Union[tuple[int, int, int], list[int, int, int], tuple[int, int, int, float], list[int, int, int, float]]
FivePointScale = Literal[*range_plus(5)]
TenPointScale = Literal[*range_plus(10)]
ZeroFivePointScale = literal_add(FivePointScale, 0)
ZeroTenPointScale = literal_add(TenPointScale, 0)
PRINT_MESSAGE = True

if PRINT_MESSAGE:
    print("Hrenpack")
    print("(c) Mag Ilyas DOMA, 2024. Distributed under a BSD license. Распостраняется с лицензией BSD.")

__version__ = '1.3.0'


def print_message_set(value: bool = False):
    global PRINT_MESSAGE
    PRINT_MESSAGE = value


def notwork():
    print("Данная функция находится в разработке и пока не работает")


def sts(word):
    stars = '*' * len(word)
    return stars


def of_utf8(filename, mode='r'):
    file = open(filename, mode, encoding='utf-8')
    return file


def write_a(path, data):
    file = open(path, 'a', encoding='utf-8')
    file.write(f'{str(data)}\n')
    file.close()


def write(path, text):
    file = open(path, 'w', encoding='utf-8')
    file.write(str(text))
    file.close()


def null():
    pass


def switch(variable, case: dict, default=null):
    for key in case:
        func = case[key]
        if variable == key:
            func()
            break
    else:
        default()


def bincode_generator(length: int, isInt: bool = False):
    bincode = ''
    for i in range(length):
        bincode = bincode + randstr(0, 1)
    return int(bincode) if isInt else bincode


def show_help(path_of_document: str, path: str = ''):
    def return_text(pod):
        document = of_utf8(path_of_document)
        data = document.read()
        document.close()
        return data

    text = return_text(path_of_document)

    if path:
        if not os.path.isfile(path):
            raise FileExistsError(
                f'[WinError 183] Невозможно создать новый файл, так как он уже существует: {path}')
        else:
            file = of_utf8(path, 'w')
            file.write(text)
            file.close()
    else:
        print(text)


def switch_return(variable, case: dict, default=None):
    for key in case:
        value = case[key]
        if variable == value:
            output = value
            break
    else:
        output = default
    return output


def string_error(error: Exception):
    return str(error)


def who_called_me():
    import inspect
    current_frame = inspect.currentframe()
    calling_frame = current_frame.f_back
    return inspect.getfile(calling_frame)


def get_resource(path: str):
    """Вызывает ресурс hrenpack. Работает только, если вызывать внутри пакета hrenpack
    :arg path: Принимаются только пути, относительные \\hrenpack\\resources\\
    """
    python_path = who_called_me()
    python_list = python_path.split('\\')
    if 'hrenpack' not in python_list:
        raise NotADirectoryError
    hrenpack_index = python_list.index('hrenpack')
    return '\\'.join(python_list[:hrenpack_index + 1]) + '\\resources\\' + path


def one_return(count: int, value=None):
    if count == 1:
        return value
    else:
        output = list()
        for i in range(count):
            output.append(value)
        return tuple(output)


none_tuple = lambda count: one_return(count)
tuple0 = lambda count: one_return(count, 0)
str_tuple = lambda count: one_return(count, '')


def module_is_installed(module_name: str):
    try:
        __import__(module_name)
    except ImportError:
        return False
    else:
        return True


if module_is_installed('django'):
    from hrenpack.framework.django import apps
