from collections import deque
from typing import Iterator, Optional


class Bits:
    bytes: list[int]
    bit_pointer: int = -1

    def __init__(self, bytes: list[int] = list(), bit_pointer: int = -1):
        self.bytes = bytes[:]
        self.bit_pointer = bit_pointer
    
    def append_bits(self, bits: "Bits"):
        for bit in bits:
            self.append_bit(bit)

    def append_bit(self, boolean: bool):
        if self.bit_pointer == -1:
            self.bytes.append(0)
            self.bit_pointer = 7
        
        if boolean:
            self.bytes[-1] += 1 << self.bit_pointer

        self.bit_pointer -= 1

    def append_binint(self, binint: "BinInt"):
        for bit in binint:
            self.append_bit(bit)

    def fill_bit(self):
        while self.bit_pointer != -1:
            self.append_bit(0)

    def to_byte_array(self) -> bytearray:
        return bytearray(self.bytes)

    def hex(self) -> str:
        return "0x" + ''.join(hex(value) for value in self.bytes)

    def __iter__(self) -> Iterator[bool]:
        for byte in self.bytes:
            for bit_pointer in range(7, -1, -1):
                mask = 1 << bit_pointer
                out = bool(mask & byte)
                yield bool(mask & byte)    

    @classmethod
    def from_byte_array(cls, array: bytearray) -> "Bits":
        cls([int(byte) for byte in array])


class BinInt:
    bits: deque[bool]

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

    def __tuple__(self):
        return tuple(self.bits)

    def __int__(self):
        total = 0
        factor = 1
        for bit in reversed(self.bits):
            total += factor * bit
            bit *= 2
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