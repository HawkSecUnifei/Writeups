# WriteUp: Finders Keepers
## Descrição do Desafio
**Categoria**: Forensics

**Descrição**:
> What even is this image bruh.


### Arquivos
| Arquivo | Descrição |
| ------- | --------- |
| weird.png | Imagem fornecida. |
| ImagemExtraida.jpg | Imagem extraída. |
| AudioExtraido.wav | Aúdio extraído. |

> 📥 **Download:** [Arquivos]()

## Solução
O desafio disponibiliza a seguinte imagem.

![image](./assets/weird.png)

Se utilizarmos o site [Cyberchef](https://gchq.github.io/CyberChef/) e a operação de `Extract Files`, conseguimos retirar dois arquivos escondidos nessa imagem. Um dos arquivos é uma imagem e o outro arquivo é um aúdio.

Ao ouvir o aúdio, podemos perceber que se trata de um código morse. Ao traduzir o código morse, conseguimos a palavra `snooooooppppppp`.

Portanto, temos uma imagem e uma espécie de "senha". Com isso, podemos usar um método de esconder inforamações em imagem que é a esteganografia com senha. Pra retirar a mensagem escondida da imagem, podemos usar a
ferramenta `steghide` para decodificar a imagem com a senha `snooooooppppppp`. Pra isso, podemos usar o seguinte comando.

`steghide extract -sf ImagemExtraida.jpg -p snooooooppppppp`

Ao fazer isso, obtemos a flag.

### Flag: `BITSCTF{1_4m_5l33py_1256AE76}`

## Autor da WriteUp
[Membro de Exploitation - CaioMendesRRosa](https://github.com/CaioMendesRRosa)
