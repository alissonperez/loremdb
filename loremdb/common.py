version = "0.1.0"   # Application version


class Signal(object):
    """
    A "Observer" implementation.
    Note: ONLY works with class methods.

    Example:
        from loremdb.common import Signal

        class Observed(object):
            def __init__(self):
                self.changed = Signal()
                self.val = 0

            def increment(self):
                self.val += 1
                self.changed()


        class Observer(object):
            def __init__(self, observed):
                self._observed = observed
                self._observed.changed.register(self.change_callback)

            def change_callback(self):
                print "Signal received... Value now is "
                + str(self._observed.val)


        observed = Observed()
        observer = Observer(observed)

        observed.increment()    # Output: "Signal received... Value now is 1"
    """

    def __init__(self):
        self._slots = {}

    def __call__(self, *args, **kwargs):
        for key, func in self._slots.iteritems():
            func.im_func(func.im_self, *args, **kwargs)

    def register(self, slot):
        self._slots[self._get_key(slot)] = slot

    def unregister(self, slot):
        key = self._get_key(slot)
        if key in self._slots:
            del self._slots[key]

    def _get_key(self, slot):
        return (slot.im_func, id(slot.im_self))