# WriteUp: Persona 6

## Descrição do Desafio:
**Autor:** [HenriUz](https://github.com/HenriUz) \
**Categoria:** pwn \
**Descrição:**
> Há um tempo, um amigo me contou que estava realmente ansioso pelo anúncio de Persona 6. Então, decidi criar a minha própria versão de Persona 6 para ele se distrair enquanto espera.

## Passo a passo da solução
### 1. Análise do código fonte
O desafio fornece apenas o código fonte `persona6.c`, e o executável. Analisando ele, podemos ver que o código simula um jogo simples, no qual o jogador é representado pela `struct Player` que contém um inteiro sinalizado para a vida e um inteiro não sinalizado para as moedas. Também há os inimigos que são representados pela `struct Enemy` que contém apenas um inteiro para a vida.

{% hint style="info" %}

**Note:** O código pode ser compilado por meio do comando `gcc persona6.c -o persona6`, pois nesta situação não faz diferença se o código foi gerado na sua máquina ou na outra, já que não é um problema envolvendo proteções e/ou bibliotecas.

{% endhint %}

{% code title="Player-e-Enemy.c" overflow="wrap" lineNumbers="true" %}
```c
typedef struct player {
    int vida;
    unsigned int moedas;
} Player;

typedef struct Enemy {
    int vida;
} Enemy;
```
{% endcode %}

No quesito das funções, a função `main()` contém apenas a instância do `Player` e o *loop* principal, que lê a entrada do usuário e de acordo com essa entrada chama as outras duas funções ou encerra o código (situação que também ocorre se a variável `derrota` for diferente de 0). 

A função `dungeon()` é aquela que modifica a variável de derrota, analisando seu comportamento vemos que ela intância o inimigo com 10 de vida, e imprime algumas coisas na tela. Após isso entra em um *loop* que fica até o jogador ou o inimigo morrer, sendo que dentro do *loop* o usuário pode escolher entre atacar o inimigo (e causar 1 de dano), atacar usando a persona HAWK (e causar 5 de dano), e por fim fugir (que não é tratada no código, então nada acontece e o *loop* continua). Após o turno do usuário o inimigo ataca causando um dano entre 1-11.

Se o jogador for derrotado, a função retorna 1 e variável de derrota é atualizada encerrando o *loop* principal, mas se o jogador derrotou o inimigo, a variável continua com o valor 0 e o jogador ganha uma quantidade aleatória de moedas, no intervalo entre 1-5.

{% code title="main-e-dungeon.c" overflow="wrap" lineNumbers="true" %}
```c
int dungeon(Player *p) {
    int resp;
    unsigned int premio;
    Enemy e = {10};

    printf("\nEntrando na dungeon.");
    fflush(stdout);
    sleep(3);

    printf("\nExplorando ");
    fflush(stdout);

    for (int i = 0; i < 3; i++) {
        sleep(1);
        printf(". ");
        fflush(stdout);
    }

    srand(time(NULL));
    printf("\n\nUma sombra apareceu!\nSua vida: %d\nVida dela: %d\n", p->vida, e.vida);
    while (e.vida > 0 && p->vida > 0) {
        printf("\n1: Atacar\n2: Pernona (HAWK)\n3: Fugir\nResposta: ");
        scanf(" %d", &resp);
        switch (resp) {
        case 1:
            e.vida -= 1;
            break;
        case 2:
            e.vida -= 5;
            break;
        default:
        }

        p->vida -= (rand() % 11) + 1;

        printf("\nSua vida: %d\nVida dela: %d\n", p->vida, e.vida);
    }

    if (p->vida > 0) {
        premio = (rand() % 5) + 1;
        printf("\nSombra derrotada! Você recebeu %u moeda(s).\nSaindo da dungeon.\n", premio);
        p->moedas += premio;
        return 0;
    } else {
        printf("\nGAME OVER!\n");
        return 1;
    }
}

int main() {
    int resp;
    int derrota = 0;
    Player p = {100, 0};

    do {
        printf("\n=========== PERSONA 6 ===========\n");
        printf("\n1: Dungeon\n2: Loja\n3: Sair\nResposta: ");
        scanf(" %d", &resp);

        switch (resp) {
        case 1:
            derrota = dungeon(&p);
            break;
        case 2:
            loja(&p);
            break;
        default:
        }

    } while (resp != 3 && !derrota);
    return 0;
}
```
{% endcode %}

Note que a `main()` e a `dungeon()` não possuem nenhuma vulnerabilidade e nem algo relacionado com a `flag`. Então sobra analisar a `loja()`.

Essa função imprime as moedas do jogador e dá duas opções de compra:
1. Vida por 10 moedas.
2. `Flag` por 999999 moedas.

E pronto, sabemos onde a `flag` é acessada, basta saber como conseguir 999999 moedas, pois como visto na função `dungeon()` é impossível conseguir esse valor antes do jogador morrer.

{% code title="loja.c" overflow="wrap" lineNumbers="true" %}
```c
void loja(Player *p) {
    char flag[28];
    int resp;
    FILE *f;

    printf("\n=========== LOJA ===========\n");
    printf("\nMoeda(s): %u", p->moedas);
    printf("\n1: Vida (10)\n2: Flag (999999)\nResposta: ");
    scanf(" %d", &resp);

    if (resp == 1) {
        p->vida += (rand() % 10) + 1;
        p->moedas -= 10;
    } else if (resp == 2 && p->moedas >= 999999) {
        printf("\nCaramba! Quantas sombras você derrotou!?");

        f = fopen("flag.txt", "r");
        fgets(flag, 28, f);
        fclose(f);

        printf("\nAqui está sua flag: %s\n", flag);
        p->moedas -= 999999;
    }
}
```
{% endcode %}

### 2. Exploit
A vulnerabilidade nesse desafio é bem simples, e ela acontece na verificação para comprar os itens:

{% code title="vulnerabilidade.c" overflow="wrap" lineNumbers="true" %}
```c
if (resp == 1) {
    p->vida += (rand() % 10) + 1;
    p->moedas -= 10;
} else if (resp == 2 && p->moedas >= 999999) {
    printf("\nCaramba! Quantas sombras você derrotou!?");

    f = fopen("flag.txt", "r");
    fgets(flag, 28, f);
    fclose(f);

    printf("\nAqui está sua flag: %s\n", flag);
    p->moedas -= 999999;
}
```
{% endcode %}

Note que quando queremos comprar a `flag` o código verifica se temos as moedas necessárias, mas quando vamos comprar a vida, o código não verifica. Isso faz com que você possa ter moedas negativas quando você comprar com uma quantidade inferior a 10.

Mas nesse código a moeda não fica negativa, pois como visto na estrutura do jogador a moeda é declarada como inteiro não sinalizado, ou seja, não pode ser um número negativo. 

Note que na memória do computador os valores negativos são representados por valores altos, por exemplo: -1 equivale à `0xFFFFFFFFFFFFFFFF` (8 `bytes`). Mas como o tipo é não sinalizado, esse valor é tratado como um número positivo, equivalendo à 4294967295, um número muito superior a 999999.

### 3. Solução
Sabendo o `exploit` basta executar o programa, digitar a opção 2 para ir para a loja, selecionar a vida, e depois repetir o processo só que comprando a `flag` dessa vez.

{% hint style="warning" %}

**Importante:** Desafios de `PWN` normalmente são feitos para serem executados remotamente, via comando `nc`, porque as `flags` só estarão no computador dos organizadores do desafio. Porém para facilitar a análise, ó código e o `exploit` são testados localmente, e para isso é utilizado uma `fake flag` para o código não quebrar na hora de abrir o arquivo. Esse desafio não era diferente, a `flag` só seria revelada se o `exploit` fosse realizado via `nc` no IP e porta fornecidos.

{% endhint %}

### Flag
`hawk{p3Rs0n@_ta_dIF3rEnte!}`