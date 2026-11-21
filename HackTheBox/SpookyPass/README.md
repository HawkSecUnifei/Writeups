# WriteUp: SpookyPass

## Descrição do Desafio:
**Autor**: [clubby789](https://app.hackthebox.com/users/83743) \
**Plataforma**: [Hack The Box](https://app.hackthebox.com/challenges/806) \
**Categoria**: Reversing \
**Dificuldade**: Muito fácil \
**Data**: 2024 \
**Descrição**:
> All the coolest ghosts in town are going to a Haunted Houseparty - can you prove you deserve to get in?

## Passo a Passo da Solução
### 1. Análise do arquivo fornecido
O desafio fornece um executável Linux de 64 bits chamado `pass`. Executando, ele pede uma senha para entrar na festa e, com uma senha qualquer, nos manda embora:

```bash
$ ./pass
Welcome to the SPOOKIEST party of the year.
Before we let you in, you'll need to give us the password: HawkSec
You're not a real ghost; clear off!
```

O primeiro passo em qualquer desafio de *reversing* é procurar *strings* no binário, e aqui isso já entrega a senha:

```bash
$ strings pass
...
Before we let you in, you'll need to give us the password:
s3cr3t_p455_f0r_gh05t5_4nd_gh0ul5
Welcome inside!
You're not a real ghost; clear off!
...
```

Mas a flag não aparece em lugar nenhum na saída do `strings`. Para entender por quê, vamos olhar o código.

### 2. Analisando o assembly
Analisando o assembly (pelo **Ghidra**, por exemplo), a função `main()` é bem simples. Ela lê a senha com `fgets()`, remove o `\n` do final e compara com a senha fixa usando `strcmp()`. Se estiver certa, monta a flag a partir de um array global chamado `parts` e a imprime.

{% code title="main" overflow="wrap" lineNumbers="true" %}

```c
int main(void)
{
  char *newline;
  char flag[26] = {0};
  char input[128];

  puts("Welcome to the \x1b[1;3mSPOOKIEST\x1b[0m party of the year.");
  printf("Before we let you in, you'll need to give us the password: ");
  fgets(input, 128, stdin);
  newline = strchr(input, '\n');
  if (newline != NULL) {
    *newline = '\0';
  }

  if (strcmp(input, "s3cr3t_p455_f0r_gh05t5_4nd_gh0ul5") == 0) {
    puts("Welcome inside!");
    for (unsigned int i = 0; i < 26; i++) {
      flag[i] = (char)parts[i];
    }
    puts(flag);
  }
  else {
    puts("You're not a real ghost; clear off!");
  }
  return 0;
}
```

{% endcode %}

O detalhe está no array `parts`: ele é um array de `int`, e não de `char`. Cada caractere da flag ocupa 4 bytes, ou seja, o caractere seguido de três bytes nulos. Por isso o `strings` não encontra a flag: ele procura sequências de caracteres imprimíveis seguidos, e aqui cada letra está isolada.

```bash
$ objdump -s -j .data pass
 4060 48000000 54000000 42000000 7b000000  H...T...B...{...
 4070 75000000 6e000000 30000000 62000000  u...n...0...b...
 4080 66000000 75000000 35000000 63000000  f...u...5...c...
 ...
```

### 3. Exploit
Temos dois caminhos. O mais direto é digitar a senha que encontramos:

```bash
$ ./pass
Welcome to the SPOOKIEST party of the year.
Before we let you in, you'll need to give us the password: s3cr3t_p455_f0r_gh05t5_4nd_gh0ul5
Welcome inside!
HTB{un0bfu5c4t3d_5tr1ng5}
```

O outro é ler o array `parts` direto do binário, pegando um byte a cada quatro, sem nem precisar da senha:

{% code title="solve.py" overflow="wrap" lineNumbers="true" %}

```py
from pwn import *

elf = ELF("./pass", checksec=False)

# Cada caractere da flag ocupa 4 bytes no array "parts"
parts = elf.read(elf.sym["parts"], 26 * 4)
flag = parts[::4].decode().strip("\x00")
print(flag)
```

{% endcode %}

### Flag
`HTB{un0bfu5c4t3d_5tr1ng5}`

## Autor da WriteUp
[Membro de Exploitation - Matheus Inhan](https://github.com/Soon-pyt)
