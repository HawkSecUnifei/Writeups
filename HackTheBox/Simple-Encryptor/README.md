# WriteUp: Simple Encryptor

## Descrição do Desafio:
**Autor**: [Leeky](https://app.hackthebox.com/users/129896) \
**Plataforma**: [Hack The Box](https://app.hackthebox.com/challenges/366) \
**Categoria**: Reversing \
**Dificuldade**: Muito fácil \
**Data**: 2022 \
**Descrição**:
> On our regular checkups of our secret flag storage server we found out that we were hit by ransomware! The original flag data is nowhere to be found, but luckily we not only have the encrypted file but also the encryption program itself.

## Passo a Passo da Solução
### 1. Análise dos arquivos fornecidos
O desafio fornece dois arquivos:
- `encrypt`: um executável Linux de 64 bits, que é o "ransomware".
- `flag.enc`: a flag criptografada, com 32 bytes.

Rodando `strings` no executável, aparecem os nomes `flag` e `flag.enc`, além de funções como `srand`, `time` e `rand`. Isso já dá uma boa ideia do que ele faz: lê o arquivo `flag`, criptografa usando números aleatórios e salva o resultado em `flag.enc`.

### 2. Analisando o assembly
Analisando o assembly (pelo **Ghidra**, por exemplo), todo o programa está na função `main()`:

{% code title="main" overflow="wrap" lineNumbers="true" %}

```c
int main(void)
{
  FILE *f;
  long size;
  unsigned char *data;
  unsigned int seed;
  unsigned char xor_key, shift;

  f = fopen("flag", "rb");
  fseek(f, 0, SEEK_END);
  size = ftell(f);
  fseek(f, 0, SEEK_SET);
  data = malloc(size);
  fread(data, size, 1, f);
  fclose(f);

  seed = time(NULL);
  srand(seed);

  for (long i = 0; i < size; i++) {
    xor_key = rand();
    data[i] = data[i] ^ xor_key;
    shift = rand() & 7;
    data[i] = (data[i] << shift) | (data[i] >> (8 - shift));  // rotação para a esquerda
  }

  f = fopen("flag.enc", "wb");
  fwrite(&seed, 1, 4, f);
  fwrite(data, 1, size, f);
  fclose(f);
  return 0;
}
```

{% endcode %}

Para cada byte da flag, o programa:
1. Faz um XOR com o byte menos significativo de um `rand()`.
2. Rotaciona o resultado para a esquerda por `rand() & 7` bits (de 0 a 7).

{% hint style="info" %}

**Nota:** No assembly, a rotação aparece como uma única instrução `rol sil, cl`, e não como os dois *shifts* do pseudo-código.

{% endhint %}

### 3. Onde está a falha?
O `rand()` não gera números aleatórios de verdade. Ele é um gerador pseudoaleatório: a partir de uma mesma *seed*, sempre gera a mesma sequência de números. A *seed* aqui é o horário em que o programa rodou (`time(NULL)`), e o pior é que o programa **salva essa *seed* nos 4 primeiros bytes do `flag.enc`**.

```
5a 35 b1 62 | 00 f5 3e 12 c0 bd 8d 16 ...
   seed     |      flag criptografada
```

A *seed* `0x62b1355a` corresponde a 21/06/2022 às 03:04:58 (UTC), o momento em que a flag foi criptografada.

Com a *seed* em mãos, basta chamar `srand(seed)` e gerar os mesmos números que o programa gerou. Depois, para cada byte, desfazemos as operações na ordem inversa:
1. Rotacionar para a **direita** pela mesma quantidade de bits.
2. Fazer o XOR com a mesma chave (o XOR desfaz a si mesmo).

{% hint style="warning" %}

**Importante:** Os dois `rand()` de cada byte precisam ser chamados na mesma ordem do programa original (primeiro a chave do XOR, depois a rotação), mesmo que na hora de descriptografar a rotação seja desfeita primeiro. Caso contrário, a sequência fica dessincronizada.

{% endhint %}

### 4. Exploit
Para gerar exatamente os mesmos números, o script usa o `rand()` da própria `libc` pelo `ctypes`, em vez do módulo `random` do Python, que usa outro algoritmo. Por isso ele precisa ser executado no Linux, na mesma pasta do `flag.enc`.

{% code title="solve.py" overflow="wrap" lineNumbers="true" %}

```py
from ctypes import CDLL

libc = CDLL("libc.so.6")

data = open("flag.enc", "rb").read()

# os 4 primeiros bytes são a seed usada no srand()
seed = int.from_bytes(data[:4], "little")
libc.srand(seed)

flag = b""
for b in data[4:]:
    xor_key = libc.rand() & 0xff
    shift = libc.rand() & 7

    # desfaz a rotação para a esquerda e depois o XOR
    b = ((b >> shift) | (b << (8 - shift))) & 0xff
    flag += bytes([b ^ xor_key])

print(flag.decode())
```

{% endcode %}

```bash
$ python3 solve.py
HTB{vRy_s1MplE_F1LE3nCryp0r}
```

### Flag
`HTB{vRy_s1MplE_F1LE3nCryp0r}`

## Autor da WriteUp
[Membro de Exploitation - Matheus Inhan](https://github.com/Soon-pyt)
[solve.py](https://github.com/user-attachments/files/34250195/solve.py)
