class SlotsReadMixin:
    def __getitem__(self, item):
        if item in self.__slots__:
            return getattr(self, item)
        raise KeyError(item)


class SlotsMixin(SlotsReadMixin):
    def __setitem__(self, key, value):
        setattr(self, key, value)
