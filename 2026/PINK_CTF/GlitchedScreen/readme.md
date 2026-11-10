# WriteUp: Glitched Screen

## Descrição do Desafio

**Categoria:** reversing / esolang

**Pontos:** 50

**Autor do desafio:** admin5559

**Descrição:**

> Look at the artwork I made ... looks like a glitchy screen. Please don't solve this with AI #againstaislop

### Arquivos

| Arquivo | Descrição |
| --- | --- |
| screen.png | Imagem PNG de 359×58 pixels contendo o programa em linguagem esotérica. |

---

## Passo a Passo da Solução

### 1. Reconhecimento e Análise Inicial

Ao analisar o arquivo fornecido `screen.png` via `file` e inspecionar suas propriedades, observamos a seguinte resolução e formato:

```text
screen.png: PNG image data, 359 x 58, 8-bit colormap, non-interlaced

```

Ao verificar a paleta de cores da imagem, notamos que ela utiliza exclusivamente combinações dos valores hexadecimais `0x00`, `0xC0` e `0xFF` (ex: RGB `255,192,192`, `255,0,0`, `192,0,0`), além de preto puro (`0,0,0`) e branco puro (`255,255,255`).

Essa combinação corresponde exatamente à paleta padrão da linguagem esotérica **Piet** (6 matizes × 3 níveis de luminosidade + preto e branco).

A estrutura da imagem também revela a lógica de execução visual do Piet:

* Na linha superior (linha 0), há uma sequência contínua de pixels coloridos que formam o fluxo de instruções principal executado da esquerda para a direita.
* As "gotas" coloridas que descem verticalmente são blocos conectados (*codels*), cujo tamanho (número de pixels agrupados) define o valor numérico a ser empilhado pela instrução `push`.
* As linhas e áreas brancas atuam como "fios" por onde o ponteiro desliza sem executar comandos, permitindo desvios e laços.
* Os blocos pretos atuam como paredes e bloqueios de fluxo.

---

### 2. Análise da Linguagem Piet

No Piet, o programa é executado movendo um ponteiro (DP - Direction Pointer) e um seletor (CC - Codel Chooser) através dos blocos de cor. A instrução executada a cada transição de bloco é determinada pela variação de matiz ($\Delta\text{hue}$) e variação de luminosidade ($\Delta\text{lightness}$):

| $\Delta\text{hue}$ \ $\Delta\text{lightness}$ | 0 (Nenhuma) | 1 (Escuro) | 2 (Muito Escuro) |
| --- | --- | --- | --- |
| **0** | (none) | push | pop |
| **1** | add | sub | mul |
| **2** | div | mod | not |
| **3** | greater | pointer | switch |
| **4** | duplicate | roll | in(number) |
| **5** | in(char) | out(number) | out(char) |

O valor empilhado pelo comando `push` equivale exatamente à quantidade de *codels* (pixels) presentes no bloco que o programa acabou de deixar.

---

### 3. Execução e Identificação do Comportamento

Carregando o arquivo `screen.png` em uma ferramenta/interpretador de Piet (com tamanho de *codel* definido para 1 pixel) e executando sem nenhuma entrada do usuário, a aplicação retorna o seguinte resultado:

```text
Wrong PIN

```

Isso indica que o programa solicita um PIN via entrada padrão (`in(char)` / `in(number)`) e valida os dígitos inseridos.

Ao inspecionar as primeiras instruções executadas através da visualização passo a passo no interpretador, podemos mapear o início da rotina de verificação:

1. `in(char)` $\to$ Lê o primeiro caractere digitado.
2. `push 7`, `push 16`, `push 3` $\to$ Empilha os valores numéricos.
3. `mul` $\to$ Calcula $16 \times 3 = 48$.
4. `add` $\to$ Calcula $7 + 48 = 55$.
5. `sub` $\to$ Subtrai o valor ASCII do caractere lido por 55 ($Caractere - 55$).
6. `not` $\to$ Retorna `1` se a diferença for igual a `0` (isto é, se o caractere for igual ao código ASCII 55).
7. `pointer` $\to$ Altera a direção do fluxo com base no resultado da comparação.

O valor ASCII 55 corresponde ao caractere **`'7'`**. Se o primeiro dígito for `'7'`, o programa segue pelo caminho correto da verificação. Caso contrário, desvia para a rotina que monta a string `"Wrong PIN"` na pilha e a exibe na tela.

---

### 4. Automação e Recuperação do PIN (Side-Channel)

A validação do PIN ocorre de maneira sequencial (dígito a dígito). Cada dígito correto inserido faz o programa avançar mais blocos e executar mais instruções na grade antes de falhar ou solicitar o próximo caractere.

Podemos explorar esse comportamento criando um script em Python que executa o interpretador (`npiet`) passando o PIN parcial e contando a quantidade de passos executados para cada caractere testado:

```python
import subprocess
import string

cands = string.digits  # O PIN é composto por dígitos numéricos
pin = ""

print("[+] Iniciando força-bruta guiada por contagem de passos...")

for posicao in range(10):
    melhor_char = None
    max_passos = -1
    
    for ch in cands:
        test_pin = pin + ch
        # Executa o npiet via subprocess e captura a contagem de instruções/passos
        proc = subprocess.run(
            ['npiet', '-t', 'screen.png'],
            input=test_pin.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # A flag '-t' ou o output do npiet indica o número de passos/execuções
        passos = len(proc.stderr.splitlines())
        saida = proc.stdout.decode(errors='ignore')

        if passos > max_passos:
            max_passos = passos
            melhor_char = ch
            saida_final = saida

    pin += melhor_char
    print(f"Posição {posicao}: Dígito '{melhor_char}' -> {max_passos} passos")

    if "Wrong" not in saida_final and "PINK" in saida_final:
        break

print(f"\n[+] PIN Encontrado: {pin}")

```

#### Progressão de Passos Observada:

| Posição | Dígito | Passos Executados |
| --- | --- | --- |
| 0 | **7** | 414 |
| 1 | **3** | 490 |
| 2 | **9** | 574 |
| 3 | **1** | 666 |
| 4 | **8** | 766 |
| 5 | **4** | 874 |
| 6 | **2** | 988 |
| 7 | **0** | 1112 |
| 8 | **5** | 1244 |
| 9 | **6** | 1837 |

No 10º dígito, a contagem de passos atinge o fim do fluxo de verificação com sucesso e a mensagem de erro deixa de ser exibida.

---

### 5. Recuperando a Flag

Fornecendo o PIN completo `7391842056` para o programa via `npiet`:

```bash
$ echo 7391842056 | npiet screen.png
PINK{d0_y0u_l1k3_this_l4ngu4g3?}

```

### Flag

`PINK{d0_y0u_l1k3_this_l4ngu4g3?}`

---

**Autor da WriteUp:** [Membro de Exploitation - Jenni-Lopes](https://github.com/Jenni-Lopes)