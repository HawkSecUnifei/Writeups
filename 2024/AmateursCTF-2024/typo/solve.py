import random as r

#Converte o inteiro '1665663c' para um inteiro na base 20 (0,1,2,3,4,5,6,7,8,9,a,b,c,d,e,f,g,h,i,j)
base20 = int('1665663c', 20)
r.seed(base20)

#arquivoBin = bytearray(open('output.txt', 'rb').read())
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
	print(ar)
	ar = int(ar,16)
	print(ar)
	for r in arr:
		ar -= int(r, 35)
	print(ar)
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
	print(valor3[::-1])
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
