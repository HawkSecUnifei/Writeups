# WriteUp: zero_to_hero

## Descrição do Desafio:
**Author**: Claude \
**Plataforma**: [PicoCTF](https://play.picoctf.org/practice/challenge/75?category=6&page=5) \
**Categoria**: Binary Exploitation \
**Dificuldade**: Difícil \
**Data**: 2019 \
**Descrição**:
> Now you're really cooking. Can you pwn this service?

## Passo a Passo da Solução
### 1. Análise do arquivo fornecido
O binário fornecido vem com as seguintes proteções: Full RELRO, Canary, e NX. Com isso já podemos descartar a opção de reescrever a tabela `.GOT` do binário.

Analisando pelo Ghidra, vemos que as funções não vem bem definidas, mas com um pouco de análise já é possível achar a função de entrada e as outras principais. Olhando a função principal, já identificamos uma dica, que é o vazamento do endereço da `system`.
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

Tirando a função `menu()`, temos outras duas funções principais, a `addPower()` e a `removePower()`.
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

Olhando para elas podemos assumir alumas coisas:

- removePower: aqui verificamos que podemos ter 6 super poderes ao mesmo tempo (não importa muito no caso), podemos ver que os poderes (na verdade o endereço do chunk deles) é armazenado em uma variável global que eu renomeei como `powers`, e o mais importante, temos uma vulnerabilidade em que após liberarmos o chunk, com a função `free()`, o endereço na variável `powers` não é anulado, fazendo com que seja possível realizar um `double-free`.
- addPower: aqui verificamos que podemos digitar o tamanho do super poder (chunk), sendo o máximo 1032 (importante), e podemos escrever nesse tamanho. E aí está outra vulnerabilidade, quando escrevemos uma string, o final dela sempre deve ser um byte nulo `\0`, e no código nós podemos escrever exatamente a quantidade que pedimos, e em seguida o `\0` é colocado. Então, se escrevermos no tamanho total, o byte nulo é colocado em uma região que não é da string.

### 2. Exploit
