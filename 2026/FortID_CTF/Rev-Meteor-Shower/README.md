# WriteUp: Meteor Shower
## Descrição do desafio:
**Categoria:** Reverse Engineering \
**Descrição:** 
> Great Scott! The biggest meteor storm in the galaxy is headed straight for your sector. Note: wrap the phrase into FortID{}, and use _ to separate the words.

### Arquivos
| Arquivo | Descrição |
| ------- | --------- |
| meteor_shower.nes | Código. |

> 📥 **Download:** [Arquivos](https://github.com/HawkSecUnifei/Writeups/raw/refs/heads/main/2026/FortID_CTF/Rev-Meteor-Shower/meteor_shower.nes)

## Passo a Passo da Solução
### 1. Análise do arquivo fornecido
O arquivo é uma ROM iNES simples (mapper 0, sem bank switching), então todo o código
cabe em `$8000–$FFFF` e pode ser lido de forma linear.

As primeiras strings visíveis no binário (`LDSDNQ RGNVDQ`) são "METEOR SHOWER" com
cada letra deslocada em 1, porque a fonte grande do título começa um tile antes do ASCII.
Isso indicou que os textos são armazenados como índices de tile e não como ASCII.

Fonte pequena (tiles `$80+`). Renderizei a CHR-ROM em ASCII art e confirmei a tabela:
`$80`–`$99` = A–Z, `$00`= espaço, `$A0`–`$A9` = dígitos, `$B0`= !, `$B1`= . , `$B4`= - , `$B5`=
& . Com ela, as strings terminadas em `$FF` a partir de `$8631` ficam legíveis:

| Endereço | Texto |
| -------- | ----- |
| $863F | D-PAD TO MOVE |
| $864D | PRESS START |
| $8659 | GAME OVER |
| $866F , $8680 , $868D | MISSION COMPLETE / YOU SURVIVED / CONGRATULATIONS!
| $86AA … $8701 |EASTER EGG FOUND! GREAT JOB ON FINDING THE EASTER EGG. I HOPE YOU LIKE BACON EGGS... FIVE STRIPS ATA TIME. |

Existem portanto três finais: derrota, vitória por sobrevivência e um easter egg. Nenhum
deles imprime uma frase que sirva como flag.

### 2. Analisando easter egg
O easter egg é acionado por 95 apertos de A/B que precisam bater com um valor derivado
das tabelas de meteoros. Duas rotinas fazem isso: Coleta (`$80EF`) e Verificação (`$8158`)

```py
8162 LDA $14 ; i
AND #$07 / TAY ; i mod 8
LDA $14 / LSR×3 / TAX ; i div 8
LDA $0400,X / AND $8609,Y ; bit i do buffer (máscara 80,40,...,01)
... ; $0F = bit digitado
817D LDX $15 ; x
817F LDA $8718,X ; T1[x]
8182 EOR $8798,X ; ^ T2[x]
8185 EOR $14 ; ^ i
8187 AND #$01 ; so o bit 0
8189 EOR $0F ; ^ bit digitado
818B ORA $16 ; acumula diferencas
818F LDA $15 / CLC / ADC #$25 / AND #$7F / STA $15 ; x = (x + 0x25) mod
128
```

{% endcode %}

O índice inicial é `x = $0B` e o resultado `$16` é zero apenas se todos os bits conferem. A
saída é SEC (acerto) ou CLC (erro), e em caso de acerto o jogo faz `$04 = 4` e `$05 = 5`,
mostrando a tela do easter egg.

Como `x` avança de `0x25` (37) em módulo 128 e `gcd(37, 128) = 1` , os índices visitados
são todos distintos. Os bits 0 de `T1` e `T2` quase não afetam o jogo (a coluna usa & $FE e
a velocidade é pequena), então os autores podiam ajustá-los livremente para que a conta
resultasse na mensagem desejada.

### 3. Decodificando a mensagem

Como a verificação compara os apertos com um valor fixo, basta calcular esse valor. Extraí
T1 e T2 do PRG e rodei a fórmula para i = 0..94:

` 10010 00010 01000 00100 01101 10011 01000 00000 01111 01110 10011 00100 01101 `
` 10011 01000 00000 00100 10010 10011                                           `

São exatamente 95 bits, ou seja, 19 grupos de 5. Cinco bits comportam 32 valores, o
suficiente para um alfabeto de 26 letras. Testei as variações mais prováveis (A=0 ou A=1,
bits invertidos, ordem dos bits invertida, espaço como 0); somente uma produziu texto
legível, com A=0, B=1, …, Z=25, bit mais significativo primeiro:

| Grupo | Binário | Valor | Letra |
| ----- | ------- | ----- | ----- |
| 1-8 | 10010 00010 01000 00100 01101 10011 01000 00000| 18 2 8 4 13 19 8 0 | S C I E N T I A |
| 9-16 | 01111 01110 10011 00100 01101 10011 01000 00000 | 15 14 19 4 13 19 8 0 | P O T E N T I A |
| 17-19 | 00100 10010 10011 | 4 18 19 | E S T |

### Flag
`FortID{SCIENTIA_POTENTIA_EST}` 

## Autor da WriteUp
[Membro de Exploitation - Porto](https://github.com/0xportoo)