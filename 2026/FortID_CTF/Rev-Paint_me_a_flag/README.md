# WriteUp: Paint me a flag
## Descrição do desafio:
**Categoria:** Reverse Engineering \
**Descrição:** 
> It was an honor to paint this flag, I hope you'll enjoy it. Download the handout.zip!

### Arquivos
Não consegui adicionar por ser muito pesado.
| Arquivo | Descrição |
| ------- | --------- |
| handout | Imagens/ código. |
| solver.cpp | Script. |

> 📥 **Download:** [Arquivos](https://github.com/HawkSecUnifei/Writeups/raw/refs/heads/main/2026/FortID_CTF/Rev-Meteor-Shower/solve.cpp)

## Passo a Passo da Solução
### 1. Análise do arquivo fornecido

O binário é um ELF x86-64 em C++ que usa `libpng`. O uso aparece nas strings: `usage:` `paint_me_a_flag START.png OPERATIONS.pmaf OUTPUT.png`. Mensagens de erro como
"operation stream lost synchronization" e "bucket position is outside the canvas" já
indicavam operações de balde de tinta com verificação de integridade.

Cada `.pmaf` tem um cabeçalho fixo de 40 bytes (inteiros little-endian) seguido das
operações, 8 bytes cada:

| Offset | Tamanho | Campo |
| ------ | ------- | ----- |
| 0 | 8 | Magic 50 4D 41 46 03 0D 0A 1A ("PMAF" + bytes de controle) |
| 8 | 4 | Largura do canvas (1600 nas partes 02–13, 256 na arte 01) |
| 12 | 4 | Altura (600 nas partes 02–13, 96 na parte 01) |
| 16 | 8 | Número de operações (960000 = 1600×600; 24576 = 256×96) |
| 24 | 8 | Semente do hash |
| 32 | 4 | Número de "decoys" por operação (64 nas partes 02–13, 0 na parte 01) |
| 36 | 4 |Reservado (precisa ser zero) |

Cada parte tem exatamente uma operação por pixel, e o tamanho do arquivo confere: 40 +
8 × 960000 = 7680040 bytes. A parte 01 é menor (196648 bytes) e gera a imagem de
256×96 com o texto "Fort".

Os PNGs iniciais são ruído: em todos, os 960000 pixels têm cores distintas e o bit menos
significativo de cada cor é sempre zero.

### 2. Reverse do binário
Disassemblei o `.text`. As constantes `0xbf58476d1ce4e5b9` e
`0x94d049bb133111eb` identificam o finalizador do SplitMix64, que chamo de `fmix` .
Também aparecem `0x9e3779b97f4a7c15` e `0xd6e8feb86659fd93`. A função `fmix`
é:

```cpp
u64 fmix(u64 x){ x ^= x>>30; x *= 0xbf58476d1ce4e5b9; x ^= x>>27; x *=
0x94d049bb133111eb; x ^= x>>31; return x; }
```

Estado inicial. O hash de estado `S` começa a partir do cabeçalho:
```cpp
S = fmix( fmix(count) ^ seed ^ h ^ ((u64)w<<32) ^ ((u64)decoys*D) ^
0x6f3d9b21a4c875e1 );
```

Cada operação. Para a operação `i`, com `T = i·G`, lê-se 8 bytes `V` e decodifica-se:
```cpp
u = T ^ S; W = fmix(u) ^ V;
pos = W & 0xffffff; cor = (W>>24) & 0xffffff; mac = W >> 48;
// MAC de 16 bits: se falhar, "operation stream lost synchronization"
fmix( ((u64)cor<<24 | pos) ^ u ) >> 48 == mac
```

Assim, cada operação só é válida se `S` estiver correto, e `S` depende do resultado de
todas as operações anteriores.

Preenchimento (`$3370`). É um flood fill de 4 vizinhos que parte de `pos`, troca todos os
pixels conectados da cor antiga pela cor nova e devolve três estatísticas da região: o
tamanho `n`, o XOR de `fmix(p ^ 0x243f6a8885a308d3)` sobre os índices p dos pixels, e a cor antiga `oc`.

Atualização do estado. Depois de cada preenchimento, com `fmix(H)` sobre o XOR dos
pixels:
```cpp
upd(S,T,n,H,oc,c) = fmix( n*D ^ fmix(H) ^ fmix(c | (oc<<24)) ^ S ^ T )
```

Decoys: Para `j = 0..decoys-1`, o binário gera uma cor aleatória `rc = (fmix(T ^ S ^(j+1)·D) & 0xfffffe) | 1` (sempre ímpar, e se for `0xf2eadf` re-sorteia). Ele pinta a
região com `rc`, atualiza `S`, pinta de volta com a cor real e atualiza `S` de novo. No fim a
imagem não muda, mas o estado é misturado 128 vezes por operação, o que torna a
emulação ingênua muito lenta. `0xf2eadf` é a cor de fundo do texto, e as cores aleatórias
são ímpares justamente para não colidirem com o ruído, que só tem cores pares.

### 3. Solução
Qual PNG vai com qual parte? Os 12 PNGs de 1600×600 não têm nome útil. Como a
primeira operação só passa no MAC com o PNG certo, testei as 144 combinações com o
binário original e um limite de 8 segundos. Os pares errados falham na hora com
"operation stream lost synchronization"; para cada parte, exatamente um PNG passou do
limite sem falhar, e esse é o par certo. A parte 01 casa com o PNG pequeno de 256×96

```cpp
for (u64 i=0; i<count; i++, T+=G) {
    u64 V; fread(&V,8,1,g);
    u64 u = T ^ S, W = fmix(u) ^ V;
    u32 pos = W & 0xffffff, c = (W>>24) & 0xffffff;
    if ((fmix(((u64)c<<24 | pos) ^ u) >> 48) != (W>>48)) die("MAC");
    u32 r = find(pos), a = col[r];
    S = upd(S, T, sz[r], Hh[r], a, c); // preenchimento real
    if (a != c) { // recolore e funde
        lrem(r); col[r] = c;
        cand = componentes_com_cor(c) \ {r}; // lista por cor
        ladd(r);
        for (x : cand) if (adjacent(find(r), x)) unite(find(r), x);
        r = find(r);
    }
    for (j=0; j<decoys; j++) { // decoys: mesmas (n,H)
        u64 x = T ^ S ^ (j+1)*D, rc = (fmix(x) & 0xfffffe) | 1;
        while (rc == 0xf2eadf) { x = fmix(x+G); rc = (fmix(x) & 0xfffffe) |
1; }
        S = upd(S,T, sz[r],Hh[r], c, rc);
        S = upd(S,T, sz[r],Hh[r], rc, c);
    }
}
```

| Parte | Texto |
| ----- | ----- |
| 1 | Fort |
| 2 | ID{P |
| 3 | 41n7 |
| 4 | _M3_ |
| 5 | L1k3 |
| 6 | _0n3 |
| 7 | _0f_ |
| 8 | Y0ur |
| 9 | _Fr3 |
| 10 | nch_ |
| 11 | Fl4g |
| 12 | zzz! |
| 13 | !!} |

### Flag
`FortID{P41n7_M3_L1k3_0n3_0f_Y0ur_Fr3nch_Fl4g_zzz!!!}`

## Autor da WriteUp
[Membro de Exploitation - Porto](https://github.com/0xportoo)