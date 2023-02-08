import zlib

def compress_text(text):
    # Comprime el texto utilizando zlib
    compressed_text = zlib.compress(text.encode())

    # Convierte el texto comprimido a una cadena en hexadecimal
    compressed_text_hex = compressed_text.hex()

    return compressed_text_hex

def decompress_text(compressed_text_hex):
    # Convierte la cadena en hexadecimal a bytes
    compressed_text = bytes.fromhex(compressed_text_hex)

    # Descomprime el texto utilizando zlib
    uncompressed_text = zlib.decompress(compressed_text)

    # Convierte los bytes a una cadena de texto
    return uncompressed_text.decode()