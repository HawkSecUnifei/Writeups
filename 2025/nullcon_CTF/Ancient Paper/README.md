# WriteUp: Profound thought
## Descrição do Desafio
**Categoria**: misc

**Descrição**:
> I found this ancient artifact stuck in an old machine
>
> labeled "29". But what is its purpose?


### Arquivos
| Arquivo | Descrição |
| ------- | --------- |
| ancient-paper.jpg | Imagem fornecida. |

> [Imagem](https://github.com/HawkSecUnifei/Writeups/raw/refs/heads/main/2025/nullcon_CTF/Ancient%20Paper/ancient-paper.jpg)

## Solução
O desafio disponibiliza a seguinte imagem.

![image](./ancient-paper.jpg)

Essa imagem se trata de um cartão perfurado. O cartão perfurado possui diversas fileiras e cada combinação de pontos marcados nessas fileiras representa um símbolo, sendo um símbolo por coluna. Portanto, a primeira coisa
que precisamos fazer é traduzir os furos para os símbolos correspondentes. Podemos usar essa imagem para decodificar os furos.

![image](./assets/punch-card.png)

Traduzindo obtemos a mensagem `1337 FORMAT("ENO?H0LL3R1TH_3NC0D3D_F0RTR4N?") = PRINT 1337` (As interrogações são de combinações de furos que não possuem símbolos associadas à elas)

Pronto, basta apenas substitituir os pontos de interrogações pelas chaves e obtemos a nossa flag.

### Flag: `ENO{H0LL3R1TH_3NC0D3D_F0RTR4N}`

## Autor da WriteUp
[Membro de Exploitation - CaioMendesRRosa](https://github.com/CaioMendesRRosa)
