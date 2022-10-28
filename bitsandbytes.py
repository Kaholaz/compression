from collections import deque
from typing import Iterator, Optional


class BinInt:
    bits: deque[bool | int]

    def __init__(self, value: Optional[int] = None, length=-1):
        self.bits = deque()
        if value is not None:
            bit_string = bin(abs(value))[2:]
            for bit in bit_string:
                self.bits.append(int(bit))

        while len(self) < length:
            self.bits.appendleft(False)

        if value is not None and value < 0:
            if self.bits[0]:
                raise ValueError(
                    "A greater bit size is needed to represent this negative number"
                )
            self.__invert__()
            self.inc()

    def leftshiftonce(self):
        self << 1

    def rightshiftonce(self):
        self >> 1

    def inc(self, signed: bool = False):
        incremented = False
        i = len(self) - 1

        while not incremented and i >= 0:
            incremented = not self.bits[i]
            self.bits[i] = incremented
            i -= 1

        if not incremented and not signed:
            self.bits.appendleft(True)

    def hex(self) -> str:
        return hex(self.to_int())[2:]

    def __copy__(self):
        out = BinInt()
        out.bits = self.bits.copy()
        return out

    def __tuple__(self):
        return tuple(self.bits)

    def to_int(self, signed: bool = False):
        if len(self) == 0:
            return 0
        if len(self) == 1:
            return self.bits[0]

        factor = 2 << len(self) - 2

        i = 0
        total = factor * self.bits[0] if not signed else -factor * self.bits[0]
        while factor > 1:
            i += 1
            factor >>= 1
            total += factor * self.bits[i]
        return total

    def __lshift__(self, other: int):
        for _ in range(other):
            self.bits.append(False)
        return self

    def __rshift__(self, other: int):
        for _ in range(other):
            if not len(self):
                break
            self.bits.pop()

        return self

    def __invert__(self):
        self.bits = deque(map(lambda b: not b, self.bits))

    def __len__(self):
        return len(self.bits)

    def __iter__(self):
        for bit in self.bits:
            yield bit

    def __repr__(self):
        return f"{self.__class__.__name__}(value={self.to_int()}, length={len(self)})"

    @classmethod
    def from_bits(cls, t: Iterator[bool]) -> "BinInt":
        result = cls(0)
        result.bits = deque(t)

        return result


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

        self.bytes[-1].bits[self.bit_pointer] = boolean

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
            for bit_pointer in range(8):
                yield byte.bits[bit_pointer]


def get_mask(bit: int) -> int:
    return 1 << (7 - bit)
