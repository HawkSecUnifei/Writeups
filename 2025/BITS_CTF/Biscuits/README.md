# WriteUp: Biscuits
## Descrição do Desafio:
**Autor:** d4y0n3 \
**Categoria:** pwn \
**Descrição:**
> Momma, can I have cookie..?
>
> No....

### Arquivos
| Arquivo | Descrição |
| ------- | --------- |
| main | Executável. |
| solve.py | Script da solução. |

> 📥 **Download:** [Arquivos](https://github.com/HawkSecUnifei/Writeups/raw/refs/heads/main/2025/BITS_CTF/Biscuits/Arquivos.zip)

## Passo a Passo da Solução
### 1. Análise do executável
Este é mais um desafio que utiliza elementos aleatórios, porém com a *seed* sendo `time(NULL)`. Analisando pelo **Ghidra**, vemos que o código executa um *loop* de 100 iterações, no qual, cada iteração calcula uma posição aleatória em uma lista chamada `cookies`, e pede um *input* para o usuário.

Se o *input* for diferente do `cookie` selecionado, a execução encerra, porém se for igual todas as vezes, a **flag** é impressa.

{% code title="main.c" overflow="wrap" lineNumbers="true" %}

```c
undefined8 main(void)

{
  int iVar1;
  time_t tVar2;
  size_t sVar3;
  FILE *__stream;
  long in_FS_OFFSET;
  int local_f8;
  char local_e8 [112];
  char local_78 [104];
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  tVar2 = time((time_t *)0x0);
  srand((uint)tVar2);
  puts("Give me the cookie I want a 100 times in a row and I\'ll give you the flag!");
  fflush(stdout);
  for (local_f8 = 0; local_f8 < 100; local_f8 = local_f8 + 1) {
    iVar1 = rand();
    strcpy(local_78,*(char **)(cookies + (long)(iVar1 % 100) * 8));
    printf("Guess the cookie: ");
    fflush(stdout);
    fgets(local_e8,100,stdin);
    sVar3 = strcspn(local_e8,"\n");
    local_e8[sVar3] = '\0';
    iVar1 = strcmp(local_e8,local_78);
    if (iVar1 != 0) {
      printf("Wrong. The cookie I wanted was: %s\n",local_78);
                    /* WARNING: Subroutine does not return */
      exit(0);
    }
    printf("Correct! The cookie was: %s\n",local_78);
    fflush(stdout);
  }
  printf("Congrats!\nFlag: ");
  fflush(stdout);
  __stream = fopen("flag.txt","r");
  if (__stream == (FILE *)0x0) {
    perror("Failed to open flag file");
                    /* WARNING: Subroutine does not return */
    exit(1);
  }
  while( true ) {
    iVar1 = fgetc(__stream);
    if ((char)iVar1 == -1) break;
    putchar((int)(char)iVar1);
  }
  putchar(10);
  fclose(__stream);
  fflush(stdout);
  if (local_10 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return 0;
}
```

{% endcode %}

### 2. Exploit
O maior desafio aqui é recriar a lista `cookies` dentro do *script*, mas uma vez com isso feito, basta recriar o *loop*, selecionando os elementos aleatórios da lista e enviando para o programa. Lembre-se de que quando a conexão é remota, a *seed* deve ser `time(NULL) - (algum valor)`, e se for local, deve ser apenas `time(NULL)`.

{% code title="solve.py" overflow="wrap" lineNumbers="true" %}

```py
from ctypes import CDLL
from pwn import *

cookies = [b"Chocolate Chip", b"Sugar Cookie", b"Oatmeal Raisin", b"Peanut Butter", b"Snickerdoodle", b"Shortbread", b"Gingerbread", b"Macaron", b"Macaroon", b"Biscotti", b"Butter Cookie", 
           b"White Chocolate Macadamia Nut", b"Double Chocolate Chip", b"M&M Cookie", b"Lemon Drop Cookie", b"Coconut Cookie", b"Almond Cookie", b"Thumbprint Cookie", b"Fortune Cookie", 
           b"Black and White Cookie", b"Molasses Cookie", b"Pumpkin Cookie", b"Maple Cookie", b"Espresso Cookie", b"Red Velvet Cookie", b"Funfetti Cookie", b"S'mores Cookie", b"Rocky Road Cookie",
           b"Caramel Apple Cookie", b"Banana Bread Cookie", b"Zucchini Cookie", b"Matcha Green Tea Cookie", b"Chai Spice Cookie", b"Lavender Shortbread", b"Earl Grey Tea Cookie", 
           b"Pistachio Cookie", b"Hazelnut Cookie", b"Pecan Sandies", b"Linzer Cookie", b"Spritz Cookie", b"Russian Tea Cake", b"Anzac Biscuit", b"Florentine Cookie", b"Stroopwafel",
           b"Alfajores", b"\x50\x6f\x6c\x76\x6f\x72\xc3\xb3\x6e\x00", b"Springerle", b"\x50\x66\x65\x66\x66\x65\x72\x6e\xc3\xbc\x73\x73\x65\x00", b"Speculoos", b"Kolaczki", b"Rugelach",
           b"Hamantaschen", b"Mandelbrot", b"Koulourakia", b"Melomakarona", b"Kourabiedes", b"Pizzelle", b"Amaretti", b"Cantucci", b"Savoiardi (Ladyfingers)", b"Madeleine", b"Palmier",
           b"Tuile", b"Langue de Chat", b"Viennese Whirls", b"Empire Biscuit", b"Jammie Dodger", b"Digestive Biscuit", b"Hobnob", b"Garibaldi Biscuit", b"Bourbon Biscuit", b"Custard Cream",
           b"Ginger Nut", b"Nice Biscuit", b"Shortcake", b"Jam Thumbprint", b"Coconut Macaroon", b"Chocolate Crinkle", b"Pepparkakor", b"Sandbakelse", b"Krumkake", b"Rosette Cookie",
           b"Pinwheel Cookie", b"Checkerboard Cookie", b"Rainbow Cookie", b"Mexican Wedding Cookie", b"Snowball Cookie", b"Cranberry Orange Cookie", b"Pumpkin Spice Cookie", 
           b"Cinnamon Roll Cookie", b"Chocolate Hazelnut Cookie", b"Salted Caramel Cookie", b"Toffee Crunch Cookie", b"Brownie Cookie", b"Cheesecake Cookie", b"Key Lime Cookie",
           b"Blueberry Lemon Cookie", b"Raspberry Almond Cookie", b"Strawberry Shortcake Cookie", b"Neapolitan Cookie"]

libc = CDLL("libc.so.6")
p = remote("20.244.40.210", 6000)
libc.srand(libc.time(0) - 2)
#p = process("./main")

p.recvuntil(b"the flag!")
for i in range(100):
    num = libc.rand() % 100
    p.sendlineafter(b"Guess the cookie: ", cookies[num])
    print(p.recvline(), cookies[num])

print(p.recvall().decode())
```

{% endcode %}

### Flag
`BITSCTF{7h4nk5_f0r_4ll_0f_th3_c00ki3s_1_r34lly_enjoy3d_th3m_d31fa51e}`

## Autor da WriteUp
[Membro de Exploitation - HenriUz](https://github.com/HenriUz)