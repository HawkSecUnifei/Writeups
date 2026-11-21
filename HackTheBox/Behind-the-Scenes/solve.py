from pwn import *

elf = ELF("./behindthescenes", checksec=False)

# A senha está quebrada em 4 pedaços na .rodata, logo depois da mensagem de uso
textos = elf.get_section_by_name(".rodata").data().split(b"\x00")
inicio = textos.index(b"./challenge <password>") + 1
senha = b"".join(textos[inicio:inicio + 4])

p = process([elf.path, senha])
print(p.recvall().decode())
