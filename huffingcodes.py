from collections import deque
from copy import copy

from bitsandbytes import BinInt, Bits, get_mask
from huffmantree import HuffingTreeNode


def huffing_encode(string: bytearray | str) -> bytearray:
    if isinstance(string, str):
        string = bytearray(string, "utf-8")

    sorted_encodings, lengths = HuffingTreeNode.create_huffing_tree(
        string
    ).canonicalized_encodings()

    max_bin_length = len(bin(max(lengths) + 1)) - 2
    out = Bits()
    out.append_binint(BinInt(max_bin_length, 3))
    for length in lengths:
        out.append_binint(BinInt(length, max_bin_length))
    out.append_binint(BinInt((1 << max_bin_length) - 1, max_bin_length))

    out.fill_byte()
    letters = bytearray(char for char, _ in sorted_encodings.items())
    for letter in letters:
        out.append_binint(BinInt(letter, 8))

    for char in string:
        encoding = sorted_encodings[char]
        for bit in encoding:
            out.append_bit(bit)

    return out.to_byte_array()


def huffing_decode(string: bytearray) -> bytearray:
    counts: deque[int] = deque()

    bits = map(
        bool,
        (string[0] & get_mask(bit) for bit in range(3)),
    )
    max_bin_length = BinInt.from_bits(bits).to_int()
    max_count = (1 << max_bin_length) - 1

    byte = 0
    bit = 3
    while True:
        bits = list()
        for _ in range(max_bin_length):
            bits.append(int(string[byte]) & get_mask(bit))
            bit += 1
            if bit >= 8:
                bit = 0
                byte += 1

        count = BinInt.from_bits(map(bool, bits)).to_int()
        if count >= max_count:
            break

        counts.append(count)

    if bit == 0:
        byte -= 1
    code = BinInt(0, 1)

    encodings = dict()
    letter_index = byte + 1
    while len(counts):
        if not counts[0]:
            code.leftshiftonce()
            counts.popleft()
            continue

        encodings[string[letter_index]] = copy(code)
        letter_index += 1
        counts[0] -= 1
        code.inc()

    tree = HuffingTreeNode.from_encodings(encodings)

    bits = Bits.from_byte_array(string[letter_index:])
    letters = bytearray()
    current = tree
    for bit in bits:
        if bit:
            current = current.right
        else:
            current = current.left

        if current.letter is not None:
            letters.append(current.letter)
            current = tree

    return letters


if __name__ == "__main__":
    print(encoded := huffing_encode("vennelige pennevenner"))
    print(decoded := huffing_decode(encoded))
