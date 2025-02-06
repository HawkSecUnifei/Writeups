# WriteUp: two-sum
## Descrição do Desafio:
**Autor**: Mubarak Mikail \
**Plataforma**: [PicoCTF](https://play.picoctf.org/practice/challenge/382?category=6&page=1) \
**Categoria**: Binary Exploitation \
**Dificuldade**: Média \
**Data**: 2023 \
**Descrição**:
> Can you solve this? \
> What two positive numbers can make this possible: n1 > n1 + n2 OR n2 > n1 + n2
## Passo a Passo da Solução
### 1. Análise do arquivo fornecido
Este desafio fornece apenas o arquivo fonte `flag.c`. Não tem muito o que ver no arquivo, pois tudo o que ele faz condiz com a descrição, devemos passar como *input* dois números inteiros e o resultado da soma dos dois deve ser menor do que um dos números passados.

{% hint style="warning" %}

**Importante:** Os dois números devem ser positivos, se eles não forem, a **flag** não será revelada.

{% endhint %}

### 2. Integer Overflow
Antes de irmos para a solução, devemos entender o que é `integer overflow`. Todos os dados primitivos tem tamanho fixo na memória do computador, no caso dos inteiros, isso faz com que haja um número máximo e mínimo que possa ser representado. Tal número pode ser cálculado por −2<sup>n-1</sup> para o número mínimo, e 2<sup>n - 1</sup> - 1 para o número máximo, sendo *n* a quantidade de bits (normalmente são 32 bits).

O `integer overflow` acontece quando qualquer operação realizada em um inteiro acaba resultando em um resultado que está fora desse limite, e em inteiros isso normalmente acaba gerando uma troca de sinais. Considere uma máquina que trabalha com inteiros de 5 bits, e que usa `signal bit` para representar se o número é positivo ou negativo, dessa forma os números são representados apenas por 4 bits, fazendo com que o número 15 seja o maior número positivo representável, com o binário sendo `01111`. Se por um acaso acontecer uma operação de 15 + 1 nessa máquina, o resultado seria `10000`, que seria interpretado como um número negativo.

### 3. Solução
Agora que sabemos como `integer overflow` funciona, podemos realizar o desafio. Basta inserir um número grande e outro número que faça a soma extrapolar o limite dos inteiros representáveis, no caso foi inserido os números `2147483647` (maior inteiro positivo representável para 32 bits) e `1`.

### Flag
`picoCTF{Tw0_Sum_Integer_Bu773R_0v3rfl0w_f6ed8057}`

## Autor da WriteUp
[Membro de Exploitation - HenriUz](https://github.com/HenriUz)
 
