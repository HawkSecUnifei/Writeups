# WriteUp: TSN

## Descrição do Desafio

**Categoria:** reversing / crypto

**Descrição:**

> I really like my calculator ... fr :/

### Arquivos

| Arquivo | Descrição |
| --- | --- |
| pink.tns | Documento da calculadora contendo o programa principal. |
| lib_pink.tns | Biblioteca contendo o alfabeto personalizado. |

## Passo a Passo da Solução

### 1. Análise do Arquivo Fornecido

Ao analisar os arquivos `pink.tns` e `lib_pink.tns`, identificamos que se tratam de documentos utilizados por calculadoras da linha **TI-Nspire**.

Embora o desafio mencione o uso de uma calculadora na descrição, os arquivos `.tns` são contêineres que armazenam scripts em Python, dispensando a necessidade de executá-los em um dispositivo físico ou emulador.

Ao inspecionar e extrair o conteúdo de `pink.tns`, encontramos o arquivo `pink.py`:

```python
import lib_pink as pinkctf

e = pinkctf.get("alphabet")
c = "62 22 28 12 31 0 43 3 25 5 35 5 3 20 48 26 24 10 5 26 60 46 29 60 35 48 5 20 5 59 60 46 25 10 5 46 50 5 48 57 5 50 10 59 5 23 35 24 23 43 24 35 25 46 60 61"

if c == "":
    c = input("Ciphertext: ")

f = ""
for n in c.split():
    f += e[int(n)]

print(f)

```

### 2. Análise da Biblioteca e do Alfabeto

O arquivo `lib_pink.tns` contém o módulo `lib_pink.py`, responsável por fornecer o alfabeto utilizado na substituição:

```python
alphabet = "jXOsE_Q7YB32KVqRGFUx15IcltpCNg8{HMz49baWkiTud60vmhnLAoSZDyewr}PJf"

def get(list_name):
    if list_name == "alphabet":
        return alphabet

```

Nesta lógica é possível notar que:

1. O desafio utiliza um alfabeto personalizado de 64 caracteres ordenados de forma pseudo-aleatória.
2. A string criptografada `c` é composta por uma sequência de números separados por espaço.
3. Cada número representa o índice numérico exato do caractere correspondente dentro da string `alphabet`.

### 3. Análise da Decodificação

A função de reconstrução da mensagem realiza as seguintes etapas:

1. `c.split()` divide a string de ciphertext em uma lista de strings numéricas.
2. `int(n)` converte cada elemento numérico para o tipo inteiro.
3. `e[int(n)]` busca o caractere no índice correspondente dentro da variável `alphabet`.
4. `f += ...` concatena os caracteres para formar a flag final.

Por exemplo, o índice `0` mapeia para o caractere `'j'`, o índice `1` para `'X'`, o índice `2` para `'O'`, e assim sucessivamente.

### 4. Descriptografando os Dados

Para reproduzir a decodificação e obter a flag sem depender da calculadora, podemos executar o seguinte script em Python:

```python
alphabet = "jXOsE_Q7YB32KVqRGFUx15IcltpCNg8{HMz49baWkiTud60vmhnLAoSZDyewr}PJf"
ciphertext = "62 22 28 12 31 0 43 3 25 5 35 5 3 20 48 26 24 10 5 26 60 46 29 60 35 48 5 20 5 59 60 46 25 10 5 46 50 5 48 57 5 50 10 59 5 23 35 24 23 43 24 35 25 46 60 61"

flag = ""
for n in ciphertext.split():
    flag += alphabet[int(n)]

print(flag)

```

Ao executar o script, a sequência de índices é traduzida diretamente para a flag final.

### Flag

`PINK{just_4_s1mpl3_pr0gr4m_1_wr0t3_0n_my_n3w_c4lcul4t0r}`

## Autor da WriteUp

[Membro de Exploitation - Jenni-Lopes](https://github.com/Jenni-Lopes)