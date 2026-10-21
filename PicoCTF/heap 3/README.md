# heap 3

## Descrição do Desafio

**Plataforma:** [picoCTF — heap 3](https://learn.cylabacademy.org/library/440)  
**Autor da WriteUp:** Marcelo Agrico Guedes  
**Edição:** picoCTF 2024  
**Categoria:** Binary Exploitation  
**Vulnerabilidade:** Use-After-Free (UAF)

O desafio apresenta um programa interativo escrito em C que utiliza alocação dinâmica de memória por meio das funções `malloc()` e `free()`.

O objetivo é explorar uma vulnerabilidade do tipo *Use-After-Free*, que ocorre quando um programa continua utilizando um ponteiro após a liberação da memória associada a ele.

Nesse caso, precisamos alterar o conteúdo de `x->flag`, inicialmente definido como `"bico"`, para `"pico"`, satisfazendo a condição necessária para obter a flag.

## Arquivos

* `chall.c` — código-fonte disponibilizado pelo desafio.
* `chall` — binário Linux fornecido pelo picoCTF.
* Instância oficial do picoCTF — endereço e porta informados ao iniciar o desafio.

Os arquivos originais devem ser obtidos na plataforma oficial e não são incluídos neste repositório.

## Passo a Passo da Solução

### 1. Análise do arquivo fornecido

Ao analisar o código-fonte `chall.c`, encontramos a seguinte estrutura:

```c
typedef struct {
    char a[10];
    char b[10];
    char c[10];
    char flag[5];
} object;
```

A estrutura possui quatro campos, totalizando **35 bytes**. O campo `flag` começa após os três primeiros vetores, ou seja, no deslocamento de **30 bytes**.

Na função `init()`, o programa realiza a alocação inicial:

```c
x = malloc(sizeof(object));
strncpy(x->flag, "bico", 5);
```

Dessa forma, `x` aponta para uma região de memória que contém uma estrutura do tipo `object`, com o campo `flag` inicialmente preenchido com `"bico"`.

A função responsável por verificar a condição de vitória é `check_win()`:

```c
if (!strcmp(x->flag, "pico")) {
    printf("YOU WIN!!11!!");
    // leitura e impressão da flag
}
```

A função `strcmp()` retorna zero quando as duas strings são iguais. Como o operador `!` inverte esse resultado, a condição será verdadeira quando `x->flag` contiver `"pico"`.

O programa também disponibiliza um menu com as seguintes opções:

```text
1. Print Heap
2. Allocate object
3. Print x->flag
4. Check for win
5. Free x
6. Exit
```

Inicialmente, utilizamos a opção **1. Print Heap**, que apresentou:

```text
[*]   Address   ->   Value
+-------------+-----------+
[*]   0x3b3c92ce  ->   bico
+-------------+-----------+
```

O endereço apresentado corresponde ao campo `x->flag`, como podemos observar na função `print_heap()`.

Em seguida, utilizamos a opção **3. Print x->flag**, que retornou:

```text
x = bico
```

Isso confirmou que a variável ainda possuía seu valor inicial.

### 2. Identificação da vulnerabilidade

A vulnerabilidade está relacionada à maneira como o programa libera e reutiliza a memória.

A função responsável pela liberação é:

```c
void free_memory() {
    free(x);
}
```

Ao executar `free(x)`, a memória anteriormente alocada fica disponível para novas alocações. Entretanto, o ponteiro `x` não é definido como `NULL`, permanecendo com o endereço antigo.

Esse comportamento deixa um *dangling pointer*, ou seja, um ponteiro que continua referenciando uma região de memória já liberada.

O programa também permite realizar novas alocações por meio da função:

```c
void alloc_object() {
    printf("Size of object allocation: ");
    fflush(stdout);
    int size = 0;
    scanf("%d", &size);
    char* alloc = malloc(size);
    printf("Data for flag: ");
    fflush(stdout);
    scanf("%s", alloc);
}
```

Essa função permite escolher o tamanho da alocação e escrever dados na região retornada por `malloc()`.

Se uma nova alocação reutilizar a região anteriormente ocupada por `x`, os dados inseridos poderão modificar o conteúdo que ainda é acessado pelo ponteiro antigo.

O problema ocorre porque outras funções continuam utilizando `x->flag` mesmo após a liberação da memória.

### 3. Exploit

A estratégia consiste em liberar a memória de `x` e realizar uma nova alocação de tamanho equivalente, permitindo que a região liberada seja reutilizada.

Como a estrutura possui **35 bytes**, solicitamos uma nova alocação com esse tamanho.

Em seguida, precisamos posicionar a string `"pico"` exatamente no campo `flag`, que começa no deslocamento de 30 bytes.

Para isso, utilizamos o seguinte payload:

```python
payload = "A" * 30 + "pico"
print(payload)
```

O payload é composto por:

* **30 letras `A`** — preenchem os campos `a`, `b` e `c`.
* **4 caracteres (`pico`)** — ocupam o campo `flag`.
* **1 byte nulo (`\0`)** — é acrescentado automaticamente por `scanf()` para finalizar a string.

Assim, são utilizados os 35 bytes da nova alocação.

A sequência de exploração realizada na instância foi:

1. **Opção 5 — Free x:** liberamos a memória inicialmente ocupada pela estrutura `x`.
2. **Opção 2 — Allocate object:** solicitamos uma nova alocação de 35 bytes.
3. **Data for flag:** inserimos o payload contendo 30 letras `A` seguidas de `pico`.
4. **Opção 4 — Check for win:** executamos a verificação da condição de vitória.

A nova alocação permitiu que os dados inseridos fossem acessados por meio do ponteiro antigo `x`.

Como o campo `flag` passou a corresponder à string `"pico"`, a comparação realizada por `check_win()` foi satisfeita.

### 4. Resultado da execução

O desafio foi executado na instância oficial utilizando o Netcat:

```bash
nc xebec.cylabacademy.net 15834
```

O endereço e a porta podem variar entre sessões.

Após executar a sequência descrita anteriormente, selecionamos a opção **4. Check for win**.

O programa retornou:

```text
Enter your choice: 4
YOU WIN!!11!!
academy{now_thats_free_real_estate_40ec417f}
```

Dessa forma, conseguimos explorar a vulnerabilidade **Use-After-Free** e obter a flag.

### 5. Correção e prevenção

Uma das medidas para evitar esse problema é definir o ponteiro como `NULL` após liberar a memória:

```c
free(x);
x = NULL;
```

Além disso, o programa deve verificar se o ponteiro continua válido antes de utilizá-lo, evitando acessos a regiões de memória já liberadas.

Também é importante estabelecer limites para a leitura de dados e controlar corretamente o tempo de vida dos objetos alocados dinamicamente.

Neste desafio, a vulnerabilidade explorada não exigiu ultrapassar os limites da nova alocação. O problema principal foi o acesso à memória liberada por meio de um ponteiro que continuou sendo utilizado.

## Flag

`academy{now_thats_free_real_estate_40ec417f}`

## Autor da WriteUp

* Criado pela equipe **HawkSec Team**, em nome de **Marcelo Agrico Guedes**.

*Referências de estudo: [desafio oficial](https://learn.cylabacademy.org/library/440).*
