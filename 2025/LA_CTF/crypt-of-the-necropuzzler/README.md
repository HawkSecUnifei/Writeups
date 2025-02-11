# WriteUp: crypt-of-the-necropuzzler
## Descrição do Desafio:
**Autor:** aplet123 \
**Categoria:** rev \
**Descrição:** 
> When no one's looking, the Necrodancer actually likes to play puzzle games in his free time. However, he got stuck on a really tough one and it's sucking all his enjoyment out of the game. If you can beat this one for him, he might not return your stolen heart, but he'll at least give you a flag.

### Arquivos
| Arquivo | Descrição |
| ------- | --------- |
| crypt-of-the-necropuzzler.py | código do desafio. |

> 📥 **Download:** [crypt-of-the-necropuzzler](https://github.com/HawkSecUnifei/Writeups/raw/refs/heads/main/2025/LA_CTF/crypt-of-the-necropuzzler/crypt-of-the-necropuzzler.py)

## Passo a Passo da Solução
### 1. Análise do arquivo fornecido
Olhando para o código do desafio, podemos notar a função `decrypt_flag(k)`, esta função descriptografa a **flag** usando o parâmetro `k`. Também é possível identificar a função `t(a,b,s=None)`, que basicamente realiza uma DFS buscando pares `(x,y)` que tenham o mesmo valor na lista `g` dos pares `(a,b)`.

Por fim, há um *loop* principal, esse *loop* é o responsável por imprimir o "tabuleiro", e por ler o carectere digitado pelo usuário, e com base nele realizar algumas operações. 
- "q": encerra a execução.
- "x": com base na posição `(a,b)` atual, altera o valor correspondente na lista `g`. Se era 1 vira 0, e se era 0 vira 1.
- "w", "s", "a", "d": se possível, anda a posição `(a,b)` com base no dicionário `m={'w':(-1,0),'s':(1,0),'a':(0,-1),'d':(0,1)}`.
- "c": verifica se todos os conjuntos encontrados pela função `t(a,b,s=None)` são válidos, se forem, a **flag** é revelada.

{% hint style="info" %}

**Nota:** Cada conjunto guarda todas as posições `(a,b)` de mesmo valor adjacentes. Dessa forma, se uma posição é marcada com 1, mas está cercada por posições com 0, seu conjunto é somente ela.

{% endhint %}

{% code title="crypt-of-the-necropuzzler.py" overflow="wrap" lineNumbers="true" %}

```py
#!/usr/local/bin/python3
import tty
import sys
import hashlib

if sys.stdin.isatty():
    tty.setcbreak(0)

g=(f:=[0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,1])[:]
n=[1,1,0,0,0,0,0,0,1,0,2,0,0,0,0,0,3,1,0,0,0,0,0,1,0,1,0,0,0,0,0,1,3,0,0,0,1,0,1,0,1,0,0,0,2,2,2,0,0]

def decrypt_flag(k):
    h=hashlib.sha512(str(k).encode()).digest()
    print(bytes(a^b for(a,b)in zip(h,bytes.fromhex("8b1e35ac3da64cb9db365e529ad8c9496388a4f499faf887386b4f6c43b616aae990f17c1b1f34af514800275673e0f3c689c0998fc73c342f033aa7cc69d199"))).decode())

m={'w':(-1,0),'s':(1,0),'a':(0,-1),'d':(0,1)}
def t(a,b,s=None):
    if s is None:
        s = set()
    s.add((a,b))
    for(i,j)in m.values():
        x,y=a+i,b+j
        if (x,y) not in s and x in range(7) and y in range(7) and g[x*7+y]==g[a*7+b]:
            t(x,y,s)
    return s

a,b=0,0
d=1
while 1:
    if d:
        print("\x1b[2J")
        for i in range(7):
            print(" ["[(a,b)==(i,0)],end="")
            for j in range(7):
                print("_#"[g[i*7+j]],end="["if(a,b)==(i,j+1)else" ]"[(a,b)==(i,j)])
            print()
        d=0
    try:
        c=sys.stdin.read(1)
        if c == "":
            break
    except EOFError:
        break
    if c=='q':
        break
    elif c=='x':
        if not f[i:=a*7+b]:
            g[i]=1-g[i]
            d=1
    elif v:=m.get(c):
        i,j=a+v[0],b+v[1]
        if i in range(7) and j in range(7):
            a,b=i,j
            d=1
    elif c=='c':
        p=1
        s=set()
        for i in range(7):
            for j in range(7):
                if(i,j)not in s:
                    v=[0]*4
                    k=t(i,j)
                    s|=k 
                    for(x,y)in k:
                        v[n[x*7+y]]+=1
                    if any(h not in (0,2) for h in v[1:]):
                        p=0
        if p:
            print("Correct!")
            decrypt_flag(g)
        else:
            print("Incorrect!")
```

{% endcode %}

Alguns pontos importantes são:
- Se o valor na lista `g` for 0, o *loop* imprime `_` na posição atual, e se for 1 é impresso `#`.
- A validação dos conjuntos é feita com base na lista `n`, que contém valores de 0 a 3, que representam os índices da lista `v`. Para a **flag** ser revelada, os valores da `v` devem ser 0 ou 2 para os índices 1, 2, e 3, o índice 0 pode conter qualquer valor. Dessa forma, o código percorre todos os conjuntos encontrados, e com base nas posições do conjunto, calcula uma posição na `n`, que representa a posição na `v` que terá o valor incrementado em 1.

### 2. Solução
Sabendo que devemos respeitar a regra dos valores na lista `v`, podemos montar uma tabela parecida com a impressa pelo *loop*, porém ao invés de ser `_` ou `#`, vai ser o índice na `v`. Isso é possível fazer apenas olhando para a lista `n`.

```
1 1 0 0 0 0 0
0 1 0 2 0 0 0
0 0 3 1 0 0 0
0 0 1 0 1 0 0
0 0 0 1 3 0 0
0 1 0 1 0 1 0
0 0 2 2 2 0 0
```

Também é possível modificar o próprio *script* para imprimir isso. Agora, o segredo é olhar para as posições já marcadas com 1, que não podem ser desmarcadas.

```
[_]_ _ _ _ _ _
 _ # _ _ _ _ _
 _ _ _ # _ _ _
 _ _ # _ # _ _
 _ _ _ # _ _ _
 _ _ _ _ _ _ _
 _ _ # _ # _ #
```

Perceba que já temos dois lugares marcados no índice 2, dessa forma precisamos colocar eles no mesmo conjunto para o valor na `v` ser 2. Porém, não podemos ligar eles pelo valor entre eles, porque esse valor também é 2, fazendo com que o valor na `v` seja 3. 

Outro ponto importante é o índice 3, os dois estão desmarcados, e se eles forem marcados e unidos, também será unido 4 pontos com valor 1, fazendo com que o valor na `v` seja 4. Assim, sabemos que os pontos com índice 3 devem ser desmarcados, e devem estar no mesmo conjunto.

Sabendo dessas duas dicas, o resto é ir montando o desenho, tentando não desrespeitar as regras de validação. Uma dica é colocar `print(v, i, j)` dentro do `if` que verifica a violação, pois dessa forma você saberá qual é o valor da `v` e em qual posição identificou.

```
 _ _ # # # # # 
 # # # _ _ _ # 
 # _ _ # # _ # 
 # _ # _ # _ # 
 # _[#]# _ _ # 
 # _ _ _ _ # # 
 # # # _ # # # 
```

### Flag
`lactf{i_may_or_may_not_have_blatantly_stolen_a_taiji_puzzle_lol}`

## Autor da WriteUp
[Membro de Exploitation - HenriUz](https://github.com/HenriUz)