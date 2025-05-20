# WriteUp: Inquebrável

## Descrição do Desafio:
**Autor:** [HenriUz](https://github.com/HenriUz) \
**Categoria:** pwn \
**Descrição:**
> Me disseram que manipular valores na memória de forma indireta é extremamente difícil... Então, resolvi criar meu próprio sistema de autenticação — que, aliás, é **inquebrável**.

## Passo a passo da solução
### 1. Análise do código-fonte
Este desafio fornece apenas o código-fonte e o executável. Analisando o código, vemos apenas duas funções: `main()` e `check()`. 

{% code title="inquebravel.c" overflow="wrap" lineNumbers="true" %}
```c
#include <stdio.h>

int check(char *string) {
    int vet[20] = {0x0, 0x29, 0x3f, 0x23, 0x33, 0xa, 0x3d, 0x2e, 0x2e, 0x2d, 0x3a, 0x7, 0x3e, 0x2d, 0x3a, 0x2e, 0x24, 0x27, 0x3f, 0x35};
    for (int i = 0; i < 20; i++) {
        if ((int)string[i] != (vet[i] ^ 0x48)) {
            return 0;
        }
    }
    return 1;
}

int main() {
    FILE *f;
    char flag[39];
    char permissao[21];
    char nome[12];

    printf("\nDigite seu nome: ");
    fgets(nome, 33, stdin);

    if (check(permissao)) {
        printf("\nPermissão verificada, aqui está a flag!");

        f = fopen("flag.txt", "r");
        fgets(flag, 39, f);
        fclose(f);

        printf("\n%s\n", flag);
    } else {
        printf("\nVocê não tem permissão para ver a flag.\n");
    }

    return 0;
}
```
{% endcode %}

A função `main()` apenas pede para o usuário digitar um nome, que será armazenado na variável `nome`, e depois verifica o retorno da função `check()`, se for 1 a `flag` é impressa e se for 0 uma outra mensagem é impressa e o programa encerra. A questão então, é entender o que está acontecendo dentro da `check()`.

Analisando ela, vemos que ela recebe um ponteiro para uma *string*, e inicializa um vetor de inteiros com 20 valores em hexadecimal. Após definir isso, ela percorre ele por meio de um `for` e a cada iteração ela faz a seguinte verificação:

{% code title="verificacao.c" overflow="wrap" lineNumbers="true" %}
```c
if ((int)string[i] != (vet[i] ^ 0x48))
```
{% endcode %}

Se o resultado dessa verificação for verdadeiro, é retornado o valor 0 e com isso a `flag` não é impressa. Então o objetivo é fazer com que essa condição nunca dê verdadeiro.

Mas o que essa condição faz? Bom, ela pega o elemento `i` (valor da iteração atual) da *string* informada como parâmetro e compara com o resultado da operação `vet[i] ^ 0x48`, que nada mais é do que a posição `i` do vetor instânciado no início do código modificado com operador `XOR` no número `0x48`. 

{% hint style="info" %}

**Note:** O operador `XOR` realiza uma operação *bit* a *bit*, aí se os dois *bits* comparados forem iguais, o valor resultante vai ser 0, e se forem diferente, o resultado vai ser 1. 

Por exemplo: o segundo elemento do vetor é `0x29` que em binário é `00101001`, e `0x48` em binário é `01001000`, logo uma operação de `XOR` entre esses dois elementos resulta em `01100001`. Note que, nas posições em que os valores são iguais, o resultado é 0, e, nas posições em que são diferentes, o resultado é 1.

{% endhint %}

Então o objetivo é fazer com que a *string* passada como parâmetro tenha os 20 valores correspondentes da operação `vet[i] ^ 0x48`. Calculando esses valores, obtemos a sequencia: `0x48`, `0x61`, `0x77`, `0x6b`, `0x7b`, `0x42`, `0x75`, `0x66`, `0x66`, `0x65`, `0x72`, `0x4f`, `0x76`, `0x65`, `0x72`, `0x66`, `0x6c`, `0x6f`, `0x77`, `0x7d`. E se convertermos o valor para *string* obtemos a frase: `Hawk{BufferOverflow}`.

{% hint style="warning" %}

**Importante:** Essa não é a `flag` final, note que está diferente do padrão fornecido, que inicia com `h` e não `H`.

{% endhint %}

### 2. Exploit
Se olharmos na `main()`, podemos identificar que a variável passada para a `check()` é a `permissao`, uma *string* que de cara não é modificada em nenhum lugar. Porém, se analisarmos a função `fgets()`, podemos ver que ela está lendo mais valores do que a *string* armazena.

{% code title="fgets.c" overflow="wrap" lineNumbers="true" %}
```c
fgets(nome, 33, stdin); // Armazena em nome; lê 33 caracteres; lê da entrada padrão (terminal).
```
{% endcode %}

Em programas assim, as variáveis (do mesmo tipo) declaradas em uma função costumam ficar adjacentes na memória, isso significa que se digitarmos mais de 12 caracteres (quantidade de caracteres que a variável `nome` armazena) no terminal, os outros caracteres serão salvos consecutivamente na memória, reescrevendo o valor da variável que estiver adjacente. No caso deste programa, a variável que está adjacente à `nome` é a `permissao`. 

{% hint style="info" %}

**Note:** Esse desafio foi pensado para ser feito sem auxílio de ferramentas como *debug*, então ele tinha algumas dicas implícitas do *exploit*. A primeira está na descrição que fala de **manipulação de valores na memória de forma indireta**, a segunda é o valor encontrado na função `check()` que diz o tipo de *exploit* (`buffer overflow`), a terceira e última é o `fgets()` ler exatamente o tamanho do vetor `nome` + o tamanho do vetor passado como parâmetro para a função.

{% endhint %}

### 3. Solução
Sabendo que devemos apenas "estourar" a variável `nome` e sabendo que o valor esperado pela `check()` é `Hawk{BufferOverflow}`. Podemos realizar o *exploit* apenas escrevendo 12 caracteres quaisquers e depois escrevendo `Hawk{BufferOverflow}`. 

Uma mensagem de exemplo é: `aaaaaaaaaaaaHawk{BufferOverflow}`.

{% hint style="warning" %}

**Importante:** Desafios de `PWN` normalmente são feitos para serem executados remotamente, via comando `nc`, porque as `flags` só estarão no computador dos organizadores do desafio. Porém para facilitar a análise, ó código e o `exploit` são testados localmente, e para isso é utilizado uma `fake flag` para o código não quebrar na hora de abrir o arquivo. Esse desafio não era diferente, a `flag` só seria revelada se o `exploit` fosse realizado via `nc` no IP e porta fornecidos.

Pelo mesmo motivo da `flag` estar somente no computador dos organizadores, não adianta modificar o código-fonte na sua máquina, pois o que será obtido é a `fake flag`, e não a real.

{% endhint %}

### Flag
`hawk{aCH0_qu3_n@0_3r@_tAO_InqU3BraV3l}`