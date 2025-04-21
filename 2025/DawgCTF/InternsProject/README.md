# WriteUp: Interns' Project
## Descrição do Desafio:
**Categoria:** pwn \
**Descrição:**
> Our interns put together a little test program for us. It seems they all might have patched together their separate projects. Could you test it out for me?

### Arquivos
| Arquivo | Descrição |
| ------- | --------- |
| internsProject | Executável. |

> 📥 **Download:** [Arquivos](https://github.com/HawkSecUnifei/Writeups/raw/refs/heads/main/2025/DawgCTF/InternsProject/internsProject)

## Passo a Passo da Solução
### 1. Análise do arquivo fornecido
Este desafio fornece apenas o executável, que é bem simples. Ao executá-lo, ele entra em um *loop* que pede para digitarmos um número de 1 a 3, cada um correspondendo a uma operação diferente:

```bash
Welcome to our intern's test project!

The following are your options:
   1. Say hi
   2. Print the flag
   3. Create an account
Enter option (1-3). Press Enter to submit:
1
Hi!

The following are your options:
   1. Say hi
   2. Print the flag
   3. Create an account
Enter option (1-3). Press Enter to submit:
2
Error: Option 2 requires root privileges HAHA

The following are your options:
   1. Say hi
   2. Print the flag
   3. Create an account
Enter option (1-3). Press Enter to submit:
```

A opção 2 parece ser o objetivo do desafio, mas quando a selecionamos, o programa informa que não temos permissão. A partir daí, partimos para a análise do código utilizando o Ghidra.

{% code title="main.cpp" overflow="wrap" lineNumbers="true" %}
```c++
void main(void)
{
  ostream *poVar1;
  
  poVar1 = std::operator<<((ostream *)std::cout,"Welcome to our intern\'s test project!");
  std::ostream::operator<<(poVar1,std::endl<>);
  do {
    std::ostream::operator<<((ostream *)std::cout,std::endl<>);
    poVar1 = std::operator<<((ostream *)std::cout,"The following are your options:");
    std::ostream::operator<<(poVar1,std::endl<>);
    poVar1 = std::operator<<((ostream *)std::cout,"   1. Say hi");
    std::ostream::operator<<(poVar1,std::endl<>);
    poVar1 = std::operator<<((ostream *)std::cout,"   2. Print the flag");
    std::ostream::operator<<(poVar1,std::endl<>);
    poVar1 = std::operator<<((ostream *)std::cout,"   3. Create an account");
    std::ostream::operator<<(poVar1,std::endl<>);
    poVar1 = std::operator<<((ostream *)std::cout,"Enter option (1-3). Press Enter to submit:");
    std::ostream::operator<<(poVar1,std::endl<>);
    handleOption();
  } while( true );
}
```
{% endcode %}

A função `main()` pode ser vista acima, e basicamente confirma o que já observamos no terminal: um *loop* que exibe o menu e pede uma entrada de 1 a 3. O destaque vai para a função `handleOption()`, que provavelmente é responsável por lidar com essa entrada do usuário.

{% code title="handleOption.cpp" overflow="wrap" lineNumbers="true" %}
```c++
void handleOption(void)

{
  bool bVar1;
  __uid_t _Var2;
  long *plVar3;
  ostream *poVar4;
  long in_FS_OFFSET;
  int local_5d4;
  int local_5d0;
  int local_5cc;
  string local_5c8 [32];
  istringstream local_5a8 [384];
  int local_428 [258];
  long local_20;
  
  local_20 = *(long *)(in_FS_OFFSET + 0x28);
  local_5d0 = 0;
  std::string::string(local_5c8);
                    /* try { // try from 0010171b to 0010173d has its CatchHandler @ 0010192b */
  std::getline<>((istream *)std::cin,local_5c8);
  std::istringstream::istringstream(local_5a8,local_5c8,8);
  while( true ) {
    plVar3 = (long *)std::istream::operator>>((istream *)local_5a8,&local_5d4);
    bVar1 = std::ios::operator.cast.to.bool((ios *)((long)plVar3 + *(long *)(*plVar3 + -0x18)));
    if ((bVar1) && (local_5d0 < 0x100)) {
      bVar1 = true;
    }
    else {
      bVar1 = false;
    }
    if (!bVar1) break;
    if ((local_5d4 < 1) || (3 < local_5d4)) {
                    /* try { // try from 00101789 to 001018b5 has its CatchHandler @ 00101913 */
      poVar4 = std::operator<<((ostream *)std::cout,"Ignoring invalid option: ");
      poVar4 = (ostream *)std::ostream::operator<<(poVar4,local_5d4);
      std::ostream::operator<<(poVar4,std::endl<>);
    }
    else {
      local_428[local_5d0] = local_5d4;
      local_5d0 = local_5d0 + 1;
    }
  }
  if ((local_428[0] == 2) && (_Var2 = geteuid(), _Var2 != 0)) {
    bVar1 = true;
  }
  else {
    bVar1 = false;
  }
  if (bVar1) {
    poVar4 = std::operator<<((ostream *)std::cout,"Error: Option 2 requires root privileges HAHA");
    std::ostream::operator<<(poVar4,std::endl<>);
  }
  else {
    for (local_5cc = 0; local_5cc < local_5d0; local_5cc = local_5cc + 1) {
      if (local_428[local_5cc] == 1) {
        sayHello();
      }
      else if (local_428[local_5cc] == 2) {
        printFlag();
      }
      else if (local_428[local_5cc] == 3) {
        login();
      }
    }
  }
  std::istringstream::~istringstream(local_5a8);
  std::string::~string(local_5c8);
  if (local_20 == *(long *)(in_FS_OFFSET + 0x28)) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}
```
{% endcode %}

O código acima mostra como a função `handleOption()` funciona. Ela lê o que foi digitado no terminal e salva os valores no vetor `local_428`. Um detalhe importante é que ela lê a linha inteira e salva todos os números digitados (desde que estejam separados por espaço), tratando todos eles um por um.

A parte mais curiosa é a verificação de permissão para a opção 2:

{% code title="option2.cpp" overflow="wrap" lineNumbers="true" %}
```c++
if ((local_428[0] == 2) && (geteuid() != 0))
```
{% endcode %}

Ou seja, ela só verifica se a **primeira opção digitada foi 2** e se o usuário não é *root*. Se isso for verdade, ela impede o acesso e mostra a mensagem de erro. Porém, se digitarmos qualquer outro número primeiro, e colocarmos o 2 depois, a função `printFlag()` será executada normalmente, pois o restante do vetor não passa pela verificação de privilégio.

### 2. Exploit
Seguindo o que foi visto acima, basta digitarmos qualquer opção antes da opção 2 para que ela seja executada, revelando assim a *flag*.

```bash
Welcome to our intern's test project!

The following are your options:
   1. Say hi
   2. Print the flag
   3. Create an account
Enter option (1-3). Press Enter to submit:
1 2
Hi!
Here is your flag: DawgCTF{B@d_P3rm1ssi0ns}

The following are your options:
   1. Say hi
   2. Print the flag
   3. Create an account
Enter option (1-3). Press Enter to submit:
```

### Flag
`DawgCTF{B@d_P3rm1ssi0ns}`

## Autor da WriteUp
[Membro de Exploitation - HenriUz](https://github.com/HenriUz)