# WriteUp: the-eye
## Descrição do Desafio:
**Autor:** aplet123 \
**Categoria:** rev \
**Descrição:** 
> I believe we’ve reached the end of our journey. All that remains is to collapse the innumerable possibilities before us.

### Arquivos
| Arquivo | Descrição |
| ------- | --------- |
| Dockerfile | Docker. |
| solve.py | Script. |
| the-eye | Executável. |

> 📥 **Download:** [Arquivos](https://github.com/HawkSecUnifei/Writeups/raw/refs/heads/main/2025/LA_CTF/the-eye/Arquivos.zip)

## Passo a Passo da Solução
### 1. Análise do executável
Analisando o executável, vemos que é um código sem muito segredo. Ele possuí 3 funções principais:
- `main()`: chama função que lê a **flag**, chama uma função que embaralha a **flag** 22 vezes, e por fim imprime o resultado.
- `read_msg()`: é função responsável por ler a **flag**, na verdade ela lê o conteúdo do arquivo `msg.txt`.
- `shuffle()`: com base em um valor aleatório, troca a posição de todos os caracteres da **flag**, indo do último índice até o ínicio.

{% code title="the-eye" overflow="wrap" lineNumbers="true" %}

```c
undefined8 main(void)

{
  time_t tVar1;
  char *__s;
  undefined4 local_c;
  
  tVar1 = time((time_t *)0x0);
  srand((uint)tVar1);
  __s = (char *)read_msg();
  for (local_c = 0; local_c < 22; local_c = local_c + 1) {
    shuffle(__s);
  }
  puts(__s);
  free(__s);
  return 0;
}

void * read_msg(void)

{
  FILE *__stream;
  void *__ptr;
  size_t local_10;
  
  __stream = fopen("msg.txt","rb");
  if (__stream == (FILE *)0x0) {
    puts("msg.txt is missing");
                    /* WARNING: Subroutine does not return */
    exit(1);
  }
  fseek(__stream,0,2);
  local_10 = ftell(__stream);
  __ptr = malloc(local_10 + 1);
  fseek(__stream,0,0);
  fread(__ptr,1,local_10,__stream);
  fclose(__stream);
  if (*(char *)((long)__ptr + (local_10 - 1)) == '\n') {
    local_10 = local_10 - 1;
  }
  *(undefined1 *)((long)__ptr + local_10) = 0;
  return __ptr;
}


void shuffle(char *param_1)

{
  char cVar1;
  int iVar2;
  int iVar3;
  size_t sVar4;
  int local_c;
  
  sVar4 = strlen(param_1);
  iVar2 = (int)sVar4;
  while (local_c = iVar2 + -1, -1 < local_c) {
    iVar3 = rand();
    cVar1 = param_1[local_c];
    param_1[local_c] = param_1[iVar3 % iVar2];
    param_1[iVar3 % iVar2] = cVar1;
    iVar2 = local_c;
  }
  return;
}
```

{% endcode %}

### 2. Solução
A solução é bem simples, devemos refazer o *shuffle* utilizando os índices no lugar dos caracteres, aí no final teremos uma lista que nos diz em qual é posição original do caractere.

```
Antes do shuffle:
[0, 1, 2, 3]

Depois do shuffle:
[1, 3, 0, 2]

-> Concluímos que o caractere na posição 0 após o shuffle, tem como posição original a 1.
```

Porém devemos nos atentar à alguns pontos:
- Aleatorização: o código usa uma *seed* específica para realizar o *shuffle*, e sem essa *seed* é impossível refazer o *shuffle*. Porém, a *seed* utilizada é `time(NULL)`, assim quando abrirmos o executável na solução já setamos a *seed* junto. Perceba que quando o executável é aberto remotamente, há alguns atrasos de conexão, então a *seed* vira `time(NULL) - (algum valor)`.
- Na função *shuffle*, o segundo valor do módulo (originalmente o tamanho da mensagem), é modificado a cada iteração para ser ele mesmo menos 1.

{% code title="solve.py" overflow="wrap" lineNumbers="true" %}

```py
from ctypes import CDLL
from pwn import *

libc = CDLL("libc.so.6")
libc.srand(libc.time(0) - 5)

#p = process("./the-eye")
p = remote("chall.lac.tf", 31313)

flag = p.recvall().decode()
qnt_carac = len(flag) - 1

# Refazendo o shuffle.
index = list(range(qnt_carac))
def shuffle(lista):
    aux = qnt_carac
    for i in range(qnt_carac - 1, -1, -1):
        idx = libc.rand() % aux
        lista[i], lista[idx] = lista[idx], lista[i]
        aux = i

for _ in range(22):
    shuffle(index)

# Montando a flag.
original_flag = [""] * qnt_carac
for i, original in enumerate(index):
    original_flag[original] = flag[i]

print("".join(original_flag))
```

{% endcode %}

### Output
`Outer Wilds is an action-adventure video game set in a small planetary system in which the player character, an unnamed space explorer referred to as the Hatchling, explores and investigates its mysteries in a self-directed manner. Whenever the Hatchling dies, the game resets to the beginning; this happens regardless after 22 minutes of gameplay due to the sun going supernova. The player uses these repeated time loops to discover the secrets of the Nomai, an alien species that has left ruins scattered throughout the planetary system, including why the sun is exploding. A downloadable content expansion, Echoes of the Eye, adds additional locations and mysteries to the game. lactf{are_you_ready_to_learn_what_comes_next?}`

### Flag
`lactf{are_you_ready_to_learn_what_comes_next?}`

## Autores da WriteUp
[Membro de Exploitation - HenriUz](https://github.com/HenriUz) \
[Membro de Exploitation - CaioMendesRRosa](https://github.com/CaioMendesRRosa)