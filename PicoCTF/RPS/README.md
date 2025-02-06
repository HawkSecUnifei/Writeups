# WriteUp: RPS

## Descrição do Desafio
**Autor**: Will Hong \
**Plataforma**: [PicoCTF](https://play.picoctf.org/practice/challenge/293?category=6&page=2) \
**Categoria**: Binary Exploitation \
**Dificuldade**: Médio \
**Data**: 2022 \
**Descrição**:
> Here's a program that plays rock, paper, scissors against you. I hear something good happens if you win 5 times in a row.

## Passo a Passo da Solução
### 1. Análise do arquivo fornecido
Este desafio fornece apenas o código-fonte, tornando mais fácil a análise. Analisando esse código, podemos ver que ele entra em um *loop* infinito, que pode ser encerrado com algumas condições, e fica pedindo o *input* do usuário. 

Se o usuário selecioar jogar, é chamada uma função `play()`, que define a *seed* para a função `rand()` como o tempo atual, e depois pede para o usuário inserir qual mão ele vai jogar. Após isso, é comparado se a entrada do usuário corresponde à mão ganhadora, que é um elemento em uma lista, cujo índice é definido por `rand() % 3`.

{% code title="game-redacted.c" overflow="wrap" lineNumbers="true" %}

```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/time.h>
#include <sys/types.h>


#define WAIT 60



static const char* flag = "[REDACTED]";

char* hands[3] = {"rock", "paper", "scissors"};
char* loses[3] = {"paper", "scissors", "rock"};
int wins = 0;



int tgetinput(char *input, unsigned int l)
{
    fd_set          input_set;
    struct timeval  timeout;
    int             ready_for_reading = 0;
    int             read_bytes = 0;
    
    if( l <= 0 )
    {
      printf("'l' for tgetinput must be greater than 0\n");
      return -2;
    }
    
    
    /* Empty the FD Set */
    FD_ZERO(&input_set );
    /* Listen to the input descriptor */
    FD_SET(STDIN_FILENO, &input_set);

    /* Waiting for some seconds */
    timeout.tv_sec = WAIT;    // WAIT seconds
    timeout.tv_usec = 0;    // 0 milliseconds

    /* Listening for input stream for any activity */
    ready_for_reading = select(1, &input_set, NULL, NULL, &timeout);
    /* Here, first parameter is number of FDs in the set, 
     * second is our FD set for reading,
     * third is the FD set in which any write activity needs to updated,
     * which is not required in this case. 
     * Fourth is timeout
     */

    if (ready_for_reading == -1) {
        /* Some error has occured in input */
        printf("Unable to read your input\n");
        return -1;
    } 

    if (ready_for_reading) {
        read_bytes = read(0, input, l-1);
        if(input[read_bytes-1]=='\n'){
        --read_bytes;
        input[read_bytes]='\0';
        }
        if(read_bytes==0){
            printf("No data given.\n");
            return -4;
        } else {
            return 0;
        }
    } else {
        printf("Timed out waiting for user input. Press Ctrl-C to disconnect\n");
        return -3;
    }

    return 0;
}


bool play () {
  char player_turn[100];
  srand(time(0));
  int r;

  printf("Please make your selection (rock/paper/scissors):\n");
  r = tgetinput(player_turn, 100);
  // Timeout on user input
  if(r == -3)
  {
    printf("Goodbye!\n");
    exit(0);
  }

  int computer_turn = rand() % 3;
  printf("You played: %s\n", player_turn);
  printf("The computer played: %s\n", hands[computer_turn]);

  if (strstr(player_turn, loses[computer_turn])) {
    puts("You win! Play again?");
    return true;
  } else {
    puts("Seems like you didn't win this time. Play again?");
    return false;
  }
}


int main () {
  char input[3] = {'\0'};
  int command;
  int r;

  puts("Welcome challenger to the game of Rock, Paper, Scissors");
  puts("For anyone that beats me 5 times in a row, I will offer up a flag I found");
  puts("Are you ready?");
  
  while (true) {
    puts("Type '1' to play a game");
    puts("Type '2' to exit the program");
    r = tgetinput(input, 3);
    // Timeout on user input
    if(r == -3)
    {
      printf("Goodbye!\n");
      exit(0);
    }
    
    if ((command = strtol(input, NULL, 10)) == 0) {
      puts("Please put in a valid number");
      
    } else if (command == 1) {
      printf("\n\n");
      if (play()) {
        wins++;
      } else {
        wins = 0;
      }

      if (wins >= 5) {
        puts("Congrats, here's the flag!");
        puts(flag);
      }
    } else if (command == 2) {
      return 0;
    } else {
      puts("Please type either 1 or 2");
    }
  }

  return 0;
}
```

{% endcode %}

Se o usuário vencer 5 vezes seguidas, a **flag** é impressa.

### 2. Solução
A forma de resolver esse desafio é bem simples, devemos apenas ter uma cópia da lista que ele usa para comparar com o usuário, e depois temos que sempre ficar definindo a *seed* para ser a mesma, fazendo com que a saída `rand() % 3` seja a mesma em ambos os códigos.

{% hint style="warning" %}
**Importante:** A solução feita não funciona em 100% dos casos, por causa (principalmente) pela diferença de tempo entre servidor e cliente. 
{% endhint %}

{% code title="solve.py" overflow="wrap" lineNumbers="true" %}
```py
from pwn import *
from ctypes import CDLL

loses = ["paper", "scissors", "rock"]
libc = CDLL("libc.so.6")

p = remote("saturn.picoctf.net", 60070)

for i in range(5):
    libc.srand(libc.time(0))
    p.sendlineafter(b"Type '2' to exit the program", b"1")
    p.recvuntil(b"\r\n\r\n\r\n")
    win = libc.rand() % 3
    p.sendlineafter(b"Please make your selection (rock/paper/scissors):", loses[win].encode())
    print(p.recvuntil(b"Play again?"))

print(p.clean().decode())
```
{% endcode %}

### Flag
`picoCTF{50M3_3X7R3M3_1UCK_C85AF58A}`

## Autor da WriteUp
[Membro de Exploitation - HenriUz](https://github.com/HenriUz)