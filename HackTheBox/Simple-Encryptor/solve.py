from ctypes import CDLL

libc = CDLL("libc.so.6")

data = open("flag.enc", "rb").read()

# os 4 primeiros bytes são a seed usada no srand()
seed = int.from_bytes(data[:4], "little")
libc.srand(seed)

flag = b""
for b in data[4:]:
    xor_key = libc.rand() & 0xff
    shift = libc.rand() & 7

    # desfaz a rotação para a esquerda e depois o XOR
    b = ((b >> shift) | (b << (8 - shift))) & 0xff
    flag += bytes([b ^ xor_key])

print(flag.decode())
