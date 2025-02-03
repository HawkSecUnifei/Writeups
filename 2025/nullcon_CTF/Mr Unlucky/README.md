# WriteUp: Mr Unlucky
## Descrição do Desafio:
Categoria: pwn \
Descrição:
> I have a love/hate relationship with dota2, I either always win or always lose. there is no inbetween :(
> 
> However, Oracle told me that If I win at his cursed game I'll win every match and gain the aegis of Immortality in real life as well!
>
> CAN YOU HELP ME???
>
>Note: The challenge autor is an immortal player already ;)

### Arquivos
| Arquivo | Descrição |
| ------- | --------- |
| mr_unlucky | Executável do desafio. |
| Dockerfile | Arquivo docker. |
| solve.py | Script em Python que resolve o desafio. |

> 📥 **Download:** [Arquivos]()

## Passo a Passo da Solução
### 1. Análise do executável
Como este desafio não fornece o código-fonte, devemos analisá-lo diretamente.

Primeiramente, verificamos as proteções ativadas no binário para termos uma noção dos desafios que enfrentaremos:

```bash
Arch:     amd64
RELRO:      Full RELRO
Stack:      Canary found
NX:         NX enabled
PIE:        PIE enabled
SHSTK:      Enabled
IBT:        Enabled
Stripped:   No
```

Como podemos ver, o executável possui praticamente todas as proteções ativadas. Em seguida, vamos decompilá-lo para entender melhor seu funcionamento.

Analisando o código pelo Ghidra, podemos identificar duas funções essenciais: `main()` e `print_flag()`.

Na função `main()`, observamos que:
- Uma *seed* é definida para a função `rand()` usando o tempo atual (`time(NULL)`).
- Um *loop* é executado 50 vezes (`0x32` *loops*).
- Em cada iteração, um nome aleatório é selecionado da variável `heroes`.
- O usuário deve inserir o nome correspondente.
- Caso a entrada esteja incorreta, o programa encerra.
- Se o usuário acertar todas as tentativas, a função `print_flag("flag.txt")` é chamada.

> 💡 **Nota:** As proteções neste caso não serão um problema, pois o objetivo é identificar uma maneira de responder todas as perguntas corretamente.

Código-fonte da `main()`:
```c
undefined8 main(EVP_PKEY_CTX *param_1)

{
  int iVar1;
  int iVar2;
  time_t tVar3;
  size_t sVar4;
  long in_FS_OFFSET;
  int local_40;
  char local_38 [40];
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  init(param_1);
  puts("I have always been unlucky. I can\'t even win a single game of dota2 :(");
  puts("however, I heard that this tool can lift the curse that I have!");
  puts("YET I CAN\'T BEAT IT\'S CHALLENGE. Can you help me guess the names?");
  tVar3 = time((time_t *)0x0);
  srand((uint)tVar3);
  sleep(3);
  puts(
      "Welcome to dota2 hero guesser! Your task is to guess the right hero each time to win the chal lenge and claim the aegis!"
      );
  for (local_40 = 0; local_40 < 0x32; local_40 = local_40 + 1) {
    iVar1 = rand();
    printf("Guess the Dota 2 hero (case sensitive!!!): ");
    fgets(local_38,0x1e,stdin);
    sVar4 = strcspn(local_38,"\n");
    local_38[sVar4] = '\0';
    iVar2 = strcmp(local_38,*(char **)(heroes + (long)(iVar1 % 0x14) * 8));
    if (iVar2 != 0) {
      printf("Wrong guess! The correct hero was %s.\n",
             *(undefined8 *)(heroes + (long)(iVar1 % 0x14) * 8));
                    /* WARNING: Subroutine does not return */
      exit(0);
    }
    printf("%s was right! moving on to the next guess...\n",local_38);
  }
  puts(
      "Wow you are one lucky person! fine, here is your aegis (roshan will not be happy about this!) "
      );
  print_flag("flag.txt");
  if (local_10 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return 0;
}
```
Saída de exemplo:
```bash
I have always been unlucky. I can't even win a single game of dota2 :(
however, I heard that this tool can lift the curse that I have!
YET I CAN'T BEAT IT'S CHALLENGE. Can you help me guess the names?
Welcome to dota2 hero guesser! Your task is to guess the right hero each time to win the challenge and claim the aegis!
Guess the Dota 2 hero (case sensitive!!!): mage
Wrong guess! The correct hero was Anti-Mage.
```

### 2. Solução
A solução é simples:
1. Precisamos de uma cópia da lista de heróis armazenada na variável `heroes`.
2. Precisamos garantir que a *seed* usada em nosso *script* seja a mesma do servidor.

Para obter os nomes, podemos inspecionar a região da memória onde `heroes` está armazenada no Ghidra:

```
                             heroes                                          XREF[5]:     Entry Point (*) , 
                                                                                          main:00101524 (*) , 
                                                                                          main:0010152b (*) , 
                                                                                          main:0010156c (*) , 
                                                                                          main:00101573 (*)   
        00104020 08  20  10       undefine
                 00  00  00 
                 00  00  12 
           00104020 08              undefine  08h                     [0]           ?  ->  00102008     XREF[5]:     Entry Point (*) , 
                                                                                                                     main:00101524 (*) , 
                                                                                                                     main:0010152b (*) , 
                                                                                                                     main:0010156c (*) , 
                                                                                                                     main:00101573 (*)   
           00104021 20              undefine  20h                     [1]
           00104022 10              undefine  10h                     [2]
           00104023 00              undefine  00h                     [3]
           00104024 00              undefine  00h                     [4]
           00104025 00              undefine  00h                     [5]
           00104026 00              undefine  00h                     [6]
           00104027 00              undefine  00h                     [7]
           00104028 12              undefine  12h                     [8]           ?  ->  00102012
           00104029 20              undefine  20h                     [9]
           0010402a 10              undefine  10h                     [10]
           0010402b 00              undefine  00h                     [11]
           0010402c 00              undefine  00h                     [12]
           0010402d 00              undefine  00h                     [13]
           0010402e 00              undefine  00h                     [14]
           0010402f 00              undefine  00h                     [15]
           00104030 16              undefine  16h                     [16]          ?  ->  00102016
           00104031 20              undefine  20h                     [17]
           00104032 10              undefine  10h                     [18]
        ...
```

Ao analisar essa região, podemos identificar que a cada 8 *offsets*, há um ponteiro para os nomes dos heróis.

Para definir a *seed*, usamos a biblioteca `CDLL`, que contém funções da *libc*.

No entanto, devemos considerar que o programa chama `sleep(3)` após definir a *seed*,
o que significa que a *seed* real do servidor será `time(NULL) - 3`.

> 💡 **Nota:** Localmente a *seed* não deve conter o '-3'.

```py
from ctypes import CDLL
from pwn import *

# Lista de personagens possíveis. Obtidos por meio do Ghidra, a partir do endereço 0x00102008.
heroes = ["Anti-Mage", "Axe", "Bane", "Bloodseeker", "Crystal Maiden", "Drow Ranger", "Earthshaker", "Juggernaut", 
          "Mirana", "Morphling", "Phantom Assassin", "Pudge", "Shadow Fiend", "Sniper", "Storm Spirit", "Sven", "Tiny",
          "Vengeful Spirit", "Windranger", "Zeus"]

elf = context.binary = ELF("./mr_unlucky")
p = remote("ip", "porta")

# Carregando as bibliotecas da libc, e setando o time para o tempo atual - 3 (devido ao sleep no servidor).
# Note que se estiver rodando localmente o processo, o '- 3' não é necessário.
libc = CDLL("libc.so.6")
libc.srand(libc.time(0) - 3)

# Respondendo as perguntas. Com a mesma seed, os elementos gerados serão os mesmos.
p.recvuntil(b"aegis!")
for i in range(0x32):
    index = (libc.rand() % 0x14)
    p.sendlineafter(b"): ", heroes[index].encode())
    print(p.recvline().decode())

print(p.recvall().decode())
```

### Flag
`ENO{0NLY_TH3_W0RTHY_0N35_C4N_CL41M_THE_AEGIS_OF_IMMORTALITY!!!}`

## Autor
[Membro de Exploitation - HenriUz](https://github.com/HenriUz)
