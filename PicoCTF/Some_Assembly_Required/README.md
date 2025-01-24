# WriteUp: Some Assembly Required
## Descrição do desafio
**Author**: Sears Schulz \
**Plataforma**: [PicoCTF](https://play.picoctf.org/practice/challenge/152?category=1&page=3) \
**Categoria**: Web Exploitation \
**Dificuldade**: Médio \
**Data**: 2021 \

## Some Assembly Required 1
Primeiramente, abrimos o link fornecido pelo desafio, http://mercury.picoctf.net:37669/index.html. Encontramos uma página html com um input e um texto *Enter the flag:*. Se procurarmos dentro dos arquivos fonte do site, encontramos uma aba **wasm** com um arquivo **adda0372**. No fim dele, estará a linha `(data (i32.const 1024) "picoCTF{a8bae10f4d9544110222c2d639dc6de6}\00\00")`. \ 
A flag é **picoCTF{a8bae10f4d9544110222c2d639dc6de6}**

## Some Assembly Required 2
Se abrirmos o link fornecido pelo desafio, http://mercury.picoctf.net:61778/index.html, encontraremos novamente uma página html com um input e um texto *Enter the flag:*. Lendo o arquivo **5655afae** na aba **wasm**, encontramos a linha `(data (i32.const 1024) "xakgK\5cNs((j:l9<mimk?:k;9;8=8?=0?>jnn:j=lu\00\00")` no fim do arquivo. Encontramos, também, a função `copy_char`. Ela é responsável por copiar a entrada do usuário para uma região específica de memória, fazendo algumas alterações nela no processo. Então, ela será comparada com a string `xakgK\5cNs((j:l9<mimk?:k;9;8=8?=0?>jnn:j=lu` na função `str_cmp`. \
Se descobrirmos uma maneria de reverter as alterações feitas na entrada do usuário, poderemos aplicar isso na string `xakgK\5cNs((j:l9<mimk?:k;9;8=8?=0?>jnn:j=lu` e obter a flag. Para isso, basta fazer uma operação de XOR 8 em cada byte da string. O código a seguir pode ser inserido no console do seu browser: 
``` javascript
p = "xakgK\5cNs((j:l9<mimk?:k;9;8=8?=0?>jnn:j=lu"
r = ""
for (let i = 0; i < p.length; i++) r += String.fromCharCode(p[i].charCodeAt() ^ 8)
```
Desse modo, acharemos a flag: **picoCTF{  b2d14eaec72c31305075876bff2b5d}**

## Autor da WriteUp
[Membro de Networking - Luiz Felipe](https://github.com/LuizF14)
