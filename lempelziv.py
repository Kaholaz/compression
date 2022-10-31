from collections import deque
from itertools import islice

from tqdm import tqdm

from bitsandbytes import Bits, BinInt


class Search:
    to_search: deque[int]

    def __init__(self, to_search: deque[int]):
        self.to_search = to_search

    def match(self, pattern: bytearray, start_index: int) -> int:
        if len(self.to_search) == 0:
            return -1
        start_index %= len(self.to_search)
        for i in range(start_index, len(self.to_search) - len(pattern) + 1):
            if i + len(pattern) >= len(self.to_search):
                break
            for j in range(len(pattern)):
                if pattern[j] != self.to_search[i + j]:
                    break
            else:
                return i
        return -1


class History(deque[int]):
    search: Search
    size: int

    def __init__(self, size: int):
        super().__init__()
        self.size = size
        self.search = Search(self)

    def append(self, __x: int) -> None:
        super().append(__x)
        if len(self) > self.size:
            self.popleft()

    def find_best_match(
        self,
        text: bytearray,
        start_index: int,
        min_length: int = 4,
        max_length: int = 255,
    ) -> tuple[int, int]:
        best_match = (0, 1)  # (Best match, letters to advance *or* letters in match)
        try:
            pattern = text[start_index : start_index + min_length]
        except IndexError:
            return best_match

        while True:
            found = self.search.match(pattern, best_match[0])
            if found == -1:  # No match
                break

            best_match = (found - len(self), len(pattern))
            if best_match[1] >= max_length:
                break

            try:
                pattern.append(text[start_index + len(pattern)])
            except IndexError:
                break

        return best_match

    def retrive(self, index: int, length: int) -> list[int]:
        index %= len(self)
        return list(islice(self, index, index + length))

    def __str__(self) -> str:
        return super().__str__()

    def __repr__(self) -> str:
        return super().__repr__()


class Block(Bits):
    def __init__(self):
        super().__init__()

    @classmethod
    def from_matched_section(cls, match: int, length: int):
        if match >= 0:
            raise ValueError("Match must be negative")
        if not (0 <= length < 256):
            raise ValueError(
                "Length must be positive and not greater than one byte of info"
            )

        match_bin = BinInt(match, 16)
        length_bin = BinInt(length, 8)
        block = cls()
        block.append_binint(match_bin)
        block.append_binint(length_bin)

        return block

    @classmethod
    def from_unmatched_section(cls, unmatched: bytearray):
        length_bin = BinInt(len(unmatched), 16)

        block = cls()
        block.append_binint(length_bin)
        for unmatch in unmatched:
            block.append_binint(BinInt(unmatch, 8))

        return block


def lempelziv_encode(text: bytearray | str) -> bytearray:
    if isinstance(text, str):
        text = bytearray(text, "utf-8")

    max_history = 2 << 14 - 1
    history = History(max_history)

    out = Bits()

    unmatched = bytearray()
    i = 0
    with tqdm(
        total=len(text), desc="Compressing file using lempelziv..."
    ) as loading_bar:
        while i < len(text):
            # Unmatched is full
            if len(unmatched) > max_history:
                out.append_bits(Block.from_unmatched_section(unmatched))
                unmatched = bytearray()

            # Find best match and react accordingly
            best_match = history.find_best_match(text, i)
            if best_match[0] == 0:
                unmatched.append(text[i])
            else:
                if len(unmatched):
                    out.append_bits(Block.from_unmatched_section(unmatched))
                    unmatched = bytearray()
                out.append_bits(Block.from_matched_section(*best_match))

            # Increment history and current index
            for _ in range(best_match[1]):
                history.append(text[i])
                i += 1

            loading_bar.update(best_match[1])

    # Don't drop remaining unmatched
    if len(unmatched):
        out.append_bits(Block.from_unmatched_section(unmatched))

    return out.to_byte_array()


def lempelziv_decode(text: bytearray | str) -> bytearray:
    out = bytearray()

    i = 0
    history = History(2 << 14 - 1)
    while i < len(text):
        identifier = BinInt((text[i] << 8) + text[i + 1], 16)
        i += 2

        identifier_int = identifier.to_int(signed=True)
        if identifier_int < 0:
            length = text[i]
            i += 1
            new_text = history.retrive(identifier_int, length)
        elif identifier_int == 0:
            raise ValueError("Something is wrong with the text to decode!")
        else:
            new_text = text[i : i + identifier_int]
            i += identifier_int

        for letter in new_text:
            history.append(letter)
            out.append(letter)

    return out


if __name__ == "__main__":
    print(lempelziv_decode(lempelziv_encode("undrende dundrende plundrende")))
