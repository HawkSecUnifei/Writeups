# Secure Password Database

**Autor:** Philip Thayer \
**Plataforma:** CyLab (picoCTF) \
**Categoria:** Engenharia Reversa \
**Dificuldade:** Médio\
**Data:** 2026

## Descrição do desafio

> I made a new password authentication program that even shows you the password you entered saved in the database! Isn't that cool?

## 1. Análise do arquivo fornecido

O desafio disponibiliza um único binário, `system.out`, um ELF 64-bit não stripped. Como os símbolos não foram removidos, é possível listar as funções diretamente com `nm`:

```
00000000000013d0 T main
000000000000135e T make_secret
0000000000001309 T hash
```

Rodando `strings` no binário, alguns trechos chamam atenção, em especial o nome do arquivo fonte original, `heartbleed.c`, referência direta à vulnerabilidade Heartbleed (CVE-2014-0160), e os prompts que o programa exibe:

```
Please set a password for your account:
How many bytes in length is your password?
You entered: %d
Your successfully stored password:
Enter your hash to access your account!
```

Executando o binário localmente, o fluxo observado é: o programa pede uma senha, pergunta quantos bytes ela tem, imprime de volta essa quantidade de bytes do "banco de dados" interno, e por fim pede um número identificado como "hash" para liberar o acesso e ler `flag.txt`.

Analisando o pseudo-código de `main` no Ghidra, ficam claros os detalhes internos:

```c
local_110 = calloc(0x5a,1);
for (local_118 = 0; local_118 < 0xd; local_118++)
    local_110[local_118 + 0x3c] = obf_bytes[local_118] ^ 0xaa;

strcpy(local_110, acStack_b9 + 1);

for (local_128 = 0; local_128 <= (int)uVar1 && local_128 < 0x5a; local_128++)
    printf("%d ", local_110[local_128]);
```

`local_110` é um buffer de 90 bytes (`0x5a`) alocado no heap. Antes mesmo do usuário digitar qualquer coisa, o loop inicial já grava ali um valor ofuscado (XOR com `0xaa`) a partir do offset `0x3c` (60), vindo do array global `obf_bytes`. Em seguida, `strcpy` copia a senha digitada (`acStack_b9 + 1`) para o início desse mesmo buffer. Por fim, o loop com `local_128` imprime de volta `uVar1` bytes do buffer, valor esse lido diretamente do que o usuário digitou como "comprimento", sem qualquer validação contra o tamanho real da senha.

---

## 2. Identificando a vulnerabilidade

O ponto chave está no trecho que lê o comprimento informado pelo usuário e o usa diretamente como limite do loop de impressão:

```c
puts("How many bytes in length is your password?");
fgets(local_d8, 0x14, stdin);
uVar1 = atoi(local_d8);

for (local_128 = 0; (local_128 <= (int)uVar1 && local_128 < 0x5a); local_128++)
    printf("%d ", local_110[local_128]);
```

`uVar1` é obtido diretamente de `atoi(local_d8)`, ou seja, é um número controlado inteiramente pelo usuário. O programa usa esse valor como limite superior do loop de impressão, sem checar se ele corresponde ao tamanho real da senha armazenada. Basta informar um número maior (por exemplo, 80) para o loop avançar além da senha e vazar memória adjacente do buffer, incluindo o dado ofuscado plantado no offset `0x3c`. Essa é exatamente a mesma classe de falha do Heartbleed real: um buffer over-read causado por um campo de tamanho não confiável.

O segundo ponto chave está em duas funções:

```c
long hash(byte *param_1)
{
    byte *local_20;
    long local_10;

    local_10 = 0x1505;
    local_20 = param_1;
    while( true ) {
        if (*local_20 == 0) break;
        local_10 = (long)(int)(uint)*local_20 + local_10 * 0x21;
        local_20 = local_20 + 1;
    }
    return local_10;
}
```

`hash()` implementa o algoritmo djb2: começa com a seed 5381 (`0x1505`) e, para cada byte da string, atualiza o valor acumulado multiplicando por 33 (`0x21`) e somando o byte atual, até encontrar o terminador nulo.

```c
void make_secret(long param_1)
{
    long local_10;

    for (local_10 = 0; obf_bytes[local_10] != '\0'; local_10 = local_10 + 1) {
        *(byte *)(local_10 + param_1) = obf_bytes[local_10] ^ 0xaa;
    }
    *(undefined1 *)(param_1 + 0xc) = 0;
    hash(param_1);
    return;
}
```

`make_secret()` reconstrói o valor original a partir de `obf_bytes` (o mesmo processo de XOR usado na inicialização do buffer em `main`), garante um terminador nulo na posição 12 e, por fim, chama `hash()` sobre esse conteúdo decodificado. Embora `make_secret` seja declarada `void`, em `main` seu "retorno" é usado (`local_f8 = make_secret(...)`); isso acontece porque o valor de retorno de `hash()` continua no registrador RAX quando `make_secret` termina, e o Ghidra captura esse valor residual. Na prática, `local_f8` é o hash esperado desse conteúdo.

A verificação final em `main` é simplesmente:

```c
local_100 = strtoul(acStack_b9 + 1, &local_120, 10);
local_f8 = make_secret(local_e5);
if (local_f8 == local_100) {
    // abre e imprime flag.txt
}
```

Ou seja: o mesmo bug de over-read que vaza o dado ofuscado também fornece tudo que é necessário para calcular, de forma determinística, o valor de "hash" esperado, sem qualquer necessidade de força bruta.

---

## 3. Exploit final

O exploit consiste em três passos:

### Passo 1: Vazar o dado ofuscado

Olhando de novo o trecho de `main` que inicializa o buffer:

```c
local_110 = calloc(0x5a,1);
for (local_118 = 0; local_118 < 0xd; local_118++)
    local_110[local_118 + 0x3c] = obf_bytes[local_118] ^ 0xaa;
```

`local_110` tem 90 bytes (`0x5a`) no total, e os 13 bytes ofuscados (`0xd`) são gravados a partir do offset `0x3c`, ou seja, 60 em decimal, ocupando os índices 60 até 72. Para que o loop de impressão alcance esse trecho, o valor informado em "How many bytes in length is your password?" precisa ser pelo menos 72. Usei 80 para ter uma margem confortável.

Rodando o binário com uma senha qualquer (`teste`) e comprimento `80`, a saída obtida foi:

```
Please set a password for your account:
How many bytes in length is your password?
You entered: 80
Your successfully stored password:
116 101 115 116 101 10 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 105 85 98 104 56 49 33 106 42 104 110 33 -86 0 0 0
0 0 0 0 0
```

Os primeiros valores (`116 101 115 116 101 10`) correspondem exatamente à senha digitada, `"teste\n"`, em código ASCII (t=116, e=101, s=115, t=116, e=101, \n=10). Depois vem uma sequência de zeros, o restante do buffer, que o `calloc` inicializa zerado e que nunca foi escrito. Só a partir do índice 60 aparecem os 13 bytes de interesse:

```
105 85 98 104 56 49 33 106 42 104 110 33 -86
```

Como o próprio `main` já aplica o XOR com `0xaa` antes de armazenar esses bytes no buffer (`obf_bytes[i] ^ 0xaa`), o que vaza é diretamente o valor decodificado, não é necessário aplicar nenhum XOR adicional depois de ler. Convertendo cada número para seu caractere ASCII correspondente:

| Decimal | 105 | 85 | 98 | 104 | 56 | 49 | 33 | 106 | 42 | 104 | 110 | 33 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Caractere | i | U | b | h | 8 | 1 | ! | j | * | h | n | ! |

Concatenando: `iUbh81!j*hn!`.

O 13º valor, `-86` (equivalente a `0xAA` em byte com sinal), não faz parte do conteúdo real: ele é só o resultado de aplicar XOR `0xaa` sobre um byte terminador nulo (`0 ^ 0xaa = 0xaa`), usado internamente pelo array `obf_bytes` para marcar o fim da string, por isso ele é descartado na reconstrução.

### Passo 2: Calcular o hash djb2 dessa string, usando o mesmo algoritmo de `hash()`

```python
secret = "iUbh81!j*hn!"
h = 0x1505
for c in secret:
    h = (ord(c) + h * 0x21) & 0xFFFFFFFFFFFFFFFF
print(h)
```

O resultado é `15237662580160011234`.

### Passo 3: Enviar o hash calculado

No prompt "Enter your hash to access your account!". Como `local_f8 == local_100` passa a ser verdadeiro, o programa abre `flag.txt` e imprime seu conteúdo.

## Flag

```
picoCTF{d0nt_trust_us3rs}
```

---

**Autora da WriteUp:** [Membro de Exploitation - lieserl](https://github.com/lieserl-git)
