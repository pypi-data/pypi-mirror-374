class AutoSuperMeta(type):
    def __new__(cls, name, bases, namespace, auto_super_methods=None):
        methods_from_arg = auto_super_methods or []

        methods_from_attr = namespace.get('__auto_super_methods__', [])

        all_auto_methods = list(set(methods_from_arg + methods_from_attr))

        for method_name in all_auto_methods:
            if method_name in namespace and callable(namespace[method_name]):
                pass

        return super().__new__(cls, name, bases, namespace)
