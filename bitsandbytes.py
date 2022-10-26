from collections import deque
from typing import Iterator, Optional


class BinInt:
    bits: deque[bool | int]

    def __init__(self, value: Optional[int] = None, length=0):
        self.bits = deque()
        if value is not None:
            for bit in bin(value)[2:]:
                self.bits.append(int(bit))
        while len(self) < length:
            self.bits.appendleft(False)

    def leftshift(self):
        self.bits.append(False)

    def rightshift(self):
        if len(self):
            self.bits.pop()

    def inc(self):
        incremented = False
        i = len(self) - 1

        while not incremented and i >= 0:
            incremented = not self.bits[i]
            self.bits[i] = incremented
            i -= 1

        if not incremented:
            self.bits.appendleft(True)

    def hex(self) -> str:
        return hex(int(self))[2:]

    def __copy__(self):
        out = BinInt()
        out.bits = self.bits.copy()
        return out

    def __tuple__(self):
        return tuple(self.bits)

    def __int__(self):
        total = 0
        factor = 1
        for bit in reversed(self.bits):
            total += factor * bit
            factor *= 2
        return total

    def __len__(self):
        return len(self.bits)

    def __iter__(self):
        for bit in self.bits:
            yield bit

    def __repr__(self):
        return f"{self.__class__.__name__}(value={int(self)}, length={len(self)})"

    @classmethod
    def from_tuple(cls, t: tuple[bool]):
        result = cls(0)
        result.bits = deque(t)


class Bits:
    bytes: list[BinInt]
    bit_pointer: int

    def __init__(self, binints: list[BinInt] = None, bit_pointer: int = 8):
        if binints is None:
            binints = list()
        self.bytes = binints[:]
        self.bit_pointer = bit_pointer

    def append_bits(self, bits: "Bits"):
        for bit in bits:
            self.append_bit(bit)

    def append_bit(self, boolean: bool):
        if self.bit_pointer == 8:
            self.bytes.append(BinInt(0, 8))
            self.bit_pointer = 0

        self.bytes[-1].bits[self.bit_pointer] = boolean

        self.bit_pointer += 1

    def append_binint(self, binint: "BinInt"):
        for bit in binint:
            self.append_bit(bit)

    def fill_bit(self):
        while self.bit_pointer != 8:
            self.append_bit(False)

    def to_byte_array(self) -> bytearray:
        return bytearray(int(byte) for byte in self.bytes)

    @classmethod
    def from_byte_array(cls, _bytearray: bytearray) -> "Bits":
        binints = [BinInt(byte, 8) for byte in _bytearray]
        return cls(binints)

    def hex(self) -> str:
        return "0x" + "".join(byte.hex() for byte in self.bytes)

    def __iter__(self) -> Iterator[bool]:
        for byte in self.bytes:
            for bit_pointer in range(8):
                yield byte.bits[bit_pointer]
