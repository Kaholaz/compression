from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from typing import Iterator, Optional

from bitsandbytes import BinInt, Bits


@dataclass
class HuffingTreeNode:
    letter: Optional[str]
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

    def add_encoding(self, value: "BinInt", letter: str):
        current = self
        for choice in tuple(value):
            if choice:
                if current.right is None:
                    current.right = self.__class__(None, None, None, None)
                current = current.right
            else:
                if current.left is None:
                    current.left = self.__class__(None, None, None, None)
                current = current.left
        current.letter = letter

    @classmethod
    def create_huffing_tree(cls, s: str) -> "HuffingTreeNode":
        heap = HuffingTreeHeap([HuffingTreeNode(key, value, None, None) for key, value in Counter(s).items()])

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
        while (min := i * 2 + 1) < len(self):
            if (right := min + 1) < len(self) and self.heap[min] > self.heap[right]:
                min = right

            if self.heap[min] < self.heap[i]:
                self.heap[min], self.heap[i] = self.heap[i], self.heap[min]
                i = min            
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


def get_encodings(root: HuffingTreeNode, code: BinInt) -> Iterator[tuple[str, tuple[bool]]]:
    if root.letter is not None:
        encoding = tuple(code)
        code.rightshift()
        yield root.letter, encoding
    else:
        code.leftshift()
        for char, encoding in get_encodings(root.left, code):
            yield char, encoding

        code.leftshift()
        code.inc()
        for char, encoding in get_encodings(root.right, code):
            yield char, encoding
        code.rightshift()


def encode(string: str) -> tuple[str, Bits]:
    tree = HuffingTreeNode.create_huffing_tree(string)

    encodings = {char: encoding for char, encoding in get_encodings(tree, BinInt())}

    lengths: defaultdict[int, int] = defaultdict(lambda: 0)
    sorted_encodings = sorted(encodings.items(), key=lambda item: len(item[1]))
    char, encoding = sorted_encodings[0]
    code = BinInt(None, len(encoding))

    encodings[char] = tuple(code)
    lengths[len(code)] += 1
    for char, encoding in sorted_encodings[1:]:
        code.inc()
        while len(encoding) > len(code):
            code.leftshift()
        encodings[char] = tuple(code)
        lengths[len(code)] += 1

    out = Bits()
    for i in range(1, len(code) + 1):
        if lengths[i] >= (1 << 4):
            raise ValueError("Not enough bits to represent the length of the huffman code")
        out.append_binint(BinInt(lengths[i], 4))
    out.fill_bit()
    out.append_binint(BinInt(255))
    
    letters = "".join(char for char, _ in sorted_encodings)
    for letter in bytearray(letters, "utf-8"):
        out.bytes.append(int(letter))
    print(out.to_byte_array())

    for char in string:
        encoding = encodings[char]
        for bit in encoding:
            out.append_bit(bit)

    return out.to_byte_array()


def decode(string: bytearray):

    counts: deque[int] = deque()
    for i, byte in enumerate(string):
        if byte == 255:
            break
        nibbles = [byte >> 4, byte & 15]
        for nibble in nibbles:
            counts.append(nibble)
    
    tree = HuffingTreeNode(None, None, None, None)
    code = BinInt(0, 1)

    letter_index = i + 1
    while len(counts):
        if not counts[0]:
            code.leftshift()
            counts.popleft()
            continue

        tree.add_encoding(tuple(code), chr(string[letter_index]))
        letter_index += 1
        counts[0] -= 1
        code.inc()
    
    
    bits = Bits(string[letter_index:])

    
    letters = []
    current = tree
    for bit in bits:
        if bit:
            current = current.right
        else:
            current = current.left
        
        if current.letter is not None:
            letters.append(current.letter)
            current = tree
    
    return "".join(letters)


print(encoded := encode("vennelige pennevenner"))
print(decoded := decode(encoded))