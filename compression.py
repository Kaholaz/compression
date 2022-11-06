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


def easy():
    text = """
    Jeg gikk en tur på stien
    og søkte skogens ro.
    Da hørte jeg fra lien
    en gjøk som gol ko-ko.
    Ko-ko, ko-ko, ko-ko, ko-ro, ko-ko
    Ko-ko, ko-ko, ko-ko, ko-ro, ko-ko

    Jeg spurte den hvor mange,
    hvor mange år ennå.
    Den svarte meg med lange
    og klagende ko-ko.
    Ko-ko, ko-ko ....

    Jeg spurte om dens make
    og om dens eget bo. 
    Den satt der oppå grenen
    og kikket ned og lo.
    Ko-ko, ko-ko ....

    Vi bygger ikke rede,
    vi har hjem, vi to.
    Fru Spurv er mor til barna
    vi galer kun ko-ko"
    Ko-ko, ko-ko....
    """

    print(text := bytearray(text, "utf-8"))
    print(encoded := lempelziv_encode(text))
    print(decoded := lempelziv_decode(encoded))
    assert decoded == text


def hard():
    files = [
        "diverse.txt",
        "diverse.lyx",
        "opg8-kompr.pdf",
    ]

    for file in files:
        encode_file(file)
        decode_and_write_file(file + ".compressed")


if __name__ == "__main__":
    encode_file("diverse.lyx")
    decode_file("diverse.lyx.compressed")