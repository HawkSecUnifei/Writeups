# [picoCTF][General Skills] binhexa

## Description
How well can you perfom basic binary operations? Start searching for the flag
here

```
nc titan.picoctf.net 55796
```

Esse desafio inicia uma instância sob demanda.

### Terminal
```
Welcome to the Binary Challenge!"
Your task is to perform the unique operations in the given order
and find the final result in hexadecimal that yields the flag.

Binary Number 1: 11101010 
Binary Number 2: 01011101

Question 1/6: 
Operation 1 '|' 
Perform the operation on Binary Number 1&2. 
Enter the binary result:

Question 2/6: 
Operation 2 '+' 
Perform the operation on Binary Number 1&2. 
Enter the binary result: 

Question 3/6: 
Operation 3 '<<' 
Perform a left shift of Binary Number 1 by 1 bits. 
Enter the binary result:

Question 4/6: 
Operation 4 '>>' 
Perform a right shift of Binary Number 2 by 1 bits. 
Enter the binary result: 

Question 5/6: 
Operation 5 '&' 
Perform the operation on Binary Number 1&2. 
Enter the binary result:

Question 6/6: 
Operation 6 '*' 
Perform the operation on Binary Number 1&2. 
Enter the binary result: 101 0101 0000 0010

Enter the results of the last operation in hexadecimal:
```

## Solução
O exercício é bem direto ao ponto, fornecendo dois números em base binária e pedindo o resultado de seis diferentes operações. Vale notar que os números e a ordem das operações mudam a cada instância do exercício.

Usando a calculadora do Windows no modo **Programador**, obtemos os seguintes resultados:

1. **OU bit a bit (`|`)** → `11111111`
2. **Soma (`+`)** → `101000111`
3. **Deslocamento à esquerda (`<<`)** → `111010100`
4. **Deslocamento à direita (`>>`)** → `101110`
5. **E bit a bit (`&`)** → `1001000`
6. **Multiplicação (`*`)** → `101 0101 0000 0010`

Por fim, convertemos o último número para hexadecimal:

```
0x5502
```

### Flag
A flag final do desafio é:

```
picoCTF{b1tw^3se_0p3eR@tI0n_su33essFuL_6862762d}
```

### Autor da WriteUp
Membro de Investigation - Mateus Alexandre 