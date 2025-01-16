# [rev]-maybe Checker
## Autor: CaioMendesRRosa

Esse é um desafio de engenharia reversa criada para o ctf Blue Water CTF 2024. Para esse desafio, foi apenas disponibilizado o arquivo binário maybe_checker.

## Entendendo o Programa

```terminal
┌──(ata㉿vBoxKali)-[~/Videos]
└─$ ./maybe_checker
Enter the flag: abcdef
Wrong flag
```

Ao rodar o programa, ele apenas pede a flag do usuário e diz se o input está correto ou não. Então, teremos que fazer o processo de engenharia reversa para descobrir a flag a partir das verificações feitas pelo programa.

![image](https://github.com/user-attachments/assets/8f399c54-b95f-461a-8c84-2422965e2067)

Utilizando o Ghidra para realizar a análise do programa, conseguimos achar a função FUN_00401180 que é onde é impresso se a flag está correta ou errada.

## Analisando o Código

![image](https://github.com/user-attachments/assets/97cefd2d-fda0-4ee9-9f04-4bb9634270bf)


A linha de código 16 não é muito clara a princípio, porém se olharmos no código assembly podemos notar que é feita uma chamada de função nessa linha e está passando um argumento dela em RDI.

![image](https://github.com/user-attachments/assets/b331ddbf-ca3a-4222-bb07-9f4196ee4fa1)


Se analisarmos de novo essa parte do código, podemos perceber que é primeiro gerado um valor aleatório e colocado em iVar2 e então é utilizado esse valor para realizar uma operação e então deslocar DAT_00402041 (possível endereço que guarda os endereços das funções) um valor aleatório, que será sempre múltiplo 9. Além disso, é passado como argumento para essa função a variável auStack_78, que se olharmos na linha 14 podemos ver que é a variável que guarda o valor dado como entrada pelo usuário, com um deslocamento que será o valor em DAT_00402040[ ( iVar2 % 0x3c ) * 9 ], que é o valor onde se encontra os endereços das funções ( DAT_00402041 ) menos 1.

![image](https://github.com/user-attachments/assets/c6be9f48-723c-4f11-88e7-d66ca1da5fcf)



Se olharmos no lugar da memória aonde está DAT_00402040, conseguimos ver que a cada 9 espaços de memória, há um endereço de uma função e antes desse endereço um valor, que é o valor de deslocamento do input do usuário na variável auStack_78. Então, agora precisamos analisar essas funções que são chamadas aleatoriamente.

![image](https://github.com/user-attachments/assets/1b07465d-fb55-47f2-89ba-3060f112e8fc)


Essas funções, parecem realizar verificações sobre o param_1, que sabemos que é o que o usuário digitou de entrada no programa, e retorna verdadeiro ou falso. Então, essas funções é a onde programa realiza as verificações para decidir se a flag está correta ou não, então podemos anotar todas essas vericações e tentar conseguir chegar a flag original a partir dessas funções. 

Porém, ao anotar essas verificações, é necessário levar em conta o deslocamento que houve sobre a string de parâmetro da função. Então, por exemplo, se olharmos na imagem que mostra os endereços dessas funções, podemos ver que a função FUN_00401270 é chamada com 05h de deslocamento sobre o seu parâmetro. Com isso, se formos anotar essa verificação, temos que levar em conta esse deslocamento, fazendo com que a FUN_00401270 fique como `s[18] < s[19]`, sendo `s` o param_1. 

Com isso, podemos agora anotar todas essas verificações que são realizadas. Todas as equações estão abaixo:

```
s[18] < s[19]
s[18] < s[21]
s[9] < s[36]
s[37] < s[19]       
s[26] < s[24]
s[30] < s[36]
s[32] < s[19]       
s[44] < s[28]
s[8] < s[38]
s[8] < s[34]         
s[15] < s[40]             
s[42] < s[21]       
s[33] < s[14]        
s[18] < s[22]                        
s[46] < s[19]   


s[33] * s[10] == 3840        
s[20] * s[9] ==  3417             
s[43] * s[20] == 3519        
s[34] * s[32] == 2448                
s[30] * s[13] == 3570                      
s[21] * s[7] ==  6003
s[26] * s[22] == 4264
s[45] * s[25] == 4335
s[21] * s[12] == 6699
s[27] * s[13] == 3417
s[42] * s[36] == 7654   


s[28] ^ s[20] == 103   
s[9] ^ s[8] == 114        
s[36] ^ s[19] == 12        
s[14] ^ s[10] == 100            
s[14] ^ s[12] == 25
s[31] ^ s[16] == 10
s[46] ^ s[26] == 28
s[34] ^ s[6] == 100
s[20] ^ s[19] == 102
s[38] ^ s[20] == 102
s[34] ^ s[26] == 97
s[42] ^ s[34] == 101
s[31] ^ s[25] == 123
s[16] ^ s[6] ==  21
s[31] ^ s[30] == 14


s[40] + s[34] == 103
s[46] + s[31] == 150
s[45] + s[37] == 133
s[43] + s[12] == 146       
s[46] + s[10] == 126
s[25] + s[18] == 100
s[44] + s[24] == 154
s[39] + s[15] == 120
s[28] + s[10] == 132
s[30] + s[27] == 137
s[34] + s[24] == 135      
s[25] + s[22] == 103
s[15] + s[14] == 132


s[0] = 'b'; s[1] = 'w'; s[2] = 'c'; s[3] = 't'; s[4] = 'f'; s[5] = '{'; s[47] = '}'
s[11] = s[17] = s[23] = s[29] = s[35] = s[41] = '-'
s[19] = s[38]
s[8] = s[18]
s[15] = s[32]
s[25] = s[34]
```

Com essas equações temos certeza que a flag tem 48 caracteres, pois s[47] é o último digito, e temos certeza de alguns digitos, fazendo a flag que temos até agora ser:

`bwctf{_____-_____-_____-_____-_____-_____-_____}`

Como nenhum desses valores que sabemos é usado nas outras equações, teremos que descobrir um outro valor qualquer para então calcular os valores restantes.

Para descobrir o primeiro valor, podemos usar essas duas equações:

```
s[30] * s[13] == 3570
s[27] * s[13] == 3417
```

Como s[13] aparece nas duas equações, podemos olhar os divisores dos números `3570` e `3417` e tentar achar algum valor que seja divisor dos dois números. 

Os números 1, 3, 17 e 51 são divisores dos dois números, porém, como 1, 3 e 17 são números nulos na tabela ASCII que com certeza não fazem parte da flag, apenas nos resta o número 51, `então s[13] = 51`. Agora, apenas nos resta encontar os outros valores a partir de s[13].

A seguir, há todas as contas feitas para encontrar a flag:

```
s[30] * s[13] == 3570 -> s[30] * 51 == 3570 :: s[30] = 70  |  bwctf{_____-_3___-_____-_____-F____-_____-_____}

s[27] * s[13] == 3417 -> s[27] * 51 == 3417 :: s[27] = 67  |  bwctf{_____-_3___-_____-___C_-F____-_____-_____}

s[31] ^ s[30] == 14   -> s[31] ^ 70 == 14   :: s[31] = 72  |  bwctf{_____-_3___-_____-___C_-FH___-_____-_____}

s[31] ^ s[25] == 123  -> 72 ^ s[25] == 123  :: s[25] = 51  |  bwctf{_____-_3___-_____-_3_C_-FH___-_____-_____}

s[25] = s[34]         -> 51 = s[34]         :: s[34] = 51  |  bwctf{_____-_3___-_____-_3_C_-FH__3-_____-_____}

s[40] + s[34] == 103  -> s[40] + 51 == 103  :: s[40] = 52  |  bwctf{_____-_3___-_____-_3_C_-FH__3-____4-_____}

s[34] + s[24] == 135  -> 51 + s[24] == 135  :: s[24] = 84  |  bwctf{_____-_3___-_____-T3_C_-FH__3-____4-_____}

s[34] ^ s[26] == 97   -> 51 ^ s[26] == 97   :: s[26] = 82  |  bwctf{_____-_3___-_____-T3RC_-FH__3-____4-_____}

s[34] ^ s[6] == 100   -> 51 ^ s[6]  == 100  :: s[6]  = 87  |  bwctf{W____-_3___-_____-T3RC_-FH__3-____4-_____}

s[31] ^ s[16] == 10   -> 72 ^ s[16] == 10   :: s[16] = 66  |  bwctf{W____-_3__B-_____-T3RC_-FH__3-____4-_____}

s[42] ^ s[34] == 101  -> s[42] ^ 51 == 101  :: s[42] = 86  |  bwctf{W____-_3__B-_____-T3RC_-FH__3-____4-V____}

s[34] * s[32] == 2448 -> 51 * s[32] == 2448 :: s[32] = 48  |  bwctf{W____-_3__B-_____-T3RC_-FH0_3-____4-V____}

s[15] = s[32]         -> s[15] = 48         :: s[15] = 48  |  bwctf{W____-_3_0B-_____-T3RC_-FH0_3-____4-V____}

s[15] + s[14] == 132  -> 48 + s[14] == 132  :: s[14] = 84  |  bwctf{W____-_3T0B-_____-T3RC_-FH0_3-____4-V____}

s[39] + s[15] == 120  -> s[39] + 48 == 120  :: s[39] = 72  |  bwctf{W____-_3T0B-_____-T3RC_-FH0_3-___H4-V____}

s[25] + s[22] == 103  -> 51 + s[22] == 103  :: s[22] = 52  |  bwctf{W____-_3T0B-____4-T3RC_-FH0_3-___H4-V____}

s[45] * s[25] == 4335 -> s[45] * 51 == 4335 :: s[45] = 85  |  bwctf{W____-_3T0B-____4-T3RC_-FH0_3-___H4-V__U_}

s[45] + s[37] == 133  -> 85 + s[37] == 133  :: s[37] = 48  |  bwctf{W____-_3T0B-____4-T3RC_-FH0_3-_0_H4-V__U_}

s[42] * s[36] == 7654 -> 86 * s[36] == 7654 :: s[36] = 89  |  bwctf{W____-_3T0B-____4-T3RC_-FH0_3-Y0_H4-V__U_}

s[46] + s[31] == 150  -> s[46] + 72 == 150  :: s[46] = 78  |  bwctf{W____-_3T0B-____4-T3RC_-FH0_3-Y0_H4-V__UN}

s[46] + s[10] == 126  -> 78 + s[10] == 126  :: s[10] = 48  |  bwctf{W___0-_3T0B-____4-T3RC_-FH0_3-Y0_H4-V__UN}

s[28] + s[10] == 132  -> s[28] + 48 == 132  :: s[28] = 84  |  bwctf{W___0-_3T0B-____4-T3RCT-FH0_3-Y0_H4-V__UN}

s[36] ^ s[19] == 12   -> 89 ^ s[19] == 12   :: s[19] = 85  |  bwctf{W___0-_3T0B-_U__4-T3RCT-FH0_3-Y0_H4-V__UN}

s[19] = s[38]         -> 85 = s[38]         :: s[38] = 85  |  bwctf{W___0-_3T0B-_U__4-T3RCT-FH0_3-Y0UH4-V__UN}

s[25] + s[18] == 100  -> 51 + s[18] == 100  :: s[18] = 49  |  bwctf{W___0-_3T0B-1U__4-T3RCT-FH0_3-Y0UH4-V__UN}

s[8] = s[18]          -> s[8] = 49          :: s[8]  = 49  |  bwctf{W_1_0-_3T0B-1U__4-T3RCT-FH0_3-Y0UH4-V__UN}

s[20] ^ s[19] == 102  -> s[20] ^ 85 == 102  :: s[20] = 51  |  bwctf{W_1_0-_3T0B-1U3_4-T3RCT-FH0_3-Y0UH4-V__UN}

s[20] * s[9] ==  3417 -> 51 * s[9]  == 3417 :: s[9]  = 67  |  bwctf{W_1C0-_3T0B-1U3_4-T3RCT-FH0_3-Y0UH4-V__UN}

s[14] ^ s[12] == 25   -> 84 ^ s[12] == 25   :: s[12] = 77  |  bwctf{W_1C0-M3T0B-1U3_4-T3RCT-FH0_3-Y0UH4-V__UN}

s[21] * s[12] == 6699 -> s[21] * 77 == 6699 :: s[21] = 87  |  bwctf{W_1C0-M3T0B-1U3W4-T3RCT-FH0_3-Y0UH4-V__UN}

s[21] * s[7] ==  6003 -> 87 * s[7]  == 6003 :: s[7]  = 69  |  bwctf{WE1C0-M3T0B-1U3W4-T3RCT-FH0_3-Y0UH4-V__UN}

s[44] + s[24] == 154  -> s[44] + 84 == 154  :: s[44] = 70  |  bwctf{WE1C0-M3T0B-1U3W4-T3RCT-FH0_3-Y0UH4-V_FUN}

s[43] * s[20] == 3519 -> s[43] * 51 == 3519 :: s[43] = 69  |  bwctf{WE1C0-M3T0B-1U3W4-T3RCT-FH0_3-Y0UH4-VEFUN}

s[33] * s[10] == 3840 -> s[33] * 48 == 3840 :: s[33] = 80  |  bwctf{WE1C0-M3T0B-1U3W4-T3RCT-FH0P3-Y0UH4-VEFUN}
```

Portanto, ao calcular todos os valores, obtemos a flag:

## `bwctf{WE1C0-M3T0B-1U3W4-T3RCT-FH0P3-Y0UH4-VEFUN}`
