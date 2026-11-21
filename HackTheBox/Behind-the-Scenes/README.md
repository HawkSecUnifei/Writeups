# WriteUp: Behind the Scenes

## Descrição do Desafio:
**Autor**: [Leeky](https://app.hackthebox.com/users/129896) \
**Plataforma**: [Hack The Box](https://app.hackthebox.com/challenges/301) \
**Categoria**: Reversing \
**Dificuldade**: Muito fácil \
**Data**: 2022 \
**Descrição**:
> After struggling to secure our secret strings for a long time, we finally figured out the solution to our problem: Make decompilation harder. It should now be impossible to figure out how our programs work!

## Passo a Passo da Solução
### 1. Análise do arquivo fornecido
O desafio fornece um executável Linux de 64 bits chamado `behindthescenes`. Executando sem argumentos, ele mostra como deve ser usado:

```bash
$ ./behindthescenes
./challenge <password>
```

E passando uma senha qualquer, o programa simplesmente termina sem imprimir nada.

Diferente de outros desafios, rodar `strings` no binário não mostra nenhuma senha. Isso acontece porque, como veremos, a senha foi quebrada em pedaços de 3 caracteres, e o `strings` só mostra sequências com 4 caracteres ou mais por padrão.

### 2. Por que o decompilador não funciona?
Abrindo o binário no **Ghidra**, a função `main()` decompilada termina logo depois de uma chamada para `sigaction()`, e no lugar do resto do código aparece apenas um `invalidInstructionException()`. Olhando o assembly, encontramos o motivo: a instrução `ud2` espalhada por toda a função.

{% code title="main (assembly)" overflow="wrap" lineNumbers="true" %}

```nasm
lea    rax, [rip+0xffffffffffffff6a]   ; segill_sigaction
mov    QWORD PTR [rbp-0xa0], rax
mov    DWORD PTR [rbp-0x18], 0x4       ; sa_flags = SA_SIGINFO
lea    rax, [rbp-0xa0]
mov    edx, 0x0
mov    rsi, rax
mov    edi, 0x4                        ; SIGILL
call   sigaction@plt
ud2
cmp    DWORD PTR [rbp-0xa4], 0x2       ; argc == 2 ?
je     130b <main+0xaa>
ud2
...
```

{% endcode %}

A `ud2` é uma instrução que existe só para gerar o erro de "instrução inválida". Quando o processador a executa, o sistema envia o sinal `SIGILL` para o programa, que normalmente seria encerrado. O Ghidra sabe disso e, por isso, entende que o código depois da `ud2` nunca é executado.

O truque está na primeira coisa que a `main()` faz: registrar a função `segill_sigaction()` como tratador do sinal `SIGILL`.

{% code title="segill_sigaction" overflow="wrap" lineNumbers="true" %}

```c
void segill_sigaction(int sig, siginfo_t *info, void *ucontext)
{
  ucontext_t *ctx = (ucontext_t *)ucontext;
  ctx->uc_mcontext.gregs[REG_RIP] += 2;
}
```

{% endcode %}

Toda vez que uma `ud2` é executada, essa função é chamada e soma 2 ao `RIP`, que é exatamente o tamanho da `ud2` (`0f 0b`). Assim, o programa pula a instrução e continua normalmente. Na prática, cada `ud2` funciona como um `nop` durante a execução, mas atrapalha completamente o decompilador.

### 3. Removendo as instruções `ud2`
Como a `ud2` não faz diferença na execução, basta trocá-las por `nop`. No Ghidra, clique com o botão direito em cada `ud2` da `main()`, escolha **Patch Instruction** e troque por dois `NOP`. Também dá para fazer isso em qualquer editor hexadecimal, trocando os bytes `0f 0b` por `90 90` dentro da `main()`.

{% hint style="info" %}

**Nota:** Não troque todas as ocorrências de `0f 0b` do arquivo. Nesse binário existe uma fora da `main()`, na seção `.eh_frame`, que não é uma instrução.

{% endhint %}

Depois do patch, o Ghidra mostra a função inteira:

{% code title="main" overflow="wrap" lineNumbers="true" %}

```c
int main(int argc, char **argv)
{
  struct sigaction act;

  memset(&act, 0, sizeof(act));
  sigemptyset(&act.sa_mask);
  act.sa_sigaction = segill_sigaction;
  act.sa_flags = SA_SIGINFO;
  sigaction(SIGILL, &act, NULL);

  if (argc != 2) {
    puts("./challenge <password>");
    return 1;
  }
  if (strlen(argv[1]) == 12 &&
      strncmp(argv[1],     "Itz", 3) == 0 &&
      strncmp(argv[1] + 3, "_0n", 3) == 0 &&
      strncmp(argv[1] + 6, "Ly_", 3) == 0 &&
      strncmp(argv[1] + 9, "UD2", 3) == 0) {
    printf("> HTB{%s}\n", argv[1]);
  }
  return 0;
}
```

{% endcode %}

Agora fica claro: a senha tem 12 caracteres e é comparada em 4 pedaços de 3. Juntando os pedaços, temos `Itz_0nLy_UD2`, e a flag é a própria senha dentro de `HTB{}`.

### 4. Exploit
Basta passar a senha como argumento:

```bash
$ ./behindthescenes Itz_0nLy_UD2
> HTB{Itz_0nLy_UD2}
```

Também dá para tirar os pedaços direto da `.rodata`, onde ficam guardados logo depois da mensagem de uso:

{% code title="solve.py" overflow="wrap" lineNumbers="true" %}

```py
from pwn import *

elf = ELF("./behindthescenes", checksec=False)

# A senha está quebrada em 4 pedaços na .rodata, logo depois da mensagem de uso
textos = elf.get_section_by_name(".rodata").data().split(b"\x00")
inicio = textos.index(b"./challenge <password>") + 1
senha = b"".join(textos[inicio:inicio + 4])

p = process([elf.path, senha])
print(p.recvall().decode())
```

{% endcode %}

### Flag
`HTB{Itz_0nLy_UD2}`

## Autor da WriteUp
[Membro de Exploitation - Matheus Inhan](https://github.com/Soon-pyt)
