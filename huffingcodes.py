from collections import deque
from copy import copy

from bitsandbytes import BinInt, Bits
from huffmantree import HuffingTreeNode


def encode(string: bytearray) -> bytearray:
    if isinstance(string, str):
        string = bytearray(string, "utf-8")

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
