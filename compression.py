from tqdm import tqdm

from file_handeling import read_file, write_file
from huffingcodes import huffing_decode, huffing_encode
from lempelziv import lempelziv_decode, lempelziv_encode


def encode(text: str | bytearray) -> bytearray:
    if isinstance(text, str):
        text = bytearray(text, "utf-8")

    return huffing_encode(lempelziv_encode(text))


def encode_to_file(file_name: str, text: str | bytearray):
    write_file(file_name, encode(text))


def encode_file(file_name: str):
    file = read_file(file_name)
    encode_to_file(file_name + ".compressed", file)


def decode(text: bytearray) -> bytearray:
    return lempelziv_decode(huffing_decode(text))


def decode_file(file_name: str) -> bytearray:
    return decode(read_file(file_name))

def decode_and_write_file(file_name: str):
    write_file(file_name + ".uncompressed", decode_file(file_name))


if __name__ == "__main__":
    files = [
        "diverse.lyx",
        "diverse.pdf",
        "diverse.txt"
        "oppg8-kompr.pdf"
    ]
    for file in tqdm(files):
        encode_file(file)
        decode_and_write_file(file + ".compressed")