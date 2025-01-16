import random as rand

#Converte o inteiro '1665663c' para um inteiro na base 20 (0,1,2,3,4,5,6,7,8,9,a,b,c,d,e,f,g,h,i,j)
base20 = int('1665663c', 20)
rand.seed(base20)

arquivoBin = bytearray(b"flag{tu_e_moscao}")

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
    print(ar, type(ar))
    print(ar.hex(), type(ar.hex()))
    ar = int(ar.hex(),17)
    print(ar, type(ar))
    print(int(str(ar), 10))
    for r in arr:
        ar += int(r, 35)
    print(ar)
    return bytes.fromhex(hex(ar)[2:])

arrRRrrrrRRrRRRrRrRRRRr = rand(arquivoBin, R.encode())
arrRRrrrrRRrRRRrRrRRRRr = funcModificada(lista9, arrRRrrrrRRrRRRrRrRRRRr)
print(arrRRrrrrRRrRRRrRrRRRRr.hex())
