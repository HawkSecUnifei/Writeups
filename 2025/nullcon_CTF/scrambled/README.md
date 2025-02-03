# WriteUp: scrambled

## Descrição do Desafio:
Categoria: rev \
Descrição:
> I am so close to finding the secret of immortality, however the code has been lost for ages.
> 
> I managed to get all the parts back and even got to know that the key to success is one bite of the forbidden fruit (the scrambled eggs!).
> 
> Can you help me to decipher the rest?



### Arquivos
| Arquivo | Descrição |
| ------- | --------- |
| main.py | Código fonte do output.txt. Porém sem a flag e a key. |
| solve.py | Código em python que resolve a flag. |
| output.txt | Output gerado pelo main.py. |

> 📥 **Download:** [Arquivos](https://github.com/HawkSecUnifei/Writeups/raw/refs/heads/main/2025/nullcon_CTF/scrambled/arquivos.zip)

## Passo a Passo da Solução
### 1. Análise do arquivo fornecido
O desafio fornece tanto o *output* quanto o código em Python que o gerou. O primeiro passo é analisar esse código para entender como o *output* foi produzido.

```py
import random

def encode_flag(flag, key):
    xor_result = [ord(c) ^ key for c in flag] 

    chunk_size = 4
    chunks = [xor_result[i:i+chunk_size] for i in range(0, len(xor_result), chunk_size)] 
    seed = random.randint(0, 10) 
    random.seed(seed) 
    random.shuffle(chunks) 
    
    scrambled_result = [item for chunk in chunks for item in chunk] 
    return scrambled_result, chunks

def main():
    flag = "REDACTED"
    key = "the scrambled eggs!"

    scrambled_result, _ = encode_flag(flag, key)
    print("result:", "".join([format(i, '02x') for i in scrambled_result]))


if __name__ == "__main__":
    main()
```

Analisando o código, podemos ver que ele é relativamente simples. Ele recebe a *flag* e a *key*, dois valores que desconhecemos, e os passa para a função `encode_flag()`.

Essa função executa os seguintes passos:
- Aplica a operação XOR entre cada caractere da *flag* com a *key*.
- Divide o resultado do XOR em *chunks* de 4 elementos cada.
- Embaralha os chunks usando `random.shuffle()`, com uma *seed* aleatória entre 0 e 10.
- Reconstrói uma lista única a partir dos *chunks* embaralhados.

Por fim, a `main()` imprime o resultado no formato hexadecimal.

### 2. Solução
A solução consiste em refazer os passos, mas na ordem reversa. A parte mais desafiadora é reverter o *shuffle*.

Primeiramente, devemos converter o *output* hexadecimal para seus valores decimais e agrupá-los em *chunks* de 4 elementos.

Em seguida, precisamos desfazer o *shuffle*. Como operações aleatórias com a mesma *seed* sempre geram o mesmo resultado, podemos simular o embaralhamento dos *chunks*, mas ao invés de usar os elementos diretamente, usaremos seus índices. Dessa forma, podemos reconstruir a ordem original dos *chunks*.

Por exemplo, olhe para uma lista de *chunks* antes e depois do *shuffle*:

```
Índices originais:  [0, 1, 2, 3]  
Após o shuffle:      [3, 2, 0, 1] 
```

Isso significa que o *chunk* na terceira posição (índice 2) originalmente estava na primeira posição (índice 0), e assim por diante.

Por fim, basta desfazer o XOR, o que é simples, pois conhecendo dois elementos da operação podemos descobrir o terceiro.

```
a XOR b = c  
Logo, a XOR c = b 
```

Para descobrir a *key*, podemos assumir que o 4º caractere da *flag* é `{`, pois as *flags* estão no formato `ENO{...}`. Dessa forma, basta aplicar o XOR entre `{` e o quarto caractere decodificado para obter a *key*.

```py
import random

def decode_scrambled(scrambled_result, chunk_size=4):
    # Recriando a lista de chunks após o shuffle.
    num_chunks = len(scrambled_result) // chunk_size
    scrambled_chunks = [scrambled_result[i:i+chunk_size] for i in range(0, len(scrambled_result), chunk_size)]
    
    # Testando todas as seeds possíveis.
    for seed in range(11):
        random.seed(seed)
        
        # O shuffle embaralha os elementos da lista. Para revertermos ele, devemos refazer o shuffle mas ao invés de usarmos os
        # elementos, usaremos índices, pois com a mesma seed o resultado do embaralhamento será o mesmo e com isso saberemos qual
        # elemento estava em qual posição.
        indices = list(range(num_chunks))  # Índices originais dos chunks
        random.shuffle(indices)  # Aplicando o shuffle nos índices
        
        # Criando uma lista vazia para os chunks ordenados corretamente.
        reordered_chunks = [None] * num_chunks

        # Reorganizando os chunks na ordem correta.
        for i, shuffled_index in enumerate(indices):
            reordered_chunks[shuffled_index] = scrambled_chunks[i]

        # Juntando os chunks de volta.
        reordered_result = [item for chunk in reordered_chunks for item in chunk]

        # Revertendo o XOR. Para isso é necessário a key utilizada, mas podemos descobrir ela por assumindo que o 4º caractere é '{'.
        key = reordered_result[3] ^ ord('{')
        flag = [reordered_result[i] ^ key for i in range(len(reordered_result))]
        print("".join(chr(b) for b in flag))

    return

def main():
    result = "1e78197567121966196e757e1f69781e1e1f7e736d6d1f75196e75191b646e196f6465510b0b0b57"
    
    # Refazendo a scrambled_result, ou seja, convertendo os pares hexadecimais do output.txt para seus valores decimais.
    scrambled_result = [int(result[i:i+2], 16) for i in range(0, len(result), 2)]
    decode_scrambled(scrambled_result)

if __name__ == "__main__":
    main()

```

### Flag
`Flag: ENO{5CR4M83L3D_3GG5_4R3_1ND33D_T45TY!!!}`

## Autor
[Membro de Exploitation - HenriUz](https://github.com/HenriUz)
