from pwn import *

elf = ELF("./pass", checksec=False)

parts = elf.read(elf.sym["parts"], 26 * 4)
flag = parts[::4].decode().strip("\x00")
print(flag)
