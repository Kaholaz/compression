from collections import Counter, deque
from copy import copy
from typing import Iterator, Optional

from dataclasses import dataclass

from bitsandbytes import BinInt, Bits


@dataclass
class HuffingTreeNode:
    letter: Optional[int]
    frequency: Optional[int]

    left: Optional["HuffingTreeNode"]
    right: Optional["HuffingTreeNode"]

    def __eq__(self, other: "HuffingTreeNode"):
        return self.frequency == other.frequency

    def __lt__(self, other: "HuffingTreeNode"):
        return self.frequency < other.frequency

    def __ge__(self, other: "HuffingTreeNode"):
        return not self < other

    def __gt__(self, other: "HuffingTreeNode"):
        return self.frequency > other.frequency

    def __le__(self, other: "HuffingTreeNode"):
        return not self > other

    def add_encoding(self, value: "BinInt", letter: int):
        current = self
        for choice in tuple(value):
            if choice:
                if current.right is None:
                    current.right = HuffingTreeNode(None, None, None, None)
                current = current.right
            else:
                if current.left is None:
                    current.left = HuffingTreeNode(None, None, None, None)
                current = current.left
        current.letter = letter

    def canonicalized_encodings(self) -> tuple[dict[int, BinInt], list[int]]:
        sorted_encodings = sorted(self.encodings.items(), key=lambda item: len(item[1]))

        encodings = {}

        first_char, first_encoding = sorted_encodings[0]
        code = BinInt(None, len(first_encoding))
        encodings[first_char] = copy(code)

        lengths: list[int] = [0 for _ in range(len(code))]
        lengths[-1] = 1
        for char, encoding in sorted_encodings[1:]:
            code.inc()
            while len(encoding) > len(code):
                lengths.append(0)
                code.leftshift()
            encodings[char] = copy(code)
            lengths[-1] += 1

        return encodings, lengths

    @property
    def encodings(self) -> dict[str, BinInt]:
        def inner(root: HuffingTreeNode, code: BinInt) -> Iterator[tuple[str, BinInt]]:
            if root.letter is not None:
                encoding = BinInt(int(code), len(code))
                code.rightshift()
                yield root.letter, encoding
            else:
                code.leftshift()
                for char, encoding in inner(root.left, code):
                    yield char, encoding

                code.leftshift()
                code.inc()
                for char, encoding in inner(root.right, code):
                    yield char, encoding
                code.rightshift()

        return {char: encoding for char, encoding in inner(self, BinInt())}

    @classmethod
    def from_encodings(cls, encodings: dict[int, BinInt]) -> "HuffingTreeNode":
        tree = HuffingTreeNode(None, None, None, None)
        for char, encoding in encodings.items():
            tree.add_encoding(encoding, char)
        return tree

    @classmethod
    def create_huffing_tree(cls, s: bytearray) -> "HuffingTreeNode":
        heap = HuffingTreeHeap(
            [
                HuffingTreeNode(key, value, None, None)
                for key, value in Counter(s).items()
            ]
        )

        root = cls(None, None, None, None)

        while len(heap) > 1:
            left = heap.pop_head()
            right = heap.pop_head()
            root = cls(None, left.frequency + right.frequency, left, right)

            heap.insert(root)

        return root


class HuffingTreeHeap:
    heap = list[HuffingTreeNode]

    def __init__(self, heap: list[HuffingTreeNode]):
        self.heap = heap[:]
        for i in range((len(self) - 2) // 2, -1, -1):
            self.fix_down(i)

    def swap(self, a: int, b: int):
        self.heap[a], self.heap[b] = self.heap[b], self.heap[a]

    def fix_up(self, i: int):
        child = i
        parent = (child - 1) // 2
        while parent >= 0 and self.heap[child] < self.heap[parent]:
            self.swap(child, parent)
            child = parent
            parent = (child - 1) // 2

    def fix_down(self, i: int):
        while (_min := i * 2 + 1) < len(self):
            if (right := _min + 1) < len(self) and self.heap[_min] > self.heap[right]:
                _min = right

            if self.heap[_min] < self.heap[i]:
                self.heap[_min], self.heap[i] = self.heap[i], self.heap[_min]
                i = _min
            else:
                break

    def insert(self, item: HuffingTreeNode):
        i = len(self)
        self.heap.append(item)
        self.fix_up(i)

    def pop_head(self):
        self.swap(0, len(self) - 1)
        result = self.heap.pop()

        if len(self) == 0:
            return result

        self.fix_down(0)

        return result

    def __len__(self):
        return len(self.heap)


def encode(string: str | bytearray) -> bytearray:
    if isinstance(string, str):
        string = bytearray(string, "utf-8")
    string: bytearray

    sorted_encodings, lengths = HuffingTreeNode.create_huffing_tree(
        string
    ).canonicalized_encodings()

    out = Bits()
    for length in lengths:
        if length >= (1 << 4):
            raise ValueError(
                "Not enough bits to represent the length of the huffman code"
            )
        out.append_binint(BinInt(length, 4))
        int(out.bytes[-1])
    out.fill_bit()
    out.append_binint(BinInt(255))

    letters = bytearray(char for char, _ in sorted_encodings.items())
    for letter in letters:
        out.append_binint(BinInt(letter, 8))

    for char in string:
        encoding = sorted_encodings[char]
        for bit in encoding:
            out.append_bit(bit)

    return out.to_byte_array()


def decode(string: bytearray):
    counts: deque[int] = deque()
    i = 0
    for i, byte in enumerate(string):
        if byte == 255:
            break
        nibbles = [byte >> 4, byte & 15]
        for nibble in nibbles:
            counts.append(nibble)

    code = BinInt(0, 1)

    encodings = dict()
    letter_index = i + 1
    while len(counts):
        if not counts[0]:
            code.leftshift()
            counts.popleft()
            continue

        encodings[string[letter_index]] = copy(code)
        letter_index += 1
        counts[0] -= 1
        code.inc()
    tree = HuffingTreeNode.from_encodings(encodings)

    bits = Bits.from_byte_array(string[letter_index:])
    letters = []
    current = tree
    for bit in bits:
        if bit:
            current = current.right
        else:
            current = current.left

        if current.letter is not None:
            letters.append(chr(current.letter))
            current = tree

    return "".join(letters)


print(encoded := encode("vennelige pennevenner"))
print(decoded := decode(encoded))
