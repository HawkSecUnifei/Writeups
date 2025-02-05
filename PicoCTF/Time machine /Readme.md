# WriteUp: Time machine


## Descrição do desafio
**Author**: Jeffery John \
**Plataforma**: [PicoCTF]([https://play.picoctf.org/practice/challenge/349?category=1&difficulty=2&page=1](https://play.picoctf.org/practice/challenge/425?page=1&search=time%20mach)) \
**Dificuldade**: fácil 

---

## Descrição do Desafio
Nós é dado um arquivo e o seguinte texto:

What was I last working on? I remember writing a note to help me remember...
You can download the challenge files here:
challenge.zip


---

## Solução

### Passo 1: Analisando o challenge.zip

Ao extrair o zip recebemos a pasta "drop-in" que contem somente um arquivo de texto dentro "message.txt"

---

### Passo 2: Lendo o arquivo

Ao utilizar o comando cat no arquivo de texto recebido, conseguimos ver a seguinte mensagem "This is what I was working on, but I'd need to look at my commit history to know why..."

---

### Passo 3: Descobrindo a Flag

Utilizando a dica dada pelo texto lido "ver o historico de commit" utilizamos o comando `git reflog` dentro da pasta extraida para ver o que nos retorna.

Ao utilizar o comando, nos é retornado que o usuario `b92bdd8` havia feito um commit inicial `picoCTF{t1m3m@ch1ne_5cde9075}` que no caso é a flag procurada

---

**Flag Final:** `picoCTF{t1m3m@ch1ne_5cde9075}`

## Autor da WriteUp
[Membro de Exploitation - BrunoVinicius]([https://github.com/gabrielhdsalves](https://github.com/BrunoVinicius-1))
