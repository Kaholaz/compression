def read_file(file_name: str) -> bytearray:
    with open(file_name, "rb") as f:
        file = bytearray(f.read())

    return file


def write_file(file_name: str, file: bytearray):
    with open(file_name, "wb") as f:
        f.write(file)
