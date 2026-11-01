# WriteUp: Truck-kun
## Descrição do desafio:
**Categoria:** Reverse Engineering \
**Descrição:** 
> 頑張ってトラックくん！ ("Boa sorte, Truck-kun!")
>
> Nota: a flag é case-insensitive.

**Formato da flag:** `rstcon{...}`

### Arquivos
| Arquivo | Descrição |
| ------- | --------- |
| truck-kun.zip | Contém um único arquivo de 70 MB (`truck-kun.x86_64`). |

## Passo a Passo da Solução
### 1. Reconhecimento
O desafio entrega `truck-kun.zip`, que contém um único arquivo de 70 MB:

```
$ file truck-kun.x86_64
truck-kun.x86_64: ELF 64-bit LSB executable, x86-64, dynamically linked, stripped
```

O nome `.x86_64` e as strings do binário (`Godot Engine`, `org.godotengine.Godot`) indicam um jogo exportado pela Godot Engine. A descrição em `project.binary` confirma: "A local, single-player truck driving & delivery simulator".

Um binário de 70 MB é quase todo o runtime da engine. O que interessa é o **PCK**, o pacote de recursos do jogo, anexado ao final do ELF.

### 2. Extraindo o PCK
Procurando a assinatura `GDPC` no arquivo, apenas uma ocorrência tem cabeçalho válido, no offset `70285592`:

| Campo | Valor |
| ----- | ----- |
| Formato do PCK | 3 |
| Versão da Godot | 4.5.0 |
| Flags | 2 (offsets relativos ao início do PCK) |
| file_base | 104 |
| dir_offset | 363000 |

Com isso foi possível ler o diretório (40 arquivos) e extrair tudo com um script Python curto. Conteúdo relevante:

- `scripts/*.gdc`: Main, Truck, NPC, HUD, Waypoint (GDScript compilado);
- `.godot/exported/.../*.scn`: cenas binárias (Main, Truck, NPC, Substrate etc.);
- `audio/bgm.ogg`: música de fundo.

### 3. Decompilando o GDScript (versão 101)
Os `.gdc` começam com `GDSC`, versão 101 e o tamanho descomprimido. O corpo está comprimido com zstd (magic `28 b5 2f fd`). Sem módulo Python de zstd e sem rede, usei a `libzstd.so.1` do sistema via `ctypes` (`ZSTD_decompress`).

O formato do buffer do tokenizer, como confirmei na prática, é:

1. quatro `uint32`: nº de identificadores, constantes, linhas e tokens;
2. identificadores: tamanho + cada caractere em 4 bytes com XOR `0xb6`;
3. constantes: variants serializados em sequência (floats, strings etc.);
4. mapa de linhas e mapa de colunas (pares `token_idx → valor`);
5. tokens de 8 bytes cada: `uint32` (`tipo = raw & 0x7f`, `dado = raw >> 8`) + `uint32` com a linha.

Não há tokens de NEWLINE/INDENT: a indentação é reconstruída pelo mapa de colunas.

Um decoder de ~100 linhas recuperou o código-fonte dos cinco scripts, sem bytes sobrando, o que valida o parser. Exemplo (`Waypoint`):

```gdscript
func _on_body_entered(body: Node3D) -> void:
    if visible and body.is_in_group('player_truck'):
        truck_entered.emit()
```

O resultado: os scripts são apenas a lógica do jogo (dirigir, entregar carga entre 6 waypoints, HUD, NPCs andando aleatoriamente). Nenhuma flag nos scripts, então o segredo está nos dados das cenas.

### 4. A cena Substrate
Listando os nós de `Main.scn` aparece um nó `Substrate`. Sua cena (`Substrate.scn`) é de longe a maior (75 KB) e contém 714 nós `MeshInstance3D` chamados `P1` … `P714`, todos usando o mesmo `BoxMesh` (`BoxMesh_pixel`): cada nó é um "pixel".

Extraí as 714 `Transform3D` procurando a matriz identidade seguida da origem (3 floats). Resultado:

- `z` constante = −300;
- `y` com 7 valores distintos (de −48,4 a −40,0, passo 1,4);
- `x` de −213,5 a 212,1 em passo 1,4 → 305 colunas.

Uma grade 305 × 7 com pixels: isso é um letreiro em fonte bitmap 5×7. 305 = 51 glifos × 6 − 1 (5 colunas por glifo + 1 de espaço), e conferi que todas as colunas de espaço estão vazias.

O letreiro fica fora da área jogável, então dirigindo não dá para vê-lo. Só aparece lendo os dados da cena.

### 5. Lendo o letreiro
Renderizei a grade em ASCII (linha de cima = maior `y`, `x` crescente para a direita). Primeiros glifos:

```
####. .#### ##### .#### .###. #...# ..##.
#...# #.... ..#.. #.... #...# ##..# ..#..
#...# #.... ..#.. #.... #...# #.#.# .#...
####. .###. ..#.. #.... #...# #..## ##...
#.#.. ....# ..#.. #.... #...# #...# .#...
#..#. ....# ..#.. #.... #...# #...# ..#..
#...# ####. ..#.. .#### .###. #...# ..##.
  R     S     T     C     O     N     {
```

Para não depender de leitura à mão, comparei cada um dos 51 glifos com uma tabela de fonte 5×7 (A–Z, 0–9, `-`, `_`, `{`, `}`). Todos casaram:

```
RSTCON{REBORN-IN-ANOTHER-WORLD-BUT-IM-PLAYING-CTFS}
```

O texto aparece sem espelhamento, e as chaves `{` e `}` ficam com as pontas virando para o lado certo, o que confirma a orientação.

### 6. Resumo da solução
1. Identificar o jogo como Godot 4.5 e extrair o PCK embutido no ELF.
2. Descomprimir (zstd) e decodificar o bytecode GDScript v101: scripts sem flag.
3. Inspecionar as cenas binárias: `Substrate` guarda 714 caixas-pixel.
4. Extrair as posições, montar a grade 305×7 e decodificar a fonte 5×7 → flag.

### Flag
`rstcon{reborn-in-another-world-but-im-playing-ctfs}`

## Autor da WriteUp
[Membro de Exploitation - Porto](https://github.com/0xportoo)
