# The "barely" language (EASY tier) — one-page manual

A tiny, memory-safe, no-heap language. `dslc prog.dsl -o prog.ll` compiles it to
LLVM IR; the server links that with `runtime.o` and runs it. The only output is
`print`. 

## Values
Two kinds only:
- **int** — a signed 64-bit integer. Literals are decimal or hex (`0x4010000`)
- **array** — an opaque reference to a fixed-length block of i64 slots. 

## Grammar
```
program   := (fn | stmt)*
fn        := 'fn' id '(' params? ')' block
block     := '{' stmt* '}'
stmt      := 'let' id '=' expr ';'
           | id '=' expr ';'
           | id '[' expr ']' '=' expr ';'
           | 'if' '(' expr ')' block ('else' block)?
           | 'while' '(' expr ')' block
           | 'return' expr ';'
           | 'print' '(' expr ')' ';'
           | 'register' '(' id ')' ';'
           | expr ';'
expr      := add (('==' | '!=' | '<' | '<=' | '>' | '>=') add)*
add       := mul (('+' | '-') mul)*
mul       := unary (('*' | '/' | '%') unary)*
unary     := '-' unary | primary
primary   := int | id | id '(' args? ')' | id '[' expr ']'
           | 'array' '(' expr ')' | 'concat' '(' expr ',' expr ')'
           | 'len' '(' expr ')' | '(' expr ')'
```
`#` and `//` start line comments. Comparisons yield `1`/`0`. `/` and `%` by zero
abort. Functions return an i64; `register(f)` takes the name of a defined `fn`.

## Builtins
| form        | meaning                                                      |
|-------------|--------------------------------------------------------------|
| `array(n)`  | new array of `n` zeroed i64 slots                            |
| `a[i]`      | read slot `i` — **bounds-checked**                           |
| `a[i] = v`  | write slot `i` — **bounds-checked**                          |
| `len(a)`    | number of slots                                              |
| `concat(a,b)` | new array holding `a` then `b`                             |
| `register(f)` | store `fn f` in a runtime dispatch slot; called once at exit |
| `print(e)`  | print an i64 and a newline                                   |
