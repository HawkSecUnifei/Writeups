# Hidden_Cipher_1

**Autor:**  Yahaya Meddy \
**Plataforma:** CyLab (picoCTF) \
**Categoria:** Engenharia Reversa \
**Dificuldade:** Médio\
**Data:** 2025

**Descrição do desafio:**
> The flag is right in front of you; just slightly encrypted. All you have to do is figure out the cipher and the key.



---

## 1. Análise do arquivo fornecido

O desafio entrega dois arquivos: o binário `hiddencipher` e um `flag.txt` de exemplo, que contém só `academy{fake_flag}`. A flag real não está nos arquivos. Rodando o `file` no binário:

```
$ file hiddencipher
hiddencipher: ELF 64-bit LSB shared object, x86-64, statically linked, no section header
```

O arquivo é um ELF de 64 bits, muito pequeno e sem section headers, o que sugere que está empacotado. O `strings` confirma:

```
$ strings hiddencipher | grep -i upx
$Info: This file is packed with the UPX executable packer http://upx.sf.net $
```

Ele está empacotado com UPX, então o primeiro passo é desempacotar:

```
$ upx -d hiddencipher -o unpacked
```

Com o binário limpo, o `strings` mostra o comportamento do programa:

```
flag.txt
Here your encrypted flag:
%02x
```

O programa lê o `flag.txt`, transforma cada byte e imprime o resultado em hexadecimal. Rodando com o `flag.txt` de exemplo:

```
$ ./unpacked
Here your encrypted flag:
3250221656192a48251358110c552f135409
```

São 18 bytes, o mesmo tamanho de `academy{fake_flag}`. A cifra, portanto, troca cada byte por outro, sem aumentar o tamanho.

No Ghidra, as funções relevantes são `main` e `get_secret`. O `main` lê o arquivo, chama `get_secret()` para obter a chave e aplica uma operação com ela em cada byte.

---

## 2. Identificando a cifra e a chave

O laço do `main` aplica um XOR em cada byte da flag usando `chave[i % 6]`, e o resultado é impresso em hexadecimal:

```c
key = get_secret();
for (i = 0; i < size; i++)
    printf("%02x", key[i % 6] ^ flag[i]);
```

O `% 6` mostra que a chave tem 6 bytes e se repete ao longo da flag. No assembly isso aparece como uma multiplicação por `0x2aaaaaab`, que é só o compilador otimizando a divisão.

A chave vem da função `get_secret`, que grava 6 bytes na memória:

```asm
mov BYTE PTR [rip+0x2d59], 0x53
mov BYTE PTR [rip+0x2d53], 0x33
mov BYTE PTR [rip+0x2d4d], 0x43
mov BYTE PTR [rip+0x2d47], 0x72
mov BYTE PTR [rip+0x2d41], 0x33
mov BYTE PTR [rip+0x2d3b], 0x74
mov BYTE PTR [rip+0x2d35], 0x0
```

Convertendo para ASCII:

| Hex | 0x53 | 0x33 | 0x43 | 0x72 | 0x33 | 0x74 |
|---|---|---|---|---|---|---|
| Caractere | S | 3 | C | r | 3 | t |

A chave é `S3Cr3t`, está fixa dentro do binário, e o XOR é reversível: `(a ^ k) ^ k = a`.

---

## 3. Exploit final

Ao executar o binário na instância do desafio, ele imprime a flag cifrada em hexadecimal:

```
Here your encrypted flag:
3250221656192a483b1d412b265d3313501f0c072d135f0d2002302d55473700224a04402e
```

Como o XOR é simétrico, a mesma operação que cifra também decifra. Basta aplicar a chave `S3Cr3t` a cada byte, o que o script `dec.py` faz:

```python
import sys

key = b"S3Cr3t"
data = bytes.fromhex(sys.argv[1])
print(bytes(b ^ key[i % len(key)] for i, b in enumerate(data)).decode())
```

Executando o script com o hex obtido:

```
$ python3 dec.py 3250221656192a483b1d412b265d3313501f0c072d135f0d2002302d55473700224a04402e
academy{xor_unpack_4nalys1s_f3d3a874}
```

---

## Flag

```
academy{xor_unpack_4nalys1s_f3d3a874}
```

---

**Autora da WriteUp:** [Membro de Exploitation - lieserl](https://github.com/lieserl-git)