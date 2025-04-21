# WriteUp: Just Parry Lol
## Descrição do Desafio:
**Categoria:** pwn \
**Descrição:**
> Welcome, warrior. Inspired by his favorite game, For Honor, my friend made a turn-based combat simulator to familiarize people with frame data. However, the system is against you. Every move you make is just too slow. You have one secret tool: the ability to manipulate time.
> 
> Can you win the fight and retrieve the flag?

### Arquivos
| Arquivo | Descrição |
| ------- | --------- |
| JustParryLol | Executável. |

> 📥 **Download:** [Arquivos](https://github.com/HawkSecUnifei/Writeups/raw/refs/heads/main/2025/DawgCTF/JustParryLol/JustParryLol)

## Passo a Passo da Solução
### 1. Análise do arquivo fornecido
O desafio nos fornece apenas um executável. Ao executá-lo, o programa apresenta a seguinte interface:

```bash
=== Frame Trap ===
The bot is overwhelming... there's no fair way to win.
Enter your warrior name: HenriUz
Choose your action:
(1) Heavy Attack
(2) Light Attack
(3) Guard Break
(4) Block
(5) Parry
(6) Dodge
Enter choice: 1

[TURN 1]
Bot uses: Heavy Attack
You use: Heavy Attack
[DEBUG] Player startup: 633 (recovery 0 + startup 433 + penalty 200)
[DEBUG] Bot startup: 433 (recovery 0 + startup 433)
The bot hits you for 30 damage. Your health: 70
Choose your action:
(1) Heavy Attack
(2) Light Attack
(3) Guard Break
(4) Block
(5) Parry
(6) Dodge
Enter choice: 2

[TURN 2]
Bot uses: Heavy Attack
You use: Light Attack
[DEBUG] Player startup: 667 (recovery 267 + startup 200 + penalty 200)
[DEBUG] Bot startup: 700 (recovery 267 + startup 433)
You hit the bot for 15 damage. Bot health: 85
Choose your action:
(1) Heavy Attack
(2) Light Attack
(3) Guard Break
(4) Block
(5) Parry
(6) Dodge
Enter choice:
```

O jogo segue em um loop, solicitando novas ações a cada turno. Contudo, independentemente da escolha do jogador, o *bot* sempre vence. Com isso, devemos analisar como é a lógica disso por meio do Ghidra, ou outra ferramenta similar.

Ao abrir o binário no Ghidra, identificamos a função `FUN_00401150()` como sendo a `main()`. O código decompilado gerado inclui um `switch` que controla o estado interno do jogo (`DAT_004042c4`), mas a estrutura não é realmente um `switch` tradicional — as execuções ocorrem sequencialmente:

{% code title="main.c" overflow="wrap" lineNumbers="true" %}

```c
undefined8 FUN_00401150(void)

{
  time_t tVar1;
  undefined8 local_38;
  undefined8 uStack_30;
  undefined8 local_28;
  undefined8 uStack_20;
  undefined4 local_18;
  
  tVar1 = time((time_t *)0x0);
  srand((uint)tVar1);
  puts("=== Frame Trap ===");
  puts("The bot is overwhelming... there\'s no fair way to win.");
  FUN_00401480(); // Nome do usuário.
  switch(DAT_004042c4) {
  case 0:
    break;
  case 1:
    goto switchD_004011ac_caseD_1;
  case 2:
    goto switchD_004011ac_caseD_2;
  case 3:
    goto switchD_004011ac_caseD_3;
  case 4:
    goto switchD_004011ac_caseD_4;
  default:
    return 0;
  }
switchD_004011ac_caseD_0:
  // Usuário digita a opção.
  FUN_00401540(&local_38);
  DAT_004042c4 = 1;
  DAT_004042c0 = local_18;
  _DAT_004042a0 = local_38;
  uRam00000000004042a8 = uStack_30;
  _DAT_004042b0 = local_28;
  uRam00000000004042b8 = uStack_20;
  do {
    // Opção do bot é gerada aleatoriamente.
    FUN_004014f0(&local_38);
    DAT_004042c4 = 2;
    DAT_00404280 = local_18;
    _DAT_00404260 = local_38;
    uRam0000000000404268 = uStack_30;
    _DAT_00404270 = local_28;
    uRam0000000000404278 = uStack_20;
switchD_004011ac_caseD_2:
    DAT_004042c8 = DAT_004042c8 + 1;
    __printf_chk(1,"\n[TURN %d]\n");
    __printf_chk(1,"Bot uses: %s\n",&DAT_00404260);
    __printf_chk(1,"You use: %s\n",&DAT_004042a0);
    DAT_004042c4 = 3;
switchD_004011ac_caseD_3:
    // Lógica principal.
    FUN_00401620();
    DAT_004042c4 = 4;
switchD_004011ac_caseD_4:
    // Condições de parada.
    if (0 < DAT_004040e0) {
      if (0 < DAT_004040a0) break;
      FUN_00401430();
    }
    FUN_00401460();
switchD_004011ac_caseD_1:
  } while( true );
  if (9 < DAT_004042c8) {
    puts(&DAT_00402390);
    DAT_004042c4 = 5;
    return 0;
  }
  DAT_004042c4 = 0;
  goto switchD_004011ac_caseD_0;
}
```

{% endcode %}

A função principal de lógica é a `FUN_00401620()`. Nela, algumas comparações são realizadas, e determinam quem acerta quem, porém há uma comparação com valores "mágicos" que chama a atenção: 

{% code title="FUN_00401620.c" overflow="wrap" lineNumbers="true" %}

```c
if ((iStack0000000000000008 == 0x72726150) && (sStack000000000000000c == 0x79)) {
if (DAT_004042d4 != 0) {
    puts("Auto-parry activated!");
    DAT_004040a0 = DAT_004040a0 + -0x32;
    __printf_chk(1,
                "You hit the bot with an enhanced-speed heavy attack for %d damage. Bot health: % d\n"
                ,0x32);
    DAT_004042cc = 0;
    DAT_004042d0 = 0x10b;
    return;
}
if (iVar2 <= iVar3 + 0x31) {
    puts(&DAT_00402160);
    DAT_00404238 = DAT_00404238 + in_stack_00000020._4_4_;
    puts("The bot immediately counters with a light attack!");
    DAT_004040e0 = DAT_004040e0 + -0xf;
    __printf_chk(1,"You take 15 damage. Your health: %d\n");
    return;
}
}
```

{% endcode %}

O valor `0x72726150` em *little-endian* corresponde à *string* "Parr" e `0x79` é o caractere 'y'. Ou seja, esse trecho está verificando se o jogador usou o movimento "Parry". E se usou, uma nova comparação é feita usando a variável `DAT_004042d4`, e neste caso se ela for diferente de 0, o *bot* é quem leva o dano.

Procurando onde essa variável é modificada, podemos notar que é na função de entrada do usuário.

{% code title="FUN_00401480.c" overflow="wrap" lineNumbers="true" %}

```c
void FUN_00401480(void)

{
  __printf_chk(1,"Enter your warrior name: ");
  gets(s_Player_004040c0);
  if ((_s_Player_004040c0 == 0x525241504f545541) && (DAT_004040c8 == 0x59)) {
    DAT_004042d4 = 1;
    puts("You feel faster...");
    return;
  }
  return;
}
```

{% endcode %}

E por mais que está função tenha a vulnerabilidade de *buffer overflow*, o objetivo aqui é apenas digitar "AUTOPARRY" no nome e pronto, modificamos a variável.

### 2. Exploit
Seguindo o que foi descoberto acima, obtemos o seguinte resultado:

```bash
=== Frame Trap ===
The bot is overwhelming... there's no fair way to win.
Enter your warrior name: AUTOPARRY
AUTOPARRY
You feel faster...
Choose your action:
(1) Heavy Attack
(2) Light Attack
(3) Guard Break
(4) Block
(5) Parry
(6) Dodge
Enter choice: 5
5

[TURN 1]
Bot uses: Heavy Attack
You use: Parry
[DEBUG] Player startup: 350 (recovery 0 + startup 150 + penalty 200)
[DEBUG] Bot startup: 433 (recovery 0 + startup 433)
Auto-parry activated!
You hit the bot with an enhanced-speed heavy attack for 50 damage. Bot health: 50
Choose your action:
(1) Heavy Attack
(2) Light Attack
(3) Guard Break
(4) Block
(5) Parry
(6) Dodge
Enter choice: 5
5

[TURN 2]
Bot uses: Heavy Attack
You use: Parry
[DEBUG] Player startup: 617 (recovery 267 + startup 150 + penalty 200)
[DEBUG] Bot startup: 433 (recovery 0 + startup 433)
Auto-parry activated!
You hit the bot with an enhanced-speed heavy attack for 50 damage. Bot health: 0
You defeated the bot! You win!
DawgCTF{fr4me_d4ta_m4nipulat10n}
```

### Flag
`DawgCTF{fr4me_d4ta_m4nipulat10n}`

## Autor da WriteUp
[Membro de Exploitation - HenriUz](https://github.com/HenriUz)