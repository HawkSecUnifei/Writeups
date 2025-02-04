# Hydraulic Press
*I'm starting a new website where we can blog about dogs!  
Could you write us an article?  
Note: The website is at http://localhost:3000/ for the xssbot.*

- *Web Exploitation*
- *Autor do writeup: [@rebane2001](https://github.com/rebane2001)*

> Você pode acessar os arquivos do desafio no nosso repositório
> <https://github.com/HawkSecUnifei/Writeups>

O desafio fornece um arquivo chamado `flag.txt`. O objetivo do desafio é decodificar e descomprimir este arquivo para descobrir a flag.

## Resolução do desafio

Analisando o arquivo `flag.txt` com o comando `file flag.txt`, obtemos:
``` console
flag.txt: ASCII text, with very long lines (65536), with no line terminators
```
Não detectamos nenhum tipo de compressão. Contudo, se o decodificarmos com **base85** por meio do código python: 
``` python
import base64
def decode(input_file, output_file):
    with open(input_file, 'rb') as fin, open(output_file, 'wb') as fout:
        encoded_data = fin.read()
        decoded_data = base64.a85decode(encoded_data)
        fout.write(decoded_data)
decode('flag.txt', 'flag1.txt')
```
E executar o comando `file flag1.txt`, obteremos:
``` console
flag1.txt: zlib compressed data
```
Descobrimos que o arquivo `flag1.txt` foi comprimido pelo zlib. Usando o código a seguir, tentemos descomprimí-lo múltiplas vezes:
``` python
import zlib
def decompress(input_file, output_file, chunk_size=1024 * 1024):
    decompressor = zlib.decompressobj()
    with open(input_file, 'rb') as fin, open(output_file, 'wb') as fout:
        while chunk := fin.read(chunk_size):
            fout.write(decompressor.decompress(chunk))
        fout.write(decompressor.flush())
decompress("flag1.txt", "flag2.txt")
decompress("flag2.txt", "flag3.txt")
decompress("flag3.txt", "flag4.txt")
decompress("flag4.txt", "flag5.txt")
```
Este código executa a descompressão um bloco de arquivo por vez (chunk), evitando assim o estouro da memória RAM. Na quarta descompressão, percebemos uma demora muito grande, bem como o uso bem alto do espaço de armazenamento. Por isso, **interrompemos o processo** antes de seu término. Examinando os bytes do arquivo `flag5.txt` por meio do comando `hexdump -C flag5.txt`, notamos uma quantidade imensa de bytes 0x00 no arquivo. Fazendo o mesmo procedimento no arquivo `flag4.txt`, notamos sequências muito longas de bytes 0xAA e 0x55. Essas sequências de bytes no arquivo `flag4.txt` são as responsáveis por gerar a vastidão de bytes 0x00 no arquivo `flag5.txt`. Sendo assim, criamos uma função que exclua essas sequências antes de descompactar o arquivo `flag4.txt`, facilitando assim o processo de descompactação:
``` python
def filter(input_file, output_file):
    with open(input_file, 'rb') as fin, open(output_file, "wb") as fout:
        data = fin.read().replace(b'\x55'*4095, b"\x55").replace(b'\xAA'*4095, b"\xAA")
        fout.write(data)

def decompress_flag(input_file, output_file, chunk_size=1024 * 1024):
    decompressor = zlib.decompressobj()

    with open(input_file, 'rb') as fin, open(output_file, 'wb') as fout:
        while chunk := fin.read(chunk_size):
            decompressed_chunk = decompressor.decompress(chunk)

            for b in decompressed_chunk:
                if b != 0x00:
                    fout.write(bytes([b]))
                if b == 0x7D: 
                    return

filter("flag4.txt", "flag5.txt")
decompress_flag("flag5.txt", "flag6.txt")
```
Criamos também uma nova função de descompressão específica para `flag5.txt`. Diferente da anterior, esta não vai escrever todos os bytes descomprimidos no arquivo de saída, mas somente aqueles que não sejam 0x00. Além disso, também foi colocada uma condição de parada para quando for encontrado os bytes 0x7D, significando que encontramos um caracter "}", ou seja, o término de uma possível flag.  
Agora, verificando o arquivo `flag6.txt`, obtemos:
```
x3c{nesting_is_fun_IDOWxzs3}
``` 
## Autor da WriteUp
[Membro de Networking - Luiz Felipe](https://github.com/LuizF14)
