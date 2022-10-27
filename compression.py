from huffingcodes import huffing_decode, huffing_encode
from lempelziv import lempelziv_decode, lempelziv_encode


def encode(text: str | bytearray) -> bytearray:
    if isinstance(text, str):
        text = bytearray(text, "utf-8")
    
    return huffing_encode(lempelziv_encode(text))

def decode(text: bytearray) -> bytearray:
    return lempelziv_decode(huffing_decode(text))
    

if __name__ == "__main__":
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
    print(encoded := encode(text))
    print(decoded := decode(encoded))
    assert decoded == text