class Struct(object):
    def __init__(self, dictionary):
        """
        Simple helper class to "convert" dictionaries into property containers.

        Usge:
        In [1]: d = {'foo': 34, 'bar': 19}
        In [2]: s = Struct(d)
        In [3]: s
                <__main__.Struct at 0x7fda49cf11c0>
        In [4]: s.foo
                34
        In [5]: s.bar
                19
        In [6]: s.bar = 23
        In [7]: s.bar
                23
        In [8]: s.woohooo = 23
        In [9]: s.woohooo
                23
        """
        self.__dict__.update(dictionary)

        for k, v in dictionary.items():
            if isinstance(v, dict):
                self.__dict__[k] = Struct(v)

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    @property
    def dictionary(self):
        return self.__dict__
