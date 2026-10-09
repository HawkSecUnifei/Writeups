# heap 0

## Descrição do Desafio

**Plataforma:** [picoCTF — heap 0](https://play.picoctf.org/practice/challenge/438)  
**Autor da WriteUp:** Marcelo Agrico Guedes  
**Edição:** picoCTF 2024  
**Categoria:** Binary Exploitation  
**Vulnerabilidade:** Heap Buffer Overflow

O desafio apresenta um programa interativo escrito em C que utiliza `malloc()` para armazenar dados na memória dinâmica (*heap*). Embora o programa trate uma variável como protegida, existe uma escrita sem verificação de tamanho capaz de alterar dados de uma segunda alocação. O objetivo da tarefa é compreender a corrupção de memória e modificar o valor de `safe_var`, fazendo com que `check_win()` entre no ramo que exibe a flag.

## Arquivos

* `chall.c` — arquivo-fonte disponibilizado pelo desafio.
* `chall` — binário Linux fornecido pelo picoCTF.
* Instância oficial do picoCTF — host e porta informados ao iniciar o desafio (podem variar entre sessões).

Os arquivos originais devem ser obtidos na plataforma oficial; não são incluídos neste repositório.

## Passo a Passo da Solução

### 1. Análise do arquivo fornecido

A leitura do arquivo `chall.c` permite identificar as seguintes alocações (trecho representativo do código original):

```c
#define INPUT_DATA_SIZE 5
#define SAFE_VAR_SIZE 5

input_data = malloc(INPUT_DATA_SIZE);
strncpy(input_data, "pico", INPUT_DATA_SIZE);

safe_var = malloc(SAFE_VAR_SIZE);
strncpy(safe_var, "bico", SAFE_VAR_SIZE);
```

`input_data` recebe a entrada do usuário e `safe_var` contém a string inicial `"bico"`. Ambas as requisições solicitam apenas **5 bytes**, suficientes para quatro caracteres mais `\0`. O menu do programa fornece as opções **1. Print Heap**, **2. Write to buffer**, **3. Print safe_var**, **4. Print Flag** e **5. Exit**. A opção 1 apresenta os endereços dos dois ponteiros, permitindo calcular a distância real entre eles na instância utilizada.

Nos ambientes Linux, o deslocamento entre o endereço retornado para `input_data` e o início de `safe_var` é **0x20 = 32 bytes**. Essa distância **não** significa que o buffer disponha de 32 bytes úteis: o tamanho solicitado foi 5, e o layout inclui espaço de alinhamento e metadados do alocador. O cálculo deve ser conferido com os endereços exibidos, pois a disposição da heap pode variar.

```text
input_data → ["pico\0"] ... [espaço/metadados do alocador] ... safe_var → ["bico\0"]
               endereço inicial                              + 0x20 (típico)
```

A falha está na função de escrita:

```c
void write_buffer() {
    printf("Data for buffer: ");
    fflush(stdout);
    scanf("%s", input_data);
}
```

Sem um limite de largura no formato `%s`, `scanf` continua gravando caracteres até encontrar um espaço em branco e acrescenta o byte nulo de término. Se a entrada superar o tamanho reservado, ocorre escrita fora dos limites do objeto alocado (**heap buffer overflow**).

A condição relevante, dentro de `check_win()`, é:

```c
if (strcmp(safe_var, "bico") != 0) {
    // ramo que lê e imprime a flag
}
```

Ou seja, a aplicação considera a variável alterada uma condição para vitória, embora a alteração possa ocorrer por um erro de memória, e não por uma operação autorizada.

### 2. Exploit

A estratégia consiste em alcançar os bytes de `safe_var` por meio da escrita iniciada em `input_data`.

1. Execute o programa do desafio em um ambiente isolado ou abra somente a instância oficial do picoCTF.
2. Use a opção **1** para registrar os endereços de `input_data` e `safe_var` e calcular `endereço(safe_var) - endereço(input_data)`.
3. Se o deslocamento observado for **32 bytes**, escolha **2** e envie **33 letras `A` consecutivas, sem espaços**. Este comprimento alcança o primeiro byte de `safe_var` no layout documentado.
4. Use a opção **3** para inspecionar `safe_var`. Em uma execução com esse layout, o primeiro byte terá sido sobrescrito por `A`; como o `scanf` também grava `\0` após a entrada, o texto da variável pode ser exibido simplesmente como `A`.
5. Escolha a opção **4**, que chama `check_win()`, e registre o resultado efetivamente apresentado pela instância.

Geração reprodutível da entrada de teste:

```python
payload = b"A" * 33
print(payload.decode())
```

A sequência funciona como prova de conceito: a corrupção de memória altera o resultado da comparação `strcmp(safe_var, "bico")`. Uma execução em outro alocador ou com outros endereços pode se comportar de modo diferente, inclusive encerrando o programa.

**Evidências da execução:**

Na instância oficial, a opção **1. Print Heap** exibiu os endereços abaixo:

```text
input_data: 0x5af901fa52b0
safe_var:   0x5af901fa52d0
```

A diferença entre os endereços foi de **0x20 (32 bytes)**. Em seguida, foi enviada uma entrada de **33 letras `A`** pela opção **2. Write to buffer**.

Após essa entrada, a opção **4. Print Flag** retornou:

```text
YOU WIN
academy{my_first_heap_overflow_045474c7}
```

**Correção e prevenção.** Como o buffer solicitado possui 5 bytes, a leitura pode ser limitada a quatro caracteres e um terminador:

```c
scanf("%4s", input_data);
```

Uma alternativa é `fgets(input_data, INPUT_DATA_SIZE, stdin)`, acompanhada do tratamento adequado de nova linha e do retorno da função. Além da validação de limites, testes com AddressSanitizer (`-fsanitize=address`) auxiliam a detectar escritas fora da área alocada. Controles de autorização não devem depender de variáveis que possam ser modificadas por entradas sem validação.

## Flag

`academy{my_first_heap_overflow_045474c7}`

## Autor da WriteUp

* Criado pela equipe **HawkSec Team**, em nome de **Marcelo Agrico Guedes**.

*Referências de estudo: [desafio oficial](https://play.picoctf.org/practice/challenge/438) e [descrição técnica pública do heap 0](https://picoctfsolutions.com/picoctf-2024-heap-0). Texto redigido para este documento, sem reprodução literal das referências.*
