

class RestrictedDict(dict):

    def __init__(self, value_validator=None, key_validator=None, iterable=None):
        super().__init__()
        if not value_validator:
            self._validate_value = lambda value: True
        else:
            if not callable(value_validator):
                raise TypeError("value_validator should be a callable or None")
            self._validate_value = value_validator
        if not key_validator:
            self._validate_key = lambda key: True
        else:
            if not callable(key_validator):
                raise TypeError("key_validator should be a callable or None")
            self._validate_key = key_validator
        if iterable:
            self.update(iterable)

    
    def __setitem__(self, key, value):
        if not self._validate_key(key):
            raise ValueError("Invalid key type, need %s but get %s" % ((t.__name__ for t in self._key_types), type(key)))
        if not self._validate_value(value):
            raise ValueError("Invalid value type, need %s but get %s" % ((t.__name__ for t in self._types), type(value)))
        return super().__setitem__(key, value)

    def can_merge(self, _dict):
        return isinstance(_dict, dict) and all([self._validate_key(k) and self._validate_value(v) for k, v in _dict])

    def trim(self, _dict):
        """
        trim dictionary to fit a form like self
        """
        return { k : v for k, v in _dict if self._validate_key(k) and self._validate_value(v) }

    def update(self, d, trim=False):
        if trim:
            d = self.trim(d)
        if not self.can_merge(d):
            raise ValueError("Cannot update dict because there are invalid keys or values in %s" % str(d))
        return super().update(d)


class TypeRestrictedDict(RestrictedDict):

    def __init__(self, value_types=None, key_types=None, iterable=None):
        """
        @var: acceptable_types: Types that can be a value of this dict
        @var: key_types: Types that can be a key of this dict
        """
        self._types = (tuple(value_types) if not isinstance(value_types, type) else (value_types, )) if value_types else None
        self._key_types = (tuple(key_types) if not isinstance(key_types, type) else (key_types, )) if key_types else None
        super(TypeRestrictedDict, self).__init__(
            key_validator=lambda key: isinstance(key, self._key_types) if self._key_types else True,
            value_validator=lambda value: isinstance(value, self._types) if self._types else True
        )

    @property
    def types(self):
        return self._types

    @property
    def key_types(self):
        return self._key_types


class RestrictedList(list):
    
    def __init__(self, validator=None, iterable=None, trim=True):
        if validator:
            self._validate = validator
        elif callable(validator):
            self._validate = lambda value : True
        else:
            raise TypeError("Validator must be callable!")
        if iterable:
            self.extend(iterable, trim=trim)
    
    def append(self, obj):
        if not self._validate(obj):
            raise ValueError("Value %s can not put in this RestrictList" % str(obj))
        return super().append(obj)

    def insert(self, index, obj):
        if not self._validate(obj):
            raise ValueError("Value %s can not put in this RestrictList" % str(obj))
        return super().insert(index, obj)

    def extend(self, iterable, trim=False):
        if not trim:
            cond = map(self._validate, iterable)
            if not all(cond):
                raise ValueError("Contains value that cannot be put into this RestricedList")
        else:
            iterable = [o for o in iterable if self._validate(o)]
        return super().extend(iterable)


class TypeRestrictedList(RestrictedList):

    def __init__(self, types=None):
        self._types = (tuple(types) if not isinstance(types, type) else (types, )) if types else None
        super().__init__(validator=lambda value: isinstance(value, self._types) if self._types else True)
        
    @property
    def types(self):
        return self._types


class _JavaIntegers:
    _bit_length = 0
    _valid_bits = 0
    def __init__(self, bit_length):
        self._bit_length = bit_length
        self._valid_bits = 0xFF
        for i in range(bit_length // 8 - 1):
            self._valid_bits *= 256
            self._valid_bits += 0xFF

    @property
    def bit_length(self):
        return self._bit_length
    
    @property
    def max_value(self):
        return 1 << (self.bit_length - 1)
    
    @property
    def min_value(self):
        return -self.max_value
    
    @property
    def num_range(self):
        return range(self.min_value, self.max_value)

    @property
    def valid_bits(self):
        return self._valid_bits

    @property
    def sign_bit(self):
        return 1 << (self.bit_length - 1)

    @property
    def number_bits(self):
        return (self.valid_bits + 1) // 2 - 1

    def to_signed(self, v='0', base=10):
        """
        Convert a python int, or objects that can be converted to int,
        into Java type integers.
        This is helful when writing binary file for Java programs to read,
        such as NBT

        For example:
        ```
        >>> from struct import Struct
        >>> int_struct = Struct(">i")
        >>> 0xaccc821c
        2899083804
        >>> JavaInteger(0xaccc821c)
        -1395883492
        >>> int_struct.pack(0xaccc821c)
        Traceback (most recent call last):
          File "<pyshell#15>", line 1, in <module>
            int_struct.pack(0xaccc821c)
        struct.error: argument out of range
        >>> int_struct.pack(JavaInteger.to_signed(0xaccc821c))
        b'\\xac\\xcc\\x82\\x1c'
        ```
        """
        result = int(v, base=base)
        result = result % (self.valid_bits + 1)
        if result not in self.num_range:
            if result & self.sign_bit:
                result -= 1
                result -= self.valid_bits
        return result

    def to_unsigned(self, v='0', base=10):
        """
        Convert a python int, or objects that can be converted to int,
        into Java type integers.
        This is helful when writing binary file for Java programs to read,
        such as NBT

        For example:
        ```
        >>> from struct import Struct
        >>> int_struct = Struct(">i")
        >>> 0xaccc821c
        2899083804
        >>> JavaInteger(0xaccc821c)
        -1395883492
        >>> int_struct.pack(0xaccc821c)
        Traceback (most recent call last):
          File "<pyshell#15>", line 1, in <module>
            int_struct.pack(0xaccc821c)
        struct.error: argument out of range
        >>> int_struct.pack(JavaInteger.to_unsigned(0xaccc821c))
        b'\\xac\\xcc\\x82\\x1c'
        ```
        """
        result = int(v, base=base)
        result = result % (self.valid_bits + 1)
        if result not in self.num_range:
            if result < 0:
                result += 1
                result += self.valid_bits
        return result

    def validate(self, v):
        return isinstance(v, int) and v in self.num_range
            
    
JavaByte = _JavaIntegers(8)
JavaShort = _JavaIntegers(16)
JavaInteger = _JavaIntegers(32)
JavaLong = _JavaIntegers(64)
