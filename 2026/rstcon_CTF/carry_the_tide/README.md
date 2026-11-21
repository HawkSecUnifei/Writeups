# WriteUp: Carry The Tide
## Descrição do desafio:
**Categoria:** Reverse Engineering \
**Descrição:** 
> A sluice controller will only align if you give it the right control key.

**Formato da flag:** `rstcon{...}`

### Arquivos
| Arquivo | Descrição |
| ------- | --------- |
| carry | Binário ELF (SuperH SH-4). |

## Passo a Passo da Solução
### 1. Reconhecimento
O desafio fornece apenas o binário `carry`. Primeiro passo, identificar o tipo do arquivo:

```
$ file carry
carry: ELF 32-bit LSB executable, Renesas SH, version 1 (SYSV), dynamically linked,
interpreter /lib/ld-linux.so.2, not stripped
```

Pontos importantes:

- A arquitetura é SuperH (SH-4), pouco comum em CTFs, então o `objdump` e as ferramentas padrão do host não desmontam o código.
- O binário não está stripped, então os símbolos `main`, `check`, `target` e `target_len` estão disponíveis.

As strings do binário já mostram o fluxo do programa:

```
Carry the tide. Enter control key:
Sluice aligned.
Out of phase.
```

Ou seja: o programa pede uma chave, valida e imprime "Sluice aligned." (sucesso) ou "Out of phase." (falha).

### 2. Análise de main
Desmontando `main`, a lógica equivale a:

```c
printf("Carry the tide. Enter control key: ");
if (!fgets(buf, 128, stdin)) return 1;
buf[strcspn(buf, "\r\n")] = 0; // remove a quebra de linha
if (check(buf)) puts("Sluice aligned.");
else puts("Out of phase.");
```

A entrada não sofre nenhuma outra transformação antes de chegar em `check`. (Há também o canário de pilha `__stack_chk_guard`, que é só proteção padrão do GCC.)

### 3. Análise de check
Trecho principal do disassembly:

```
400744: mov.l @(0x4007fc),r1 ; r1 = &strlen
400746: jsr @r1              ; strlen(input)
400752: mov #38,r1
40075a: cmp/eq r1,r2         ; len == 38 ?
40075c: bt 0x400764          ; senão -> return 0
400766: mov #90,r2           ; 0x5a
40076a: mov.b r0,@(6,r1)     ; key = 0x5a
400772: mov.l r2,@(56,r1)    ; i = 0
; --- corpo do laço (0x400778) ---
400786: mov.b @r1,r1         ; c = input[i]
40078e: mov.b @(6,r2),r0     ; key
400792: add r3,r2            ; t = key + c
400796: mov.b r0,@(7,r1)     ; t &= 0xff (armazenado em byte)
4007a2: mov.b @r1,r1         ; target[i]
4007ae: cmp/eq r1,r2         ; t == target[i] ?
4007b0: bt 0x4007b8          ; senão -> return 0
4007c6: mov.b @r1,r2         ; key = input[i] (cadeia!)
4007d8: add #1,r2            ; i++
4007e8: cmp/ge r1,r2         ; bf loop ; while (i < len)
4007ec: mov #1,r1            ; return 1
```

Traduzindo para C:

```c
int check(const char *s) {
    if (strlen(s) != 38) return 0;
    uint8_t key = 0x5a;
    for (int i = 0; i < 38; i++) {
        uint8_t t = (uint8_t)(key + (uint8_t)s[i]);
        if (t != target[i]) return 0;
        key = (uint8_t)s[i]; // a chave vira o caractere ANTERIOR
    }
    return 1;
}
```

### 4. A vulnerabilidade lógica
O nome do desafio (*Carry the Tide*, "carregar a maré") e o nome da flag apontam para a ideia: é uma soma acumulada em que cada byte "carrega" o anterior.

O ponto-chave é que a chave de cada passo é o **texto claro** do passo anterior, não o texto cifrado. Logo, cada caractere é recuperável diretamente:

```
input[0] = (target[0] − 0x5a) mod 256
input[i] = (target[i] − input[i−1]) mod 256
```

Verificando à mão os primeiros bytes de `target` (`cc e5 e7 d7 d2 dd e9 ...`):

| i | target[i] | chave | target − chave | char |
| - | --------- | ----- | -------------- | ---- |
| 0 | 0xcc | 0x5a | 0x72 | r |
| 1 | 0xe5 | 0x72 | 0x73 | s |
| 2 | 0xe7 | 0x73 | 0x74 | t |
| 3 | 0xd7 | 0x74 | 0x63 | c |
| 4 | 0xd2 | 0x63 | 0x6f | o |
| 5 | 0xdd | 0x6f | 0x6e | n |
| 6 | 0xe9 | 0x6e | 0x7b | { |

Os 7 primeiros caracteres formam `rstcon{`, exatamente o prefixo esperado, o que confirma que a análise está correta.

### 5. Solver

```python
d = open('carry', 'rb').read()
target = d[0x95c:0x95c + 38]  # .rodata: vaddr 0x40095c -> offset 0x95c

key = 0x5a
out = bytearray()
for t in target:
    c = (t - key) & 0xff
    out.append(c)
    key = c

flag = out.decode()
print(flag)

# verificação com o algoritmo original
def check(s):
    s = s.encode()
    if len(s) != 38: return 0
    key = 0x5a
    for i, c in enumerate(s):
        if ((key + c) & 0xff) != target[i]: return 0
        key = c
    return 1

print(check(flag))  # 1
```

Saída:

```
rstcon{running_sum_unwinds_in_reverse}
1
```

### Flag
`rstcon{running_sum_unwinds_in_reverse}`

## Autor da WriteUp
[Membro de Exploitation - Porto](https://github.com/0xportoo)
