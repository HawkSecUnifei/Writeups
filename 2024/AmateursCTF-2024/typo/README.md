# [rev]-typo
## Autor: HenriUz

## Analisando o desafio
Ao olhar para o desafio temos dois arquivos para serem baixados, o primeiro é um arquivo `.py` e o segundo um `.txt`.

mian.py:
```py
import random as RrRrRrrrRrRRrrRRrRRrrRr
RrRrRrrrRrRRrrRRrRRrRrr = int('1665663c', 20)
RrRrRrrrRrRRrrRRrRRrrRr.seed(RrRrRrrrRrRRrrRRrRRrRrr)
arRRrrRRrRRrRRRrRrRRrRr = bytearray(open('flag.txt', 'rb').read())
arRRrrRrrRRrRRRrRrRRrRr = '\r'r'\r''r''\\r'r'\\r\r'r'r''r''\\r'r'r\r'r'r\\r''r'r'r''r''\\r'r'\\r\r'r'r''r''\\r'r'rr\r''\r''r''r\\'r'\r''\r''r\\\r'r'r\r''\rr'
arRRrrRRrRRrRrRrRrRRrRr = [
    b'arRRrrRRrRRrRRrRr',
    b'aRrRrrRRrRr',
    b'arRRrrRRrRRrRr',
    b'arRRrRrRRrRr',
    b'arRRrRRrRrrRRrRR'
    b'arRRrrRRrRRRrRRrRr',
    b'arRRrrRRrRRRrRr',
    b'arRRrrRRrRRRrRr'
    b'arRrRrRrRRRrrRrrrR',
]
arRRRrRRrRRrRRRrRrRRrRr = lambda aRrRrRrrrRrRRrrRRrRrrRr: bytearray([arRrrrRRrRRrRRRrRrRrrRr + 1 for arRrrrRRrRRrRRRrRrRrrRr in aRrRrRrrrRrRRrrRRrRrrRr])
arRRrrRRrRRrRRRrRrRrrRr = lambda aRrRrRrrrRrRRrrRRrRrrRr: bytearray([arRrrrRRrRRrRRRrRrRrrRr - 1 for arRrrrRRrRRrRRRrRrRrrRr in aRrRrRrrrRrRRrrRRrRrrRr])
def arRRrrRRrRRrRrRRrRrrRrRr(hex):
    for id in range(0, len(hex) - 1, 2):
        hex[id], hex[id + 1] = hex[id + 1], hex[id]
    for list in range(1, len(hex) - 1, 2):
        hex[list], hex[list + 1] = hex[list + 1], hex[list]
    return hex
arRRRRRRrRRrRRRrRrRrrRr = [arRRrrRRrRRrRrRRrRrrRrRr, arRRRrRRrRRrRRRrRrRRrRr, arRRrrRRrRRrRRRrRrRrrRr]
arRRRRRRrRRrRRRrRrRrrRr = [RrRrRrrrRrRRrrRRrRRrrRr.choice(arRRRRRRrRRrRRRrRrRrrRr) for arRrrrRRrRRrRRRrRrRrrRr in range(128)]
def RrRrRrrrRrRRrrRRrRRrrRr(arr, ar):
    for r in ar:
        arr = arRRRRRRrRRrRRRrRrRrrRr[r](arr)
    return arr
def arRRrrRRrRRrRrRRrRrrRrRr(arr, ar):
    ar = int(ar.hex(), 17)
    for r in arr:
        ar += int(r, 35)
    return bytes.fromhex(hex(ar)[2:])
arrRRrrrrRRrRRRrRrRRRRr = RrRrRrrrRrRRrrRRrRRrrRr(arRRrrRRrRRrRRRrRrRRrRr, arRRrrRrrRRrRRRrRrRRrRr.encode())
arrRRrrrrRRrRRRrRrRRRRr = arRRrrRRrRRrRrRRrRrrRrRr(arRRrrRRrRRrRrRrRrRRrRr, arrRRrrrrRRrRRRrRrRRRRr)
print(arrRRrrrrRRrRRRrRrRRRRr.hex())
```

output.txt:
```
5915f8ba06db0a50aa2f3eee4baef82e70be1a9ac80cb59e5b9cb15a15a7f7246604a5e456ad5324167411480f893f97e3
```

## Analisando o código
Para resolver esse desafio primeiro a gente deve dar um jeito de entender o código `mian.py`, ele obviamente é quem deixa a `flag` igual à saída do `output.txt`, e minha abordagem para entender esse código foi renomear todas as variáveis.

main.py:
```py
import random as rand

#Setando a seed.
base20 = int('1665663c', 20)
rand.seed(base20)

#Abrindo o arquivo .txt
arquivoBin = bytearray(open('flag.txt', 'rb').read())

R = '\r'r'\r''r''\\r'r'\\r\r'r'r''r''\\r'r'r\r'r'r\\r''r'r'r''r''\\r'r'\\r\r'r'r''r''\\r'r'rr\r''\r''r''r\\'r'\r''\r''r\\\r'r'r\r''\rr'

lista9 = [
    b'arRRrrRRrRRrRRrRr',
    b'aRrRrrRRrRr',
    b'arRRrrRRrRRrRr',
    b'arRRrRrRRrRr',
    b'arRRrRRrRrrRRrRR'
    b'arRRrrRRrRRRrRRrRr',
    b'arRRrrRRrRRRrRr',
    b'arRRrrRRrRRRrRr'
    b'arRrRrRrRRRrrRrrrR',
]

func1L = lambda param: bytearray([pos + 1 for pos in param])

func2L = lambda param: bytearray([pos - 1 for pos in param])

def func(hex):
    for id in range(0, len(hex) - 1, 2):
        hex[id], hex[id + 1] = hex[id + 1], hex[id]
    for list in range(1, len(hex) - 1, 2):
        hex[list], hex[list + 1] = hex[list + 1], hex[list]
    return hex

listaF = [func, func1L, func2L]
listaF = [rand.choice(listaF) for pos in range(128)]

def rand(arr, ar):
    for r in ar:
        arr = listaF[r](arr)
    return arr

def funcModificada(arr, ar):
    ar = int(ar.hex(),17)
    for r in arr:
        ar += int(r, 35)
    return bytes.fromhex(hex(ar)[2:])

arrRRrrrrRRrRRRrRrRRRRr = rand(arquivoBin, R.encode())
arrRRrrrrRRrRRRrRrRRRRr = funcModificada(lista9, arrRRrrrrRRrRRRrRrRRRRr)
print(arrRRrrrrRRrRRRrRrRRRRr.hex())
```
Com as variáveis renomeadas fica bem mais fácil entender o que esse código faz, vale notar que o código reutiliza variáveis em certos momentos, mas isso não faz uma grande diferença para nós. Olhando o código podemos ver que o código pega a `flag` e faz uma série de operações em cima dela.

A função `rand` recebe como parâmetro a `flag` e uma string convertida pelo `.encode()`, essa função tem acesso à uma lista que contém 3 funções, em que 2 funções servem para aumentar ou diminuir 1 de cada valor da `flag` (`func1L` e `func2L`) e a outra troca as posições da `flag`. Note que quando eu me refiro à `flag` eu estou me referindo ao seu valor no `bytearray` gerado com a função `open`. Com acesso à essas 3 funções, a função `rand` usa um `for` para percorrer o segundo parâmetro, e com isso é usado a variável do `for` para escolher qual função da lista de função será usado na `flag`. Por fim é retornado a `flag`.

A função `funcModificada` recebe 2 parâmetros, o primeiro é uma lista com 9 strings de bytes, e o segundo é o `bytearray` da `flag`. A função começa convertendo o `bytearray` para um inteiro em `base 17`, e em seguida faz um `for` percorrendo o primeiro parâmetro e converte cada valor da lista para `base 35` e soma com o inteiro gerado na `base 17`. Por fim retorna o resultado de todas as somas em bytes.

## Resolução
Para resolver precisamos fazer todo o processo inverso. Primeiramente setamos a `seed` do `random` para ficar igual à `seed` no código `main.py`, porque com a mesma `seed` qualquer valor gerado aleatóriamente no nosso computador será igual aos valores gerados aleatorimente na geração do `output.txt`. Depois precisamos criar as variáveis que não são modificadas e que são usadas nas funções, elas são a string `R` (que é usada com o `.encode()`), a `lista9` (que contém as strings de bytes) e abrimos a `flag` com a função `open`.

Após criarmos as variáveis, precisamos modificar as funções. A função `func1L` nós só preisamos modificar o `+ 1` para `- 1`, a função `func2L` segue a mesma lógica, só precisamos modificar o `- 1` para `+ 1`, e a função `func` só precisamos trocar a ordem dos `for`. 

A função `funModificada` é a mais complicada, preisamos transformar nosso `bytearray` em inteiro (usando `base 16` pelo `output.txt` estar em hexadecimal), após isso subtraímos o valor das strings de bytes convertidas em `base 35` do nosso inteiro, e agora a função complica, precisamos fazer o processo inverso de converter para `base 17` e para isso precisamos fazer diversas divisão por 17 e vamos salvando o resto até o valor ser menor do que 17, no fim verificamos se sobrou algum valor no inteiro e salvamos ele. O método escolhido para resolver isso foi usando uma string (por ser mais fácil de concatenar) e um `while` que ficará em loop até o inteiro ficar menor que 17. No `while` é verificado se o resto por 17 esta entre 10 e 16 para caso isso acontece nós colocamos o valor correspondente em hexadecimal e caso contrário é só colocar o resto, depois fazemos o inteiro ser ele mesmo dividido por 17. Após o while verificamos se sobrou algo no inteiro e no fim invertemos a string e retornamos ela convertida para bytes.

A função `rand` continua a mesma coisa, pois modificamos as funções que ela utiliza acima.

```py
import random as r

#Converte o inteiro '1665663c' para um inteiro na base 20 (0,1,2,3,4,5,6,7,8,9,a,b,c,d,e,f,g,h,i,j)
base20 = int('1665663c', 20)
r.seed(base20)

R = '\r'r'\r''r''\\r'r'\\r\r'r'r''r''\\r'r'r\r'r'r\\r''r'r'r''r''\\r'r'\\r\r'r'r''r''\\r'r'rr\r''\r''r''r\\'r'\r''\r''r\\\r'r'r\r''\rr'

lista9 = [
    b'arRRrrRRrRRrRRrRr',
    b'aRrRrrRRrRr',
    b'arRRrrRRrRRrRr',
    b'arRRrRrRRrRr',
    b'arRRrRRrRrrRRrRR'
    b'arRRrrRRrRRRrRRrRr',
    b'arRRrrRRrRRRrRr',
    b'arRRrrRRrRRRrRr'
    b'arRrRrRrRRRrrRrrrR',
]


flag = bytearray(open('output.txt', 'rb').read())

    
def revFuncModificada(arr, ar):
	ar = int(ar,16)
	for r in arr:
		ar -= int(r, 35)
	valor3 = ''
	while ar >= 17:
		if str(ar%17) == '16':
			valor3 += '1f'
		elif str(ar%17) == '15':
			valor3 += 'f'
		elif str(ar%17) == '14':
			valor3 += 'e'
		elif str(ar%17) == '13':
			valor3 += 'd'
		elif str(ar%17) == '12':
			valor3 += 'c'
		elif str(ar%17) == '11':
			valor3 += 'b'
		elif str(ar%17) == '10':
			valor3 += 'a'
		else:
			valor3 += str(ar%17)
		ar = ar//17
	if str(ar) == '16':
		valor3 += '1f'
	elif str(ar) == '15':
		valor3 += 'f'
	elif str(ar) == '14':
		valor3 += 'e'
	elif str(ar) == '13':
		valor3 += 'd'
	elif str(ar) == '12':
		valor3 += 'c'
	elif str(ar) == '11':
		valor3 += 'b'
	elif str(ar) == '10':
		valor3 += 'a'
	else:
		valor3 += str(ar)
	return bytes.fromhex(valor3[::-1])

func1L = lambda param: bytearray([pos - 1 for pos in param])

func2L = lambda param: bytearray([pos + 1 for pos in param])

def func(hex):
    for list in range(1, len(hex) - 1, 2):
        hex[list], hex[list + 1] = hex[list + 1], hex[list]
    for id in range(0, len(hex) - 1, 2):
        hex[id], hex[id + 1] = hex[id + 1], hex[id]
    return hex

listaF = [func, func1L, func2L]
listaF = [r.choice(listaF) for pos in range(128)]

def rand(arr, ar):
	for r in ar:
		arr = listaF[r](arr)
	return arr

fg = revFuncModificada(lista9, flag)
fg = rand(bytearray(fg), R.encode())
print(fg)
```

## Resultado
`amateursCTF{4t_l3ast_th15_fl4g_isn7_misspelll3d}`
