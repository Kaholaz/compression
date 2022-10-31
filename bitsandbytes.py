from typing import Iterator, Optional


class BinInt:
    value: int
    number_of_bits: int

    def __init__(self, value: Optional[int] = None, length=None):
        if value is None:
            value = 0

        if length is None:
            if value < 0:
                raise ValueError("Length needs to be specified for negative values")
            length = len(bin(value)) - 2

        max_value = (1 << length) - 1
        if abs(value) > max_value:
            raise ValueError("Length is bit enough to represent the number")

        self.value = value
        self.number_of_bits = length
        if value < 0:
            bits = self.from_bits(bit for bit in self)
            self.value = bits.value
            self.number_of_bits = bits.number_of_bits

    def leftshiftonce(self):
        self.number_of_bits += 1
        self.value <<= 1

    def rightshiftonce(self):
        self.number_of_bits = max(self.number_of_bits - 1, 1)
        self.value >>= 1

    def inc(self, signed: bool = False):
        self.value += 1
        if self.value >= 1 << self.number_of_bits:
            self.number_of_bits += 1

    def hex(self) -> str:
        return hex(self.to_int())[2:]

    def get_bit(self, bit_number):
        bit_value = 1 << (self.number_of_bits - bit_number - 1)
        return bool(bit_value & self.value)

    def set_bit(self, bit_number: int, value: bool):
        current_bit = self.get_bit(bit_number)
        bit_value = 1 << (self.number_of_bits - bit_number - 1)
        if current_bit and not value:
            self.value -= bit_value
        if not current_bit and value:
            self.value += bit_value

    def __copy__(self):
        out = BinInt(self.value, self.number_of_bits)
        return out

    def __tuple__(self):
        return tuple(bit for bit in self)

    def __iter__(self) -> Iterator[bool]:
        factor = 1 << (self.number_of_bits - 1)
        if self.value < 0:
            yield True
            total = -factor
            factor >>= 1
        else:
            total = 0

        while factor > 0:
            if (new_total := total + factor) > self.value:
                yield False
            else:
                yield True
                total = new_total
            factor >>= 1

    def to_int(self, signed: bool = False):
        if signed and self.get_bit(0):
            return self.value - (1 << self.number_of_bits)
        return  self.value

    def __lshift__(self, other: int) -> "BinInt":
        return self.__class__(self.value << other, self.number_of_bits + other)

    def __rshift__(self, other: int) -> "BinInt":
        return self.__class__(self.value >> other, self.number_of_bits - other)

    def __invert__(self) -> "BinInt":
        return self.__class__.from_bits(not bit for bit in self)

    def __len__(self):
        return self.number_of_bits

    def __repr__(self):
        return f"{self.__class__.__name__}(value={self.to_int()}, length={len(self)})"

    @classmethod
    def from_bits(cls, t: Iterator[bool]) -> "BinInt":
        value = 0
        length = 0
        for bit in t:
            value <<= 1
            length += 1
            value += bit

        return cls(value, length)


class Bits:
    bytes: list[BinInt]
    bit_pointer: int

    def __init__(
        self, binints: Optional[Iterator[BinInt]] = None, bit_pointer: int = 8
    ):
        if binints is None:
            binints = list()
        self.bytes = list(binints)
        self.bit_pointer = bit_pointer

    def append_bits(self, bits: "Bits"):
        for bit in bits:
            self.append_bit(bit)

    def append_bit(self, boolean: bool):
        if self.bit_pointer == 8:
            self.bytes.append(BinInt(0, 8))
            self.bit_pointer = 0

        self.bytes[-1].set_bit(self.bit_pointer, boolean)

        self.bit_pointer += 1

    def append_binint(self, binint: "BinInt"):
        for bit in binint:
            self.append_bit(bit)

    def fill_byte(self):
        while self.bit_pointer != 8:
            self.append_bit(False)

    def to_byte_array(self) -> bytearray:
        return bytearray(map(lambda byte: byte.to_int(), self.bytes))

    @classmethod
    def from_byte_array(cls, _bytearray: bytearray) -> "Bits":
        binints = map(lambda byte: BinInt(byte, 8), _bytearray)
        return cls(binints)

    def hex(self) -> str:
        return "0x" + "".join(byte.hex() for byte in self.bytes)

    def __iter__(self) -> Iterator[bool]:
        for byte in self.bytes:
            for bit in byte:
                yield bit


def get_mask(bit: int) -> int:
    return 1 << (7 - bit)
