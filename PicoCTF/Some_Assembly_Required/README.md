# WriteUp: Some Assembly Required
## Descrição do desafio
**Author**: Sears Schulz \
**Plataforma**: [PicoCTF](https://play.picoctf.org/practice/challenge/152?category=1&page=3) \
**Categoria**: Web Exploitation \
**Dificuldade**: Médio, Difícil \
**Data**: 2021

## Some Assembly Required 1
Primeiramente, abrimos o link fornecido pelo desafio, http://mercury.picoctf.net:37669/index.html. Encontramos uma página html com um input e um texto *Enter the flag:*. Se procurarmos dentro dos arquivos fonte do site, encontramos uma aba **wasm** com um arquivo **adda0372**. No fim dele, estará a linha `(data (i32.const 1024) "picoCTF{a8bae10f4d9544110222c2d639dc6de6}\00\00")`.  
A flag é **picoCTF{a8bae10f4d9544110222c2d639dc6de6}**

## Some Assembly Required 2
Se abrirmos o link fornecido pelo desafio, http://mercury.picoctf.net:61778/index.html, encontraremos novamente uma página html com um input e um texto *Enter the flag:*. Lendo o arquivo **5655afae** na aba **wasm**, encontramos a linha `(data (i32.const 1024) "xakgK\5cNs((j:l9<mimk?:k;9;8=8?=0?>jnn:j=lu\00\00")` no fim do arquivo. Encontramos, também, a função `copy_char`. Ela é responsável por copiar a entrada do usuário para uma região específica de memória, fazendo algumas alterações nela no processo. Então, ela será comparada com a string `xakgK\5cNs((j:l9<mimk?:k;9;8=8?=0?>jnn:j=lu` na função `str_cmp`.  
Se descobrirmos uma maneria de reverter as alterações feitas na entrada do usuário, poderemos aplicar isso na string `xakgK\5cNs((j:l9<mimk?:k;9;8=8?=0?>jnn:j=lu` e obter a flag. Para isso, basta fazer uma operação de XOR 8 em cada caractere da string. O código a seguir pode ser inserido no console do seu browser: 
``` javascript
p = "xakgK\5cNs((j:l9<mimk?:k;9;8=8?=0?>jnn:j=lu"
r = ""
for (let i = 0; i < p.length; i++) r += String.fromCharCode(p[i].charCodeAt() ^ 8)
```
Desse modo, acharemos a flag: **picoCTF{  b2d14eaec72c31305075876bff2b5d}**

## Some Assembly Required 3
Na aba **wasm**, encontramos o arquivo **371a51fe**. No final do arquivo, está a linha `(data (i32.const 1024) "\9dn\93\c8\b2\b9A\8b\c5\c6\dda\93\c3\c2\da?\c7\93\c1\8b1\95\93\93\8eb\c8\94\c9\d5d\c0\96\c4\d97\93\93\c2\90\00\00")`. Analisando a função `copy_char`, vemos que cada caractere da entrada do usuário sofre uma operação XOR com a variável var14 e, em seguida, mantêm-se somente os 8 primeiros bits. A variável var14 tem seu valor mudado a cada caractere. No entanto, isso não será um grande problema, uma vez que ela irá sempre assumir um desses valores de forma sequencial e cíclica: -19,7,-16,-89,-15. Dessa maneira, podemos criar um código que decodifique `\9dn\93\c8\b2\b9A\8b\c5\c6\dda\93\c3\c2\da?\c7\93\c1\8b1\95\93\93\8eb\c8\94\c9\d5d\c0\96\c4\d97\93\93\c2\90` para acharmos a flag. 
``` javascript
let arrFlag = ["\x9d", "n", "\x93", "\xc8", "\xb2", "\xb9", "A", "\x8b", "\xc5", "\xc6", "\xdd", "a", "\x93", "\xc3", "\xc2", "\xda", "?", "\xc7", "\x93", "\xc1", "\x8b", "1", "\x95", "\x93", "\x93", "\x8e", "b", "\xc8", "\x94", "\xc9", "\xd5", "d", "\xc0", "\x96", "\xc4", "\xd9", "7", "\x93", "\x93", "\xc2", "\x90"];
let var14 = [-19,7,-16,-89,-15];
flag = "";
for(let i = 0; i < arrFlag.length; i++) {
	flag += String.fromCharCode((arrFlag[i].charCodeAt() ^ var14[i % 5]) & 0xFF)
}
```

## Some Assembly Required 4
Na aba **wasm**, encontramos o arquivo **ba111912**. No final do arquivo, está a linha `(data (i32.const 1024) "\18j|a\118i7F[#\06fJV:\0d\1c\12/dd\11Vu\0fn\1b\068\07E\10/o?\13\02+\09^\00\00")`. Dessa vez, o foco de nossa atenção não será na função `copy_char`, mas sim na função `check_flag`. Analisando o código, vemos que ele é complicado demais para criar um algoritmo que reverta as alterações feitas na entrada do usuário.  
Entretanto, percebemos um comportamento estranho na variável var14. Se tivermos na última posição da string de entrada do usuário e se a string for de comprimento par, o valor numérico de var14 irá concordar com o caractere correspondente na string `\18j|a\118i7F[#\06fJV:\0d\1c\12/dd\11Vu\0fn\1b\068\07E\10/o?\13\02+\09^\00\00`. Se a string for de comprimento ímpar, var14 irá concordar com o próximo caractere. Por exemplo, se a entrada do usuário for "pico", var14 será 97, que corresponde ao quarto caractere da string `\18j|a\118i7F[#\06fJV:\0d\1c\12/dd\11Vu\0fn\1b\068\07E\10/o?\13\02+\09^\00\00`, que é o 'a'. Mas, se a entrada for "picoC", var14 será 56, que corresponde ao quinto caractere, que é o '8'. Desse modo, é possível fazer uma brute force da flag com o auxílio do debugger do browser.  
A flag é: **picoCTF{382f73c815f2c599d3af057a4b7ca3e2}**



## Autor da WriteUp
[Membro de Networking - Luiz Felipe](https://github.com/LuizF14)
