# [rev]-crushing
## Autor: HenriUz

## Código:
Este desafio consiste em analisar um código que fez uma "criptografia" em um texto.
Existem 3 funções principais no código: 

```c
undefined8 main(void)

{
  long lVar1;
  undefined8 *puVar2;
  undefined8 lista [256];
  uint local_14;
  long local_10;

  puVar2 = lista;
  for (lVar1 = 0xff; lVar1 != 0; lVar1 = lVar1 + -1) {
    *puVar2 = 0;
    puVar2 = puVar2 + 1;
  }

  local_10 = 0;
  while( true ) {
    local_14 = getchar();
    if (local_14 == 0xffffffff) break;
    add_char_to_map(lista,local_14 & 0xff,local_10);
    local_10 = local_10 + 1;
  }
  serialize_and_output(lista);
  return 0;
}
```
 - `main`:

Aqui nós temos algumas variáveis sendo criadas, as principais são: a `lista` (nome editado por mim) que irá armazenar ponteiros; o `local_10` que conta a posição que o caractere/hexadecimal aparece; o `local_14` que vai pegando os caracteres.

No código o primeiro `for` zera a `lista` e o segundo lê os caracteres digitados (?), no final a função que irá escrever no arquivo é chamada.

```c
void add_char_to_map(long lista,byte char,undefined8 idx)

{
  undefined8 *puVar1;
  long local_10;
  
  local_10 = *(long *)(lista + (ulong)char * 8);
  puVar1 = (undefined8 *)malloc(0x10);
  *puVar1 = idx;
  puVar1[1] = 0;
  if (local_10 == 0) {
    *(undefined8 **)((ulong)char * 8 + lista) = puVar1;
  }
  else {
    for (; *(long *)(local_10 + 8) != 0; local_10 = *(long *)(local_10 + 8)) {
    }
    *(undefined8 **)(local_10 + 8) = puVar1;
  }
  return;
}
```

 - `add_char_to_map`: 

Essa função recebe três parâmetros, o primeiro é a `lista`, o segundo é o binário do caractere `char` e o terceiro o índice/posição `idx` que ele aparece. No código nós também temos outras variáveis importantes: `local_10` é a variável que irá calcular uma posição na lista por meio da multiplicação do binário do caractere e `0x8`, e receberá o valor apontado por aquela posição (note que na primeira vez que entrar em uma posição nova o valor vai ser zero, ou seja, não aponta para nada); `puVar1` é um ponteiro que irá apontar para o índice informado.

O código inicialmente verifica se `local_10` é nulo (não aponta para nada), se for ele salva naquela posição o `puVar1` (índice do caractere), se não for ele entra em for que irá percorrer as posições seguintes à calculada inicialmente até achar uma que não aponte para nada, salvando nessa posição o índice.


```c
void serialize_and_output(long param_1)

{
  undefined8 local_28;
  void **pp;
  void *local_18;
  int local_c;
  
  for (local_c = 0; local_c < 0xff; local_c = local_c + 1) {
    pp = (void **)(param_1 + (long)local_c * 8);
    local_28 = list_len(pp);
    fwrite(&local_28,8,1,stdout);
    for (local_18 = *pp; local_18 != (void *)0x0; local_18 = *(void **)((long)local_18 + 8)) {
      fwrite(local_18,8,1,stdout);
    }
  }
  return;
}
```

- `serialize_and_output`: 

Essa função recebe apenas a `lista` como parâmetro (no código `param_1`), suas variáveis importantes são: `pp` que é um ponteiro de ponteiro e irá receber o ponteiro armazenado na posição calculada pela multiplicação do `local_c` (o `i` do for) e `0x8`; `local_28` recebe o número de caracteres iguais (como a posição dos caracteres iguais estão colocados de forma adjacente na lista, a função `list_len` recebe a posição e verifica quantas casas ela tem que andar para ficar nulo).

O código tem um loop indo de 0 até 255, e para cada iteração ele usa o valor do `local_c` para calcular uma posição na lista (note que terá vezes que esse valor irá bater com o binário dos caracteres digitados) e irá escrever no arquivo o tamanho seguido pelas posições que o caractere (`local_c` convertido para hexadecimal) aparece na mensagem (se o tamanho não for 0).

## Resolução:

Se abrirmos o arquivo com um editor de texto normal não iremos entender nada, mas se abrirmos com um hexdump iremos ver exatamente o que aconteceu no código, ou seja, irá ter um valor indicando a quantidade e em seguida as posições.

Como resolver: um script básico em python já o suficiente. Primeiro importamos a biblioteca pwn, abrimos o arquivo e e criamos uma string para conter a mensagem
```python
import pwn
data = open("./message.txt.cz", "rb").read()
message = bytearray(b" "*(8784//8)) #muito maior que o necessário, mas ok
```

Depois percorremos o arquivo da mesma forma que ele foi armazenado
```python
for c in range(256):
	count = pwn.u64(data[0:8]) #pegamos o primeiro elemento (que normalmente é a quantidade)
	data = data[8:] #fazemos o arquivo ser as posições a frente
	for offsets in range(count): #note que se for 0 nem entramos nesse for
		offset = pwn.u64(data[0:8]) #se não for 0, os elementos seguintes são os índices, e nós estamos lendo eles aqui
		data = data[8:] #andamos com o arquivo
		message[offset] = c #salvamos o caractere no array
	print(message.decode()) #printamos o array e vamos vendo ele sendo decodificado de pouco em pouco.
```


## Resultado: 

Organizer 1: Hey, did you finalize the password for the next... you know?

Organizer 2: Yeah, I did. It's "HTB{4_v3ry_b4d_compr3ss1on_sch3m3}"

Organizer 1: "HTB{4_v3ry_b4d_compr3ss1on_sch3m3}," got it. Sounds ominous enough to keep things interesting. Where do we spread the word?

Organizer 2: Let's stick to the usual channels: encrypted messages to the leaders and discreetly slip it into the training manuals for the participants.

Organizer 1: Perfect. And let's make sure it's not leaked this time. Last thing we need is an early bird getting the worm.

Organizer 2: Agreed. We can't afford any slip-ups, especially with the stakes so high. The anticipation leading up to it should be palpable.

Organizer 1: Absolutely. The thrill of the unknown is what keeps them coming back for more. "HTB{4_v3ry_b4d_compr3ss1on_sch3m3}" it is then.

## Flag: `HTB{4_v3ry_b4d_compr3ss1on_sch3m3}`
