import os, sys, logging
from typing import Optional
from functools import wraps
from hrenpack.listwork import key_in_dict


def confirm(inp_text: str = "Вы уверены, что хотите выполнить эту программу?"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = input(inp_text + "\nВведите y, д или 1, если да, или n, н или 0, если нет\n")
            while True:
                if result in ('y', 'Y', "д", "Д", "1"):
                    return func(*args, **kwargs)
                elif result in ('n', 'N', "н", "Н", "0"):
                    break
                else:
                    result = input(inp_text + "\nВведите y, д или 1, если да, или n, н или 0, если нет\n")

        return wrapper
    return decorator


def non_print(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with open(os.devnull, 'w') as devnull:
            old_stdout = sys.stdout
            sys.stdout = devnull
            try:
                f = func(*args, **kwargs)
            finally:
                sys.stdout = old_stdout
                return f
    return wrapper


def args_kwargs(**kwargs):
    args_name = kwargs.get('args_name', 'args')
    kwargs_name = kwargs.get('kwargs_name', 'kwargs')
    copy_args = kwargs.get('copy_args', True)
    copy_kwargs = kwargs.get('copy_kwargs', True)
    del_kwargs = kwargs.get('del_kwargs', True)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **key_args):
            if key_in_dict(key_args, args_name) and copy_args:
                args = [*args, *key_args[args_name]]
                if del_kwargs:
                    del key_args[args_name]
            if key_in_dict(key_args, kwargs_name) and copy_kwargs:
                key_args = {**key_args, **key_args[kwargs_name]}
                if del_kwargs:
                    del key_args[kwargs_name]
            return func(*args, **key_args)
        return wrapper
    return decorator


def debug_logging(start_message: str = '', end_message: str = ''):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if start_message:
                logging.debug(start_message)
            output = func(*args, **kwargs)
            if end_message:
                logging.debug(end_message)
            return output
        return wrapper
    return decorator


def method(func):
    return func


def multi_decorator(*decorators):
    """Декораторы применяются слева направо"""
    def decorator(func):
        for dec in decorators:
            func = dec(func)
        return func
    return decorator


# def super_method(*super_args, super_var_name__: Optional[str] = None, all_args__: bool = False, **super_kwargs):
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             name = func.__name__
#             code = f'super().{name}(*super_args, **super_kwargs)'
#             if all_args__:
#                 code = code.replace('super_', '')
#             if super_var_name__:
#                 code = super_var_name__ + ' = ' + code
#             print(code)
#             exec(code)
#             return func(*args, **kwargs)
#         return wrapper
#     return decorator


if __name__ == '__main__':
    @confirm
    def test():
        print('Hello, world!')


    test()
