# Flag Hunters

**Autor:** syreal \
**Plataforma:** CyLab (picoCTF) \
**Categoria:** Engenharia Reversa \
**Dificuldade:** Fácil\
**Data:** 2025

## Descrição do desafio

> Lyrics jump from verses to the refrain kind of like a subroutine call. There's a hidden refrain this program doesn't print by default. Can you get it to print it? There might be something in it for you.

## 1. Análise do arquivo fornecido

O desafio fornece um único arquivo, `lyric-reader.py`. A descrição já sugere que o programa trata a letra da música como código, com versos e refrões funcionando como chamadas de sub-rotina, e que existe um trecho oculto que nunca é impresso durante a execução normal.

Antes de interagir com a instância remota, decidi rodar o script localmente com uma `flag.txt` fake, apenas para observar seu comportamento. Logo no início, dois aspectos chamam atenção: a execução não segue uma ordem linear, certos trechos da letra se repetem em momentos específicos, e em determinado ponto, o programa solicita entrada do usuário através de um prompt interativo (`Crowd:`).

Lendo o código fonte, o script lê a flag de um arquivo local e a insere dentro de uma string chamada `secret_intro`:

```python
flag = open('flag.txt', 'r').read()
secret_intro = \
'''Pico warriors rising, puzzles laid bare,
Solving each challenge with precision and flair.
With unity and skill, flags we deliver,
The ether's ours to conquer, '''\
+ flag + '\n'
```

Essa `secret_intro` é concatenada com o restante da letra da música, formando a string completa `song_flag_hunters`. Isso já revela que a flag não está escondida nem ofuscada: o script lê o conteúdo bruto do arquivo e o insere diretamente em `secret_intro`, sem aplicar nenhuma transformação. Ou seja, a flag está em texto plano desde o momento em que é lida, apenas posicionada numa parte da string que o programa não alcança durante a execução normal.

O desafio real é fazer o programa imprimir esse trecho, já que a execução começa em outro ponto.

## 2. Identificando a vulnerabilidade

O loop principal controla tudo:

```python
line_count = 0
lip = start
while not finished and line_count < MAX_LINES:
    line_count += 1
    for line in song_lines[lip].split(';'):
        if line == '' and song_lines[lip] != '':
            continue
        if line == 'REFRAIN':
            song_lines[refrain_return] = 'RETURN ' + str(lip + 1)
            lip = refrain
        elif re.match(r"CROWD.*", line):
            crowd = input('Crowd: ')
            song_lines[lip] = 'Crowd: ' + crowd
            lip += 1
        elif re.match(r"RETURN [0-9]+", line):
            lip = int(line.split()[1])
        elif line == 'END':
            finished = True
        else:
            print(line, flush=True)
            time.sleep(0.5)
            lip += 1
```

A variável `lip` indica qual linha está sendo executada. A cada iteração, o programa pega a linha atual, separa por `;` e interpreta cada pedaço:

| Padrão | Comportamento |
|---|---|
| `REFRAIN` | Grava o ponto de retorno e desvia para o refrão |
| `CROWD.*` | Pede input do usuário e sobrescreve a própria linha com o texto digitado |
| `RETURN [0-9]+` | Desvia para o índice numérico indicado |
| `END` | Encerra a execução |
| Qualquer outro texto | Imprime na tela e avança para a próxima linha |

O ponto chave da vulnerabilidade está aqui:

```python
elif re.match(r"CROWD.*", line):
    crowd = input('Crowd: ')
    song_lines[lip] = 'Crowd: ' + crowd
    lip += 1
```

O input do usuário é gravado de volta no array de instruções, na mesma posição. Como o refrão é executado várias vezes ao longo da música, essa linha modificada será processada novamente na próxima passagem do fluxo por ali. Isso configura uma **auto-modificação de código controlada pelo usuário**. Além disso, o programa divide cada linha por `;` antes de interpretá-la, permitindo injetar múltiplos comandos em uma única resposta do `Crowd`.

## 3. Exploit final

O exploit consiste em responder ao primeiro prompt `Crowd:` com a string:

```
Flag;RETURN 0;
```

Essa resposta é gravada pelo programa na posição atual do `lip`, sobrescrevendo a linha que antes continha o comando `CROWD` original. Como essa posição faz parte do refrão, trecho que é revisitado sempre que a música chama `REFRAIN`, a linha modificada é reprocessada na segunda execução do refrão. Dessa vez, ela não é mais tratada como pedido de entrada, mas como uma nova instrução.

Ao ser dividida por `split(';')`, a linha vira dois pedaços:

- `"Crowd: Flag"` — é apenas impresso como texto comum, pois o padrão `CROWD.*` exige que "CROWD" esteja todo em maiúsculas, e a string gravada usa "Crowd" com apenas o "C" maiúsculo.
- `"RETURN 0"` — bate exatamente com o padrão de retorno reconhecido, fazendo o `lip` ser redirecionado para o índice 0.

É justamente nesse índice que começa a `secret_intro`, o trecho que contém a flag e que, até então, nunca havia sido alcançado pelo fluxo normal. A partir daí, o programa imprime esse conteúdo escondido, revelando a flag, antes de cair novamente em `[REFRAIN]` e entrar num loop interrompido apenas pelo limite de `MAX_LINES` ou manualmente.

O exploit funciona porque o programa confia que o input do usuário será apenas texto decorativo, sem validar se ele contém comandos que possam alterar o fluxo de execução. A ausência de sanitização no comando `CROWD` é a raiz da vulnerabilidade.

## Flag

```
picoCTF{70637h3r_f0r3v3r_b248b032}
```

---

**Autora da WriteUp:** [Membro de Exploitation - lieserl](https://github.com/lieserl-git)
